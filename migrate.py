import sys
from app import create_app
from extensions import db
from models import User, Chat, UserChatSettings

app = create_app()
with app.app_context():
    db.create_all()
    
    try:
        db.session.execute(db.text('ALTER TABLE message ADD COLUMN is_read BOOLEAN DEFAULT FALSE'))
        db.session.commit()
        print('Added is_read column')
    except Exception as e:
        print('is_read:', str(e))
    
    try:
        db.session.execute(db.text('ALTER TABLE user ADD COLUMN reset_token VARCHAR(100)'))
        db.session.execute(db.text('ALTER TABLE user ADD COLUMN reset_token_expires DATETIME'))
        db.session.commit()
        print('Added reset_token columns')
    except Exception as e:
        print('reset_token:', str(e))
    
    try:
        db.session.execute(db.text('ALTER TABLE user ADD COLUMN is_verified BOOLEAN DEFAULT TRUE'))
        db.session.execute(db.text('ALTER TABLE user ADD COLUMN verify_token VARCHAR(100)'))
        db.session.execute(db.text('ALTER TABLE user ADD COLUMN verify_token_expires DATETIME'))
        db.session.commit()
        print('Added email verification columns')
    except Exception as e:
        print('verify columns:', str(e))
    
    try:
        chats = Chat.query.all()
        for chat in chats:
            for member in chat.members:
                existing = UserChatSettings.query.filter_by(user_id=member.id, chat_id=chat.id).first()
                if not existing:
                    settings = UserChatSettings(
                        user_id=member.id,
                        chat_id=chat.id,
                        is_pinned=getattr(chat, 'is_pinned', False) if hasattr(chat, 'is_pinned') else False,
                        is_archived=getattr(chat, 'is_archived', False) if hasattr(chat, 'is_archived') else False,
                        is_muted=getattr(chat, 'is_muted', False) if hasattr(chat, 'is_muted') else False
                    )
                    db.session.add(settings)
        db.session.commit()
        print('Migrated chat settings to per-user')
    except Exception as e:
        print('chat_settings migration:', str(e))
        db.session.rollback()
    
    print('Migration completed')
