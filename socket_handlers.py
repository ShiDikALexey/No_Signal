from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from models import User, Chat, Message
from extensions import db
from datetime import datetime
from crypto import encrypt, decrypt


def register_socket_handlers(socketio):

    @socketio.on('connect')
    def on_connect():
        if not current_user.is_authenticated:
            return False

        user = User.query.get(current_user.id)
        if user:
            user.last_seen = datetime.utcnow()
            db.session.commit()

        join_room(f'user_{current_user.id}')

        user_chats = Chat.query.filter(Chat.members.any(User.id == current_user.id)).all()
        for c in user_chats:
            join_room(f'chat_{c.id}')

        emit('user_online', {
            'user_id': current_user.id,
            'nickname': current_user.nickname
        }, broadcast=True)

    @socketio.on('disconnect')
    def on_disconnect():
        if current_user.is_authenticated:
            user = User.query.get(current_user.id)
            if user:
                user.last_seen = datetime.utcnow()
                db.session.commit()
            emit('user_offline', {
                'user_id': current_user.id,
                'nickname': current_user.nickname
            }, broadcast=True)

    @socketio.on('join_chat')
    def on_join_chat(data):
        if not current_user.is_authenticated:
            return
        chat_id = data.get('chat_id')
        if not chat_id:
            return
        chat = Chat.query.get(chat_id)
        if not chat or current_user not in chat.members:
            return
        join_room(f'chat_{chat_id}')

    @socketio.on('send_message')
    def on_send_message(data):
        if not current_user.is_authenticated:
            return

        chat_id = data.get('chat_id')
        text = data.get('text', '').strip()
        file_url = data.get('file_url', '').strip() if data.get('file_url') else None
        file_name = data.get('file_name', '').strip() if data.get('file_name') else None
        file_type = data.get('file_type', '').strip() if data.get('file_type') else None
        file_size = data.get('file_size')

        if (not text and not file_url) or not chat_id:
            return

        chat = Chat.query.get(chat_id)
        if not chat or current_user not in chat.members:
            return

        message = Message(
            chat_id=chat_id,
            sender_id=current_user.id,
            text=encrypt(text),
            timestamp=datetime.utcnow(),
            file_url=file_url,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size
        )
        db.session.add(message)
        db.session.commit()

        msg_data = message.to_dict()
        msg_data['text'] = text
        emit('new_message', msg_data, room=f'chat_{chat_id}')

        for member in chat.members:
            chat_data = chat.to_dict(member.id)
            emit('chat_updated', chat_data, room=f'user_{member.id}')

    @socketio.on('typing')
    def on_typing(data):
        if not current_user.is_authenticated:
            return
        chat_id = data.get('chat_id')
        if not chat_id:
            return
        emit('user_typing', {
            'chat_id': chat_id,
            'user_id': current_user.id,
            'nickname': current_user.nickname
        }, room=f'chat_{chat_id}', include_self=False)

    @socketio.on('stop_typing')
    def on_stop_typing(data):
        if not current_user.is_authenticated:
            return
        chat_id = data.get('chat_id')
        if not chat_id:
            return
        emit('user_stopped_typing', {
            'chat_id': chat_id,
            'user_id': current_user.id
        }, room=f'chat_{chat_id}', include_self=False)