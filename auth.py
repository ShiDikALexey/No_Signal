from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import User, AVATAR_COLORS, Chat, Message, SystemAnnouncement
from extensions import db, limiter
from config import BASE_DIR
from mail import send_password_reset_email, send_verification_email
import random
import os
import uuid
import secrets
from datetime import datetime, timezone, timedelta

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chat.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            if not user.is_verified:
                flash('Подтвердите ваш email. Проверьте почту.', 'error')
                return render_template('login.html')
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('chat.index'))
        else:
            flash('Неверный email или пароль', 'error')

    return render_template('login.html')


@auth.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('chat.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        nickname = request.form.get('nickname', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        errors = []
        if not email or not nickname or not password:
            errors.append('Заполните все поля')
        if len(nickname) < 2:
            errors.append('Никнейм должен быть не менее 2 символов')
        if len(password) < 6:
            errors.append('Пароль должен быть не менее 6 символов')
        if password != confirm_password:
            errors.append('Пароли не совпадают')
        if User.query.filter_by(email=email).first():
            errors.append('Этот email уже зарегистрирован')
        if User.query.filter_by(nickname=nickname).first():
            errors.append('Этот никнейм уже занят')

        if errors:
            for e in errors:
                flash(e, 'error')
        else:
            token = secrets.token_urlsafe(32)
            user = User(
                email=email,
                nickname=nickname,
                password_hash=generate_password_hash(password),
                avatar_color=random.choice(AVATAR_COLORS),
                is_verified=False,
                verify_token=token,
                verify_token_expires=datetime.now(timezone.utc) + timedelta(hours=24)
            )
            db.session.add(user)
            db.session.commit()
            
            verify_url = url_for('auth.verify_email', token=token, _external=True)
            
            if send_verification_email(email, verify_url, nickname):
                flash('Письмо с подтверждением отправлено на ваш email', 'success')
            else:
                flash('Аккаунт создан, но письмо не удалось отправить. Обратитесь к администратору.', 'error')
            
            return redirect(url_for('auth.login'))

    return render_template('register.html', email=request.form.get('email', ''), nickname=request.form.get('nickname', ''))


@auth.route('/reset-password', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('chat.index'))

    token = request.args.get('token', '')
    email = request.args.get('email', '').strip().lower()
    
    success = False
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        token = request.form.get('token', '')

        if not email:
            flash('Введите email', 'error')
        elif len(new_password) < 6:
            flash('Пароль должен быть не менее 6 символов', 'error')
        elif new_password != confirm_password:
            flash('Пароли не совпадают', 'error')
        elif not token:
            flash('Требуется подтверждение через email', 'error')
        else:
            user = User.query.filter_by(email=email).first()
            if user and user.reset_token == token:
                if user.reset_token_expires and user.reset_token_expires.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
                    user.password_hash = generate_password_hash(new_password)
                    user.reset_token = None
                    user.reset_token_expires = None
                    db.session.commit()
                    success = True
                    flash('Пароль успешно изменён', 'success')
                else:
                    flash('Ссылка для сброса пароля истекла', 'error')
            else:
                flash('Неверный или отсутствующий токен', 'error')

    return render_template('reset_password.html', success=success, token=token, email=email)


@auth.route('/verify/<token>')
def verify_email(token):
    user = User.query.filter_by(verify_token=token).first()
    
    if not user:
        flash('Неверная или истёкшая ссылка подтверждения', 'error')
        return redirect(url_for('auth.login'))
    
    if user.verify_token_expires and user.verify_token_expires.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        flash('Ссылка подтверждения истекла. Зарегистрируйтесь заново.', 'error')
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('auth.register'))
    
    user.is_verified = True
    user.verify_token = None
    user.verify_token_expires = None
    db.session.commit()
    
    flash('Email подтверждён! Теперь вы можете войти.', 'success')
    return redirect(url_for('auth.login'))


@auth.route('/resend-verification', methods=['POST'])
@limiter.limit("3 per hour")
def resend_verification():
    email = request.form.get('email', '').strip().lower()
    
    if not email:
        flash('Введите email', 'error')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=email, is_verified=False).first()
    
    if user:
        token = secrets.token_urlsafe(32)
        user.verify_token = token
        user.verify_token_expires = datetime.now(timezone.utc) + timedelta(hours=24)
        db.session.commit()
        
        verify_url = url_for('auth.verify_email', token=token, _external=True)
        
        if send_verification_email(email, verify_url, user.nickname):
            flash('Письмо с подтверждением отправлено повторно', 'success')
        else:
            flash('Ошибка отправки. Попробуйте позже.', 'error')
    else:
        flash('Если аккаунт существует и не подтверждён, письмо будет отправлено', 'info')
    
    return redirect(url_for('auth.login'))


