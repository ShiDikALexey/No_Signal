import pytest
from app import create_app
from extensions import db
from models import User, Chat, Message
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(
            email='test@example.com',
            nickname='TestUser',
            password_hash=generate_password_hash('password123'),
            avatar_color='#ff0000',
            is_verified=True
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def auth_client(client, test_user):
    client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    return client


class TestAuth:
    def test_login_page_loads(self, client):
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'No_Signal' in response.data

    def test_register_page_loads(self, client):
        response = client.get('/auth/register')
        assert response.status_code == 200

    def test_login_success(self, client, test_user):
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_login_wrong_password(self, client, test_user):
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'error' in response.data.lower() or b'alert' in response.data.lower()

    def test_register_success(self, client):
        response = client.post('/auth/register', data={
            'email': 'newuser@example.com',
            'nickname': 'NewUser',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_register_password_mismatch(self, client):
        response = client.post('/auth/register', data={
            'email': 'newuser@example.com',
            'nickname': 'NewUser',
            'password': 'password123',
            'confirm_password': 'differentpassword'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'error' in response.data.lower() or b'alert' in response.data.lower()

    def test_logout(self, auth_client):
        response = auth_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200

    def test_reset_password_page_loads(self, client):
        response = client.get('/auth/reset-password')
        assert response.status_code == 200


class TestChat:
    def test_chat_page_requires_login(self, client):
        response = client.get('/', follow_redirects=True)
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'auth' in response.data.lower()

    def test_chat_page_loads(self, auth_client):
        response = auth_client.get('/')
        assert response.status_code == 200
        assert b'No_Signal' in response.data


class TestProfileAPI:
    def test_get_profile(self, auth_client):
        response = auth_client.get('/auth/api/profile')
        assert response.status_code == 200
        data = response.get_json()
        assert 'nickname' in data
        assert 'email' in data

    def test_change_nickname(self, auth_client):
        response = auth_client.post('/auth/api/profile/nickname', json={
            'nickname': 'NewNickname'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data.get('nickname') == 'NewNickname'

    def test_change_status(self, auth_client):
        response = auth_client.post('/auth/api/profile/status', json={
            'status': 'Hello World'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data.get('status') == 'Hello World'

    def test_change_avatar_color(self, auth_client):
        response = auth_client.post('/auth/api/profile/avatar-color', json={
            'color': '#e94560'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data.get('avatar_color') == '#e94560'


class TestChatAPI:
    def test_get_chats(self, auth_client):
        response = auth_client.get('/api/chats')
        assert response.status_code == 200
        assert isinstance(response.get_json(), list)

    def test_search_users(self, auth_client, test_user):
        response = auth_client.get('/api/users?q=Test')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)


class TestStaticFiles:
    def test_css_loads(self, client):
        response = client.get('/static/style.css')
        assert response.status_code == 200

    def test_js_loads(self, client):
        response = client.get('/static/main.js')
        assert response.status_code == 200

    def test_favicon_loads(self, client):
        response = client.get('/static/favicon.svg')
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
