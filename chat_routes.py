from flask import Blueprint, render_template, jsonify, request, send_from_directory, current_app
from flask_login import login_required, current_user
from models import User, Chat, Message, chat_members, UserChatSettings
from extensions import db, socketio
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from crypto import decrypt
import os
import uuid

chat = Blueprint('chat', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'mp4', 'webm', 'mov', 'avi', 'mkv', 'mp3', 'wav', 'ogg', 'flac', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'rtf', 'zip', 'rar', '7z', 'tar', 'gz', 'json', 'xml', 'csv'}

ALLOWED_MIMES = {
    'image/png', 'image/jpeg', 'image/gif', 'image/webp', 'image/bmp',
    'video/mp4', 'video/webm', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska',
    'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/flac', 'audio/webm',
    'application/pdf',
    'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain', 'application/rtf',
    'application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed',
    'application/x-tar', 'application/gzip',
    'application/json', 'application/xml', 'text/csv',
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_type(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    image_exts = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}
    video_exts = {'mp4', 'webm', 'mov', 'avi', 'mkv'}
    audio_exts = {'mp3', 'wav', 'ogg', 'flac'}
    doc_exts = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'rtf', 'csv', 'json', 'xml'}
    archive_exts = {'zip', 'rar', '7z', 'tar', 'gz'}
    if ext in image_exts:
        return 'image'
    elif ext in video_exts:
        return 'video'
    elif ext in audio_exts:
        return 'audio'
    elif ext in doc_exts:
        return 'document'
    elif ext in archive_exts:
        return 'archive'
    return 'other'


@chat.route('/')
@login_required
def index():
    return render_template('chat.html')


@chat.route('/api/users')
@login_required
def search_users():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    users = User.query.filter(
        User.nickname.ilike(f'%{query}%'),
        User.id != current_user.id
    ).limit(30).all()
    return jsonify([u.to_dict() for u in users])


@chat.route('/api/chats')
@login_required
def get_chats():
    user_chats = Chat.query.filter(
        Chat.members.any(User.id == current_user.id)
    ).all()

    chats_with_messages = []
    for c in user_chats:
        last_msg = Message.query.filter_by(chat_id=c.id).order_by(Message.timestamp.desc()).first()
        if last_msg:
            chats_with_messages.append((c, last_msg.timestamp))
        else:
            chats_with_messages.append((c, c.created_at))

    chats_with_messages.sort(key=lambda x: x[1], reverse=True)
    
    pinned = []
    unpinned = []
    for c, _ in chats_with_messages:
        settings = c.get_user_settings(current_user.id)
        if settings.is_pinned and not settings.is_archived:
            pinned.append(c)
        else:
            unpinned.append(c)
    
    sorted_chats = pinned + unpinned
    result = [c.to_dict(current_user.id) for c in sorted_chats]
    return jsonify(result)


@chat.route('/api/chats/private/<int:user_id>', methods=['POST'])
@login_required
def create_private_chat(user_id):
    if user_id == current_user.id:
        return jsonify({'error': 'Нельзя создать чат с собой'}), 400

    other_user = User.query.get_or_404(user_id)

    existing = Chat.query.filter(
        Chat.is_group == False,
        Chat.members.any(User.id == current_user.id),
        Chat.members.any(User.id == user_id)
    ).first()

    if existing:
        return jsonify(existing.to_dict(current_user.id))

    new_chat = Chat(is_group=False)
    db.session.add(new_chat)
    db.session.flush()
    new_chat.members.append(current_user)
    new_chat.members.append(other_user)
    db.session.commit()

    chat_data = new_chat.to_dict(current_user.id)
    for member in new_chat.members:
        socketio.emit('new_chat', chat_data, room=f'user_{member.id}')

    return jsonify(chat_data)


@chat.route('/api/chats/group', methods=['POST'])
@login_required
def create_group_chat():
    data = request.json or {}
    name = data.get('name', '').strip() or 'Групповой чат'
    member_ids = data.get('members', [])

    new_chat = Chat(is_group=True, name=name)
    db.session.add(new_chat)
    db.session.flush()
    new_chat.members.append(current_user)
    for mid in member_ids:
        user = User.query.get(mid)
        if user and user not in new_chat.members:
            new_chat.members.append(user)
    db.session.commit()

    chat_data = new_chat.to_dict(current_user.id)
    for member in new_chat.members:
        socketio.emit('new_chat', chat_data, room=f'user_{member.id}')

    return jsonify(chat_data)