@auth.route('/request-reset', methods=['POST'])
@limiter.limit("3 per hour")
def request_password_reset():
    email = request.form.get('email', '').strip().lower()
    
    if not email:
        flash('Введите email', 'error')
        return redirect(url_for('auth.reset_password'))
    
    user = User.query.filter_by(email=email).first()
    if user:
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db.session.commit()
        
        reset_url = url_for('auth.reset_password', token=token, email=email, _external=True)
        
        if send_password_reset_email(email, reset_url):
            flash('Ссылка для сброса пароля отправлена на ваш email', 'success')
        else:
            flash('Ошибка отправки письма. Попробуйте позже или обратитесь к администратору.', 'error')
    else:
        flash('Если пользователь с таким email существует, ссылка для сброса отправлена', 'info')
    
    return redirect(url_for('auth.reset_password'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/api/profile')
@login_required
def get_profile():
    return jsonify({
        'id': current_user.id,
        'email': current_user.email,
        'nickname': current_user.nickname,
        'avatar_color': current_user.avatar_color,
        'avatar_photo': current_user.avatar_photo,
        'status': current_user.status,
        'avatar_colors': AVATAR_COLORS
    })


@auth.route('/api/profile/nickname', methods=['POST'])
@login_required
def change_nickname():
    data = request.json or {}
    nickname = data.get('nickname', '').strip()

    if len(nickname) < 2:
        return jsonify({'error': 'Никнейм должен быть не менее 2 символов'}), 400

    if User.query.filter(User.nickname == nickname, User.id != current_user.id).first():
        return jsonify({'error': 'Этот никнейм уже занят'}), 400

    current_user.nickname = nickname
    db.session.commit()
    return jsonify({'nickname': nickname})


@auth.route('/api/profile/password', methods=['POST'])
@login_required
def change_password():
    data = request.json or {}
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')

    if not check_password_hash(current_user.password_hash, old_password):
        return jsonify({'error': 'Неверный текущий пароль'}), 400

    if len(new_password) < 6:
        return jsonify({'error': 'Пароль должен быть не менее 6 символов'}), 400

    if new_password != confirm_password:
        return jsonify({'error': 'Пароли не совпадают'}), 400

    current_user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({'success': True})


@auth.route('/api/profile/avatar-color', methods=['POST'])
@login_required
def change_avatar_color():
    data = request.json or {}
    color = data.get('color', '')

    if color not in AVATAR_COLORS:
        return jsonify({'error': 'Недопустимый цвет'}), 400

    current_user.avatar_color = color
    db.session.commit()
    return jsonify({'avatar_color': color})


@auth.route('/api/profile/status', methods=['POST'])
@login_required
def change_status():
    data = request.json or {}
    status = data.get('status', '').strip()

    if len(status) > 100:
        return jsonify({'error': 'Статус слишком длинный'}), 400

    current_user.status = status if status else None
    db.session.commit()
    return jsonify({'status': current_user.status})


@auth.route('/api/profile/delete', methods=['POST'])
@login_required
def delete_account():
    data = request.json or {}
    password = data.get('password', '')

    if not check_password_hash(current_user.password_hash, password):
        return jsonify({'error': 'Неверный пароль'}), 400

    user_id = current_user.id

    user_chats = Chat.query.filter(Chat.members.any(User.id == user_id)).all()
    for chat in user_chats:
        Message.query.filter_by(chat_id=chat.id).delete()
        chat.members.remove(current_user)
        if len(chat.members) == 0:
            db.session.delete(chat)

    db.session.delete(current_user)
    db.session.commit()
    logout_user()
    return jsonify({'success': True})


@auth.route('/api/profile/avatar-photo', methods=['POST'])
@login_required
def upload_avatar_photo():
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400

    allowed = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed:
        return jsonify({'error': 'Допустимы только изображения (png, jpg, gif, webp)'}), 400

    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)

    original_name = secure_filename(file.filename) or 'avatar'
    unique_name = 'avatar_' + str(uuid.uuid4())[:8] + '_' + original_name
    file_path = os.path.join(upload_folder, unique_name)
    file.save(file_path)

    if current_user.avatar_photo:
        old_path = os.path.join(BASE_DIR, current_user.avatar_photo.lstrip('/'))
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass

    current_user.avatar_photo = '/uploads/' + unique_name
    db.session.commit()
    return jsonify({'avatar_photo': current_user.avatar_photo})


@auth.route('/api/profile/avatar-photo', methods=['DELETE'])
@login_required
def delete_avatar_photo():
    if current_user.avatar_photo:
        old_path = os.path.join(BASE_DIR, current_user.avatar_photo.lstrip('/'))
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass
    current_user.avatar_photo = None
    db.session.commit()
    return jsonify({'avatar_photo': None})


def admin_required(f):
    from functools import wraps
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'error': 'Доступ запрещён'}), 403
        return f(*args, **kwargs)
    return decorated


@auth.route('/api/announcement')
@login_required
def get_announcement():
    announcement = SystemAnnouncement.query.filter_by(is_active=True).order_by(SystemAnnouncement.id.desc()).first()
    return jsonify(announcement.to_dict() if announcement else None)


@auth.route('/api/announcement', methods=['POST'])
@admin_required
def set_announcement():
    data = request.json or {}
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'Текст обязателен'}), 400
    SystemAnnouncement.query.filter_by(is_active=True).update({'is_active': False})
    announcement = SystemAnnouncement(text=text, is_active=True)
    db.session.add(announcement)
    db.session.commit()
    return jsonify(announcement.to_dict())


@auth.route('/api/announcement', methods=['DELETE'])
@admin_required
def delete_announcement():
    SystemAnnouncement.query.filter_by(is_active=True).update({'is_active': False})
    db.session.commit()
    return jsonify({'success': True})


@auth.route('/api/admin/users')
@admin_required
def admin_users():
    users = User.query.order_by(User.id.desc()).all()
    return jsonify([{
        'id': u.id,
        'email': u.email,
        'nickname': u.nickname,
        'is_admin': u.is_admin,
        'last_seen': u.last_seen.strftime('%d.%m.%Y %H:%M'),
        'avatar_color': u.avatar_color
    } for u in users])


@auth.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    if user_id == current_user.id:
        return jsonify({'error': 'Нельзя удалить самого себя'}), 400
    user = User.query.get_or_404(user_id)
    user_chats = Chat.query.filter(Chat.members.any(User.id == user_id)).all()
    for chat in user_chats:
        Message.query.filter_by(chat_id=chat.id).delete()
        chat.members.remove(user)
        if len(chat.members) == 0:
            db.session.delete(chat)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})