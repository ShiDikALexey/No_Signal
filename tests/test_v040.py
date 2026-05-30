import pytest
from app import create_app
from extensions import db
from models import User, Chat, Message, UserChatSettings
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(app, client):
    with app.app_context():
        user = User(
            email='test@example.com',
            nickname='testuser',
            password_hash=generate_password_hash('password123'),
            avatar_color='#e94560',
            is_verified=True
        )
        db.session.add(user)
        db.session.commit()
        
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        return client, user


class TestUserChatSettings:
    def test_create_user_chat_settings(self, app):
        with app.app_context():
            user = User(
                email='test@example.com',
                nickname='testuser',
                password_hash=generate_password_hash('password123'),
                avatar_color='#e94560'
            )
            db.session.add(user)
            
            chat = Chat(is_group=False)
            db.session.add(chat)
            db.session.flush()
            
            chat.members.append(user)
            db.session.commit()
            
            settings = chat.get_user_settings(user.id)
            
            assert settings is not None
            assert settings.user_id == user.id
            assert settings.chat_id == chat.id
            assert settings.is_pinned == False
            assert settings.is_archived == False
            assert settings.is_muted == False
    
    def test_toggle_chat_settings(self, app):
        with app.app_context():
            user = User(
                email='test@example.com',
                nickname='testuser',
                password_hash=generate_password_hash('password123'),
                avatar_color='#e94560'
            )
            db.session.add(user)
            
            chat = Chat(is_group=False)
            db.session.add(chat)
            db.session.flush()
            
            chat.members.append(user)
            db.session.commit()
            
            settings = chat.get_user_settings(user.id)
            settings.is_pinned = True
            db.session.commit()
            
            settings = chat.get_user_settings(user.id)
            assert settings.is_pinned == True


class TestMessagePagination:
    def test_get_messages_with_pagination(self, auth_client):
        client, user = auth_client
        
        with client.application.app_context():
            chat = Chat(is_group=False)
            db.session.add(chat)
            db.session.flush()
            chat.members.append(user)
            db.session.commit()
            
            for i in range(100):
                msg = Message(
                    chat_id=chat.id,
                    sender_id=user.id,
                    text=f'Message {i}',
                    timestamp=datetime.now(timezone.utc)
                )
                db.session.add(msg)
            db.session.commit()
            
            response = client.get(f'/api/chats/{chat.id}/messages?limit=50')
            assert response.status_code == 200
            
            data = response.get_json()
            assert 'messages' in data
            assert 'has_more' in data
            assert len(data['messages']) == 50
            assert data['has_more'] == True
            
            response = client.get(f'/api/chats/{chat.id}/messages?limit=50&before={data["oldest_id"]}')
            assert response.status_code == 200
            
            data = response.get_json()
            assert len(data['messages']) == 50


class TestPasswordReset:
    def test_request_password_reset(self, app, client):
        with app.app_context():
            user = User(
                email='test@example.com',
                nickname='testuser',
                password_hash=generate_password_hash('password123'),
                avatar_color='#e94560'
            )
            db.session.add(user)
            db.session.commit()
            
            response = client.post('/auth/request-reset', data={
                'email': 'test@example.com'
            })
            
            assert response.status_code == 302
            
            user = User.query.filter_by(email='test@example.com').first()
            assert user.reset_token is not None
            assert user.reset_token_expires is not None


class TestEmailVerification:
    def test_register_creates_unverified_user(self, app, client):
        with app.app_context():
            response = client.post('/auth/register', data={
                'email': 'new@example.com',
                'nickname': 'NewUser',
                'password': 'password123',
                'confirm_password': 'password123'
            }, follow_redirects=True)
            assert response.status_code == 200
            
            user = User.query.filter_by(email='new@example.com').first()
            assert user is not None
            assert user.is_verified == False
            assert user.verify_token is not None
    
    def test_unverified_user_cannot_login(self, app, client):
        with app.app_context():
            user = User(
                email='unverified@example.com',
                nickname='Unverified',
                password_hash=generate_password_hash('password123'),
                avatar_color='#e94560',
                is_verified=False
            )
            db.session.add(user)
            db.session.commit()
            
            response = client.post('/auth/login', data={
                'email': 'unverified@example.com',
                'password': 'password123'
            }, follow_redirects=True)
            
            assert b'login' in response.data.lower() or b'auth' in response.data.lower()
    
    def test_verify_email_success(self, app, client):
        with app.app_context():
            import secrets
            from datetime import datetime, timezone, timedelta
            token = secrets.token_urlsafe(32)
            user = User(
                email='verify@example.com',
                nickname='VerifyUser',
                password_hash=generate_password_hash('password123'),
                avatar_color='#e94560',
                is_verified=False,
                verify_token=token,
                verify_token_expires=datetime.now(timezone.utc) + timedelta(hours=24)
            )
            db.session.add(user)
            db.session.commit()
            
            response = client.get(f'/auth/verify/{token}', follow_redirects=True)
            assert response.status_code == 200
            
            user = User.query.filter_by(email='verify@example.com').first()
            assert user.is_verified == True
            assert user.verify_token is None
    
    def test_verify_email_expired_token(self, app, client):
        with app.app_context():
            import secrets
            from datetime import datetime, timezone, timedelta
            token = secrets.token_urlsafe(32)
            user = User(
                email='expired@example.com',
                nickname='ExpiredUser',
                password_hash=generate_password_hash('password123'),
                avatar_color='#e94560',
                is_verified=False,
                verify_token=token,
                verify_token_expires=datetime.now(timezone.utc) - timedelta(hours=1)
            )
            db.session.add(user)
            db.session.commit()
            
            response = client.get(f'/auth/verify/{token}', follow_redirects=True)
            assert response.status_code == 200
            
            user = User.query.filter_by(email='expired@example.com').first()
            assert user is None
    
    def test_verify_email_invalid_token(self, app, client):
        response = client.get('/auth/verify/invalid-token', follow_redirects=True)
        assert response.status_code == 200


class TestRateLimiting:
    def test_login_rate_limit(self, app, client):
        with app.app_context():
            user = User(
                email='test@example.com',
                nickname='testuser',
                password_hash=generate_password_hash('password123'),
                avatar_color='#e94560'
            )
            db.session.add(user)
            db.session.commit()
            
            for i in range(10):
                response = client.post('/auth/login', data={
                    'email': 'test@example.com',
                    'password': 'wrongpassword'
                })
            
            response = client.post('/auth/login', data={
                'email': 'test@example.com',
                'password': 'wrongpassword'
            })
            
            assert response.status_code == 429