@chat.route('/api/chats/<int:chat_id>/messages')
@login_required
def get_messages(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if current_user not in chat.members:
        return jsonify({'error': 'Нет доступа'}), 403

    before_id = request.args.get('before', type=int)
    limit = request.args.get('limit', 50, type=int)
    limit = min(limit, 100)

    query = Message.query.filter_by(chat_id=chat_id)
    
    if before_id:
        query = query.filter(Message.id < before_id)
    
    messages = query.order_by(Message.timestamp.desc()).limit(limit).all()
    messages.reverse()

    result = []
    for m in messages:
        msg_dict = m.to_dict()
        msg_dict['text'] = decrypt(m.text)
        result.append(msg_dict)

    has_more = len(messages) == limit
    
    return jsonify({
        'messages': result,
        'has_more': has_more,
        'oldest_id': messages[0].id if messages else None
    })


@chat.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Недопустимый тип файла'}), 400

    if file.content_type and file.content_type not in ALLOWED_MIMES:
        return jsonify({'error': 'Недопустимый формат файла'}), 400

    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)

    original_name = secure_filename(file.filename) or 'file'
    unique_name = uuid.uuid4().hex + '_' + original_name
    file_path = os.path.join(upload_folder, unique_name)
    file.save(file_path)

    file_size = os.path.getsize(file_path)
    file_type = get_file_type(original_name)
    file_url = '/uploads/' + unique_name

    return jsonify({
        'file_url': file_url,
        'file_name': original_name,
        'file_type': file_type,
        'file_size': file_size
    })


@chat.route('/uploads/<path:filename>')
@login_required
def serve_upload(filename):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'Файл не найден'}), 404
    
    user_chats = Chat.query.filter(Chat.members.any(User.id == current_user.id)).all()
    user_chat_ids = [c.id for c in user_chats]
    
    message = Message.query.filter(
        Message.chat_id.in_(user_chat_ids),
        Message.file_url == '/uploads/' + filename
    ).first()
    
    if not message:
        avatar_user = User.query.filter_by(avatar_photo='/uploads/' + filename).first()
        if not avatar_user or avatar_user.id != current_user.id:
            return jsonify({'error': 'Нет доступа к файлу'}), 403
    
    return send_from_directory(upload_folder, filename)


@chat.route('/api/chats/<int:chat_id>/pin', methods=['POST'])
@login_required
def toggle_pin_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if current_user not in chat.members:
        return jsonify({'error': 'Нет доступа'}), 403
    
    settings = chat.get_user_settings(current_user.id)
    settings.is_pinned = not settings.is_pinned
    db.session.commit()
    return jsonify({'is_pinned': settings.is_pinned})


@chat.route('/api/chats/<int:chat_id>/archive', methods=['POST'])
@login_required
def toggle_archive_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if current_user not in chat.members:
        return jsonify({'error': 'Нет доступа'}), 403
    
    settings = chat.get_user_settings(current_user.id)
    settings.is_archived = not settings.is_archived
    if settings.is_archived:
        settings.is_pinned = False
    db.session.commit()
    return jsonify({'is_archived': settings.is_archived, 'is_pinned': settings.is_pinned})


@chat.route('/api/chats/<int:chat_id>/mute', methods=['POST'])
@login_required
def toggle_mute_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if current_user not in chat.members:
        return jsonify({'error': 'Нет доступа'}), 403
    
    settings = chat.get_user_settings(current_user.id)
    settings.is_muted = not settings.is_muted
    db.session.commit()
    return jsonify({'is_muted': settings.is_muted})


@chat.route('/api/chats/<int:chat_id>/clear', methods=['POST'])
@login_required
def clear_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if current_user not in chat.members:
        return jsonify({'error': 'Нет доступа'}), 403
    Message.query.filter_by(chat_id=chat_id).delete()
    db.session.commit()
    return jsonify({'success': True})


@chat.route('/api/chats/<int:chat_id>', methods=['DELETE'])
@login_required
def delete_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if current_user not in chat.members:
        return jsonify({'error': 'Нет доступа'}), 403
    Message.query.filter_by(chat_id=chat_id).delete()
    chat.members.remove(current_user)
    if len(chat.members) == 0:
        UserChatSettings.query.filter_by(chat_id=chat_id).delete()
        db.session.delete(chat)
    db.session.commit()
    return jsonify({'success': True})