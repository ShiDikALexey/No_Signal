import sys
from app import create_app
from extensions import db
from models import User, Chat, UserChatSettings

app = create_app()
with app.app_context():
    db.create_all()
    
    # Use "user" (quoted) for PostgreSQL compatibility
    table = '"user"' if 'postgresql' in str(db.engine.url) else 'user'
    
    # PostgreSQL uses TIMESTAMP WITH TIME ZONE, SQLite uses DATETIME
    datetime_type = 'TIMESTAMP WITH TIME ZONE' if 'postgresql' in str(db.engine.url) else 'DATETIME'
    
    tries = [
        ('is_read', f'ALTER TABLE message ADD COLUMN is_read BOOLEAN DEFAULT FALSE'),
        ('reset_token', f'ALTER TABLE {table} ADD COLUMN reset_token VARCHAR(100)'),
        ('reset_token_expires', f'ALTER TABLE {table} ADD COLUMN reset_token_expires {datetime_type}'),
        ('is_verified', f'ALTER TABLE {table} ADD COLUMN is_verified BOOLEAN DEFAULT TRUE'),
        ('verify_token', f'ALTER TABLE {table} ADD COLUMN verify_token VARCHAR(100)'),
        ('verify_token_expires', f'ALTER TABLE {table} ADD COLUMN verify_token_expires {datetime_type}'),
    ]
    
    for name, sql in tries:
        try:
            db.session.execute(db.text(sql))
            db.session.commit()
            print(f'OK: {name}')
        except Exception as e:
            db.session.rollback()
            print(f'SKIP: {name} — {e}')
    
    # Migrate chat settings
    try:
        chats = Chat.query.all()
        count = 0
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
                    count += 1
        db.session.commit()
        print(f'Migrated {count} chat settings to per-user')
    except Exception as e:
        db.session.rollback()
        print(f'chat_settings: {e}')
    
    print('Migration completed')
