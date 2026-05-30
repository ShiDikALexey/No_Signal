from extensions import db
from flask_login import UserMixin
from datetime import datetime, timezone
import random

AVATAR_COLORS = [
    '#e94560', '#3a96f9', '#2ecc71', '#e67e22', '#9b59b6',
    '#1abc9c', '#f39c12', '#e74c3c', '#3498db', '#16a085',
    '#d35400', '#8e44ad', '#27ae60', '#2980b9', '#c0392b'
]


def _decrypt_text(text):
    try:
        from crypto import decrypt
        return decrypt(text)
    except Exception:
        return text

chat_members = db.Table(
    'chat_member',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('chat_id', db.Integer, db.ForeignKey('chat.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nickname = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    avatar_color = db.Column(db.String(7), nullable=False)
    avatar_photo = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(100), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        last_seen = self.last_seen
        if last_seen and last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=timezone.utc)
        is_online = last_seen and (datetime.now(timezone.utc) - last_seen).total_seconds() < 180
        return {
            'id': self.id,
            'nickname': self.nickname,
            'avatar_color': self.avatar_color,
            'avatar_photo': self.avatar_photo,
            'status': self.status,
            'is_online': is_online,
            'is_admin': self.is_admin
        }


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    is_group = db.Column(db.Boolean, default=False, nullable=False)
    is_pinned = db.Column(db.Boolean, default=False, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    is_muted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    members = db.relationship('User', secondary=chat_members, backref='chats')
    messages = db.relationship('Message', backref='chat_msg', order_by='Message.timestamp')

    def to_dict(self, current_user_id):
        if self.is_group:
            name = self.name or 'Групповой чат'
            avatar_color = '#3a96f9'
            avatar_photo = None
        else:
            other = None
            for m in self.members:
                if m.id != current_user_id:
                    other = m
                    break
            name = other.nickname if other else 'Неизвестный'
            avatar_color = other.avatar_color if other else '#888'
            avatar_photo = other.avatar_photo if other else None

        last_msg = None
        if self.messages:
            m = self.messages[-1]
            decrypted_text = _decrypt_text(m.text)
            prefix = 'Вы' if m.sender_id == current_user_id else m.sender.nickname
            last_msg = {
                'sender_nickname': m.sender.nickname,
                'prefix': prefix,
                'text': decrypted_text[:50] + ('...' if len(decrypted_text) > 50 else ''),
                'timestamp': m.timestamp.strftime('%H:%M')
            }

        return {
            'id': self.id,
            'name': name,
            'is_group': self.is_group,
            'avatar_color': avatar_color,
            'avatar_photo': avatar_photo,
            'members_count': len(self.members),
            'last_message': last_msg,
            'is_pinned': self.is_pinned,
            'is_archived': self.is_archived,
            'is_muted': self.is_muted
        }


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False, default='')
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    file_type = db.Column(db.String(20), nullable=True)
    file_url = db.Column(db.String(500), nullable=True)
    file_name = db.Column(db.String(255), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False)

    sender = db.relationship('User', backref='user_messages')

    def to_dict(self):
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'sender_id': self.sender_id,
            'sender_nickname': self.sender.nickname,
            'sender_avatar_color': self.sender.avatar_color,
            'text': self.text,
            'timestamp': self.timestamp.strftime('%H:%M'),
            'full_timestamp': self.timestamp.isoformat(),
            'file_type': self.file_type,
            'file_url': self.file_url,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'is_read': self.is_read
        }


class SystemAnnouncement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%H:%M %d.%m.%Y')
        }