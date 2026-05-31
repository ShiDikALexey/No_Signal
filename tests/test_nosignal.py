"""
Интеграционные и юнит-тесты для мессенджера No_Signal v0.3.0
Покрывают: REST API, файлы, Socket.IO события, админ-панель, безопасность, криптографию
"""
import os
import io
import pytest
from unittest.mock import patch
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash
from app import create_app
from extensions import db, socketio
from models import User, Chat, Message, UserChatSettings
import crypto


# =============================================================================
# ФИКСТУРЫ
# =============================================================================

@pytest.fixture
def test_encryption_key():
    """Генерация уникального ключа шифрования для каждого теста."""
    return Fernet.generate_key()


@pytest.fixture
def app(test_encryption_key):
    """
    Инициализация тестового приложения с чистой SQLite БД в памяти.
    Ключ шифрования генерируется динамически для изоляции тестов.
    """
    test_fernet = Fernet(test_encryption_key)

    with patch.object(crypto, '_fernet', test_fernet):
        app = create_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['UPLOAD_FOLDER'] = os.path.join(
            os.path.dirname(__file__), 'test_uploads'
        )
        app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()

        upload_folder = app.config['UPLOAD_FOLDER']
        if os.path.exists(upload_folder):
            for f in os.listdir(upload_folder):
                try:
                    os.remove(os.path.join(upload_folder, f))
                except OSError:
                    pass
            try:
                os.rmdir(upload_folder)
            except OSError:
                pass


@pytest.fixture
def user_factory(app):
    """
    Фабрика пользователей. Возвращает dict с данными пользователя
    (а не ORM-объект, чтобы избежать DetachedInstanceError).
    """
    counter = [0]

    def create_user(email=None, nickname=None, password='password123',
                    is_admin=False, avatar_color='#ff0000'):
        counter[0] += 1
        email = email or f'user{counter[0]}_{id(object())}@example.com'
        nickname = nickname or f'User{counter[0]}_{id(object())}'

        with app.app_context():
            user = User(
                email=email,
                nickname=nickname,
                password_hash=generate_password_hash(password),
                avatar_color=avatar_color,
                is_admin=is_admin
            )
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        return {
            'id': user_id,
            'email': email,
            'nickname': nickname,
            'password': password,
            'is_admin': is_admin,
            'avatar_color': avatar_color
        }

    return create_user


@pytest.fixture
def auth_client_factory(app):
    """
    Фабрика авторизованных HTTP-клиентов.
    Принимает dict пользователя (от user_factory) или создаёт нового.
    """
    def create_auth_client(user_data=None, email=None, nickname=None,
                           password='password123', is_admin=False):
        if user_data:
            email = user_data['email']
            password = user_data['password']
        else:
            email = email or f'auto_{id(object())}@example.com'
            nickname = nickname or f'Auto{id(object())}'
            with app.app_context():
                user = User(
                    email=email,
                    nickname=nickname,
                    password_hash=generate_password_hash(password),
                    avatar_color='#ff0000',
                    is_admin=is_admin
                )
                db.session.add(user)
                db.session.commit()

        client = app.test_client()
        client.post('/auth/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)
        return client

    return create_auth_client


@pytest.fixture
def socket_client_factory(app):
    """
    Фабрика Socket.IO тестовых клиентов.
    Создаёт подключённый flask_socketio.test_client с авторизованной сессией.
    """
    clients = []

    def create_socket_client(user_data, password=None):
        pwd = password or user_data['password']
        http_client = app.test_client()
        http_client.post('/auth/login', data={
            'email': user_data['email'],
            'password': pwd
        }, follow_redirects=True)

        socket_client = socketio.test_client(
            app,
            namespace='/',
            flask_test_client=http_client
        )
        clients.append(socket_client)
        return socket_client

    yield create_socket_client

    for sc in clients:
        try:
            sc.disconnect()
        except Exception:
            pass


@pytest.fixture
def private_chat_fixture(app, user_factory):
    """
    Создаёт тестовый приватный чат между двумя пользователями.
    Возвращает кортеж: (chat_id, user1_dict, user2_dict).
    """
    user1 = user_factory('chat_u1@example.com', 'ChatUser1', 'pass123', avatar_color='#ff0000')
    user2 = user_factory('chat_u2@example.com', 'ChatUser2', 'pass123', avatar_color='#2ecc71')

    with app.app_context():
        u1 = User.query.get(user1['id'])
        u2 = User.query.get(user2['id'])
        chat = Chat(is_group=False)
        db.session.add(chat)
        db.session.flush()
        chat.members.append(u1)
        chat.members.append(u2)
        db.session.commit()
        chat_id = chat.id

    return chat_id, user1, user2


# =============================================================================
# 1. ТЕСТИРОВАНИЕ REST API И ФАЙЛОВ (routes)
# =============================================================================

class TestFileUpload:
    """Тесты загрузки файлов через POST /api/upload."""

    def test_upload_file_success(self, app, user_factory, auth_client_factory):
        """Успешная загрузка файла с проверкой UUID в имени."""
        user = user_factory('upload@example.com', 'UploadUser')
        client = auth_client_factory(user_data=user)

        data = {
            'file': (io.BytesIO(b'fake image content for testing'), 'test_photo.jpg')
        }
        response = client.post('/api/upload', data=data, content_type='multipart/form-data')

        assert response.status_code == 200
        result = response.get_json()
        assert 'file_url' in result
        assert 'file_name' in result
        assert 'file_type' in result
        assert 'file_size' in result
        assert result['file_name'] == 'test_photo.jpg'
        assert result['file_type'] == 'image'
        assert result['file_size'] == len(b'fake image content for testing')

        filename = result['file_url'].split('/')[-1]
        assert '_' in filename
        uuid_part = filename.split('_')[0]
        assert len(uuid_part) == 8

    def test_upload_file_various_types(self, app, user_factory, auth_client_factory):
        """Загрузка файлов разных типов с проверкой классификации."""
        user = user_factory('types@example.com', 'TypesUser')
        client = auth_client_factory(user_data=user)

        test_files = [
            ('video.mp4', 'video'),
            ('audio.mp3', 'audio'),
            ('document.pdf', 'document'),
            ('archive.zip', 'archive'),
            ('script.py', 'other'),
            ('data.json', 'document'),
            ('presentation.pptx', 'document'),
            ('image.png', 'image'),
            ('webpage.html', 'other'),
        ]

        for filename, expected_type in test_files:
            data = {'file': (io.BytesIO(b'test content'), filename)}
            response = client.post('/api/upload', data=data, content_type='multipart/form-data')
            assert response.status_code == 200, f"Failed for {filename}"
            result = response.get_json()
            assert result['file_type'] == expected_type, (
                f"Expected {expected_type} for {filename}, got {result['file_type']}"
            )

    def test_upload_file_disallowed_extension(self, app, user_factory, auth_client_factory):
        """Загрузка файла с недопустимым расширением — возврат 400."""
        user = user_factory('disallow@example.com', 'DisallowUser')
        client = auth_client_factory(user_data=user)

        data = {'file': (io.BytesIO(b'malicious content'), 'hack.php')}
        response = client.post('/api/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400
        result = response.get_json()
        assert 'error' in result

    def test_upload_file_size_limit(self, app, user_factory, auth_client_factory):
        """
        Тест лимита размера файла.
        Подменяет MAX_CONTENT_LENGTH на 1000 байт, отправляет файл 2 КБ.
        """
        user = user_factory('limit@example.com', 'LimitUser')
        client = auth_client_factory(user_data=user)

        app.config['MAX_CONTENT_LENGTH'] = 1000

        large_content = b'x' * 2048
        data = {'file': (io.BytesIO(large_content), 'large_file.jpg')}
        response = client.post('/api/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 413

        app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024


class TestChatManagement:
    """Тесты управления чатами: pin, mute, clear."""

    def test_toggle_pin_chat(self, app, auth_client_factory, private_chat_fixture):
        """Закрепление/открепление чата с проверкой флага в UserChatSettings."""
        chat_id, user1, user2 = private_chat_fixture
        client = auth_client_factory(user_data=user1)

        with app.app_context():
            settings = UserChatSettings.query.filter_by(user_id=user1['id'], chat_id=chat_id).first()
            assert settings is not None

        response = client.post(f'/api/chats/{chat_id}/pin')
        assert response.status_code == 200
        assert response.get_json()['is_pinned'] is True

        with app.app_context():
            settings = UserChatSettings.query.filter_by(user_id=user1['id'], chat_id=chat_id).first()
            assert settings.is_pinned is True

        response = client.post(f'/api/chats/{chat_id}/pin')
        assert response.status_code == 200
        assert response.get_json()['is_pinned'] is False

        with app.app_context():
            settings = UserChatSettings.query.filter_by(user_id=user1['id'], chat_id=chat_id).first()
            assert settings.is_pinned is False

    def test_toggle_mute_chat(self, app, auth_client_factory, private_chat_fixture):
        """Включение/выключение уведомлений с проверкой флага в UserChatSettings."""
        chat_id, user1, user2 = private_chat_fixture
        client = auth_client_factory(user_data=user1)

        with app.app_context():
            settings = UserChatSettings.query.filter_by(user_id=user1['id'], chat_id=chat_id).first()
            assert settings is not None

        response = client.post(f'/api/chats/{chat_id}/mute')
        assert response.status_code == 200
        assert response.get_json()['is_muted'] is True

        with app.app_context():
            settings = UserChatSettings.query.filter_by(user_id=user1['id'], chat_id=chat_id).first()
            assert settings.is_muted is True

        response = client.post(f'/api/chats/{chat_id}/mute')
        assert response.status_code == 200
        assert response.get_json()['is_muted'] is False

        with app.app_context():
            settings = UserChatSettings.query.filter_by(user_id=user1['id'], chat_id=chat_id).first()
            assert settings.is_muted is False

        response = client.post(f'/api/chats/{chat_id}/mute')
        assert response.status_code == 200
        assert response.get_json()['is_muted'] is True

        with app.app_context():
            settings = UserChatSettings.query.filter_by(user_id=user1['id'], chat_id=chat_id).first()
            assert settings.is_muted is True

        response = client.post(f'/api/chats/{chat_id}/mute')
        assert response.status_code == 200
        assert response.get_json()['is_muted'] is False

    def test_clear_chat_messages(self, app, auth_client_factory, private_chat_fixture,
                                  test_encryption_key):
        """Очистка истории чата с проверкой удаления записей из БД."""
        chat_id, user1, user2 = private_chat_fixture
        client = auth_client_factory(user_data=user1)
        test_fernet = Fernet(test_encryption_key)

        with app.app_context():
            for i in range(5):
                msg = Message(
                    chat_id=chat_id,
                    sender_id=user1['id'],
                    text=test_fernet.encrypt(f'Сообщение {i}'.encode()).decode(),
                    file_url=None
                )
                db.session.add(msg)
            db.session.commit()
            assert Message.query.filter_by(chat_id=chat_id).count() == 5

        response = client.post(f'/api/chats/{chat_id}/clear')
        assert response.status_code == 200
        assert response.get_json()['success'] is True

        with app.app_context():
            assert Message.query.filter_by(chat_id=chat_id).count() == 0

    def test_clear_chat_no_access(self, app, user_factory, auth_client_factory):
        """Попытка очистить чат без доступа — 403."""
        outsider = user_factory('outsider@example.com', 'Outsider', 'pass123')
        client = auth_client_factory(user_data=outsider)

        with app.app_context():
            u1 = User.query.get(user_factory('u1@example.com', 'U1', 'pass123')['id'])
            u2 = User.query.get(user_factory('u2@example.com', 'U2', 'pass123')['id'])
            chat = Chat(is_group=False)
            db.session.add(chat)
            db.session.flush()
            chat.members.append(u1)
            chat.members.append(u2)
            db.session.commit()
            chat_id = chat.id

        response = client.post(f'/api/chats/{chat_id}/clear')
        assert response.status_code == 403


# =============================================================================
# 2. ТЕСТИРОВАНИЕ REAL-TIME (Socket.IO события)
# =============================================================================

class TestSocketIOEvents:
    """Тесты WebSocket событий через flask_socketio.test_client."""

    def test_send_message_text_encrypted(self, app, socket_client_factory,
                                          private_chat_fixture):
        """Отправка текста через сокет — проверка шифрования в БД."""
        chat_id, user1, user2 = private_chat_fixture
        socket_client = socket_client_factory(user1)

        socket_client.emit('join_chat', {'chat_id': chat_id})
        socket_client.emit('send_message', {
            'chat_id': chat_id,
            'text': 'Привет, это тест шифрования!'
        })

        with app.app_context():
            msg = Message.query.filter_by(chat_id=chat_id).first()
            assert msg is not None
            assert msg.text != 'Привет, это тест шифрования!'
            assert crypto.decrypt(msg.text) == 'Привет, это тест шифрования!'

    def test_send_message_with_file(self, app, socket_client_factory,
                                     private_chat_fixture):
        """Отправка сообщения с файлом (эмуляция Drag & Drop)."""
        chat_id, user1, user2 = private_chat_fixture
        socket_client = socket_client_factory(user1)

        socket_client.emit('join_chat', {'chat_id': chat_id})
        socket_client.emit('send_message', {
            'chat_id': chat_id,
            'text': 'Смотри файл',
            'file_url': '/uploads/abc1234_photo.jpg',
            'file_name': 'photo.jpg',
            'file_type': 'image',
            'file_size': 12345
        })

        with app.app_context():
            msg = Message.query.filter_by(chat_id=chat_id).first()
            assert msg is not None
            assert msg.file_url == '/uploads/abc1234_photo.jpg'
            assert msg.file_name == 'photo.jpg'
            assert msg.file_type == 'image'
            assert msg.file_size == 12345
            assert crypto.decrypt(msg.text) == 'Смотри файл'

    def test_typing_stop_typing_broadcast(self, app, socket_client_factory,
                                           private_chat_fixture):
        """
        Проверка броадкаста typing/stop_typing.
        Два клиента: отправитель (user1) и получатель (user2).
        """
        chat_id, user1, user2 = private_chat_fixture

        client1 = socket_client_factory(user1)
        client2 = socket_client_factory(user2)

        client1.emit('join_chat', {'chat_id': chat_id})
        client2.emit('join_chat', {'chat_id': chat_id})

        client1.get_received()
        client2.get_received()

        client1.emit('typing', {'chat_id': chat_id})

        received_by_user2 = client2.get_received()
        typing_events = [e for e in received_by_user2 if e['name'] == 'user_typing']
        assert len(typing_events) == 1
        assert typing_events[0]['args'][0]['user_id'] == user1['id']
        assert typing_events[0]['args'][0]['nickname'] == user1['nickname']
        assert typing_events[0]['args'][0]['chat_id'] == chat_id

        received_by_user1 = client1.get_received()
        typing_self = [e for e in received_by_user1 if e['name'] == 'user_typing']
        assert len(typing_self) == 0

        client1.emit('stop_typing', {'chat_id': chat_id})

        received_by_user2 = client2.get_received()
        stopped = [e for e in received_by_user2 if e['name'] == 'user_stopped_typing']
        assert len(stopped) == 1
        assert stopped[0]['args'][0]['user_id'] == user1['id']

    def test_mark_read(self, app, socket_client_factory, private_chat_fixture,
                       test_encryption_key):
        """Проверка mark_read: is_read=True для непрочитанных сообщений."""
        chat_id, user1, user2 = private_chat_fixture
        test_fernet = Fernet(test_encryption_key)

        with app.app_context():
            for i in range(3):
                msg = Message(
                    chat_id=chat_id,
                    sender_id=user2['id'],
                    text=test_fernet.encrypt(f'Непрочитанное {i}'.encode()).decode(),
                    is_read=False
                )
                db.session.add(msg)
            db.session.commit()
            assert Message.query.filter_by(
                chat_id=chat_id, is_read=False, sender_id=user2['id']
            ).count() == 3

        socket_client = socket_client_factory(user1)
        socket_client.emit('join_chat', {'chat_id': chat_id})
        socket_client.emit('mark_read', {'chat_id': chat_id})

        with app.app_context():
            assert Message.query.filter_by(
                chat_id=chat_id, is_read=False, sender_id=user2['id']
            ).count() == 0

    def test_connect_disconnect_online(self, app, user_factory, socket_client_factory):
        """Эмуляция connect/disconnect — проверка user_online/user_offline broadcast."""
        user1 = user_factory('online1@example.com', 'OnlineUser1', 'pass123')
        user2 = user_factory('online2@example.com', 'OnlineUser2', 'pass123')

        client1 = socket_client_factory(user1)
        client2 = socket_client_factory(user2)

        received_by_user2 = client2.get_received()
        online_events = [e for e in received_by_user2 if e['name'] == 'user_online']
        assert len(online_events) >= 1

        last_online = online_events[-1]
        assert 'user_id' in last_online['args'][0]
        assert 'nickname' in last_online['args'][0]

        client1.disconnect()

        received_by_user2 = client2.get_received()
        offline_events = [e for e in received_by_user2 if e['name'] == 'user_offline']
        assert len(offline_events) >= 1
        assert offline_events[-1]['args'][0]['user_id'] == user1['id']
        assert offline_events[-1]['args'][0]['nickname'] == user1['nickname']


# =============================================================================
# 3. АДМИН-ПАНЕЛЬ И БЕЗОПАСНОСТЬ
# =============================================================================

class TestAdminSecurity:
    """Тесты защиты админ-панели."""

    def test_admin_users_requires_admin(self, app, user_factory, auth_client_factory):
        """Обычный пользователь не может получить список пользователей — 403."""
        user = user_factory('regular@example.com', 'RegularUser', is_admin=False)
        client = auth_client_factory(user_data=user)

        response = client.get('/auth/api/admin/users')
        assert response.status_code == 403
        assert 'error' in response.get_json()

    def test_admin_delete_user_requires_admin(self, app, user_factory, auth_client_factory):
        """Обычный пользователь не может удалить другого — 403."""
        regular = user_factory('regular2@example.com', 'Regular2')
        target = user_factory('target@example.com', 'Target')
        client = auth_client_factory(user_data=regular)

        response = client.delete(f'/auth/api/admin/users/{target["id"]}')
        assert response.status_code == 403
        assert 'error' in response.get_json()

    def test_admin_users_success(self, app, user_factory, auth_client_factory):
        """Администратор может получить список пользователей."""
        user_factory('regular3@example.com', 'Regular3')
        admin = user_factory('admin@example.com', 'AdminUser', is_admin=True)
        client = auth_client_factory(user_data=admin)

        response = client.get('/auth/api/admin/users')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 2
        emails = [u['email'] for u in data]
        assert 'regular3@example.com' in emails
        assert 'admin@example.com' in emails

    def test_admin_cannot_delete_self(self, app, user_factory, auth_client_factory):
        """Администратор не может удалить самого себя — 400."""
        admin = user_factory('admin2@example.com', 'Admin2', is_admin=True)
        client = auth_client_factory(user_data=admin)

        response = client.delete(f'/auth/api/admin/users/{admin["id"]}')
        assert response.status_code == 400
        assert 'error' in response.get_json()

    def test_admin_announcement_requires_admin(self, app, user_factory, auth_client_factory):
        """Обычный пользователь не может создать оповещение — 403."""
        user = user_factory('regular4@example.com', 'Regular4', is_admin=False)
        client = auth_client_factory(user_data=user)

        response = client.post('/auth/api/announcement', json={'text': 'Важное объявление'})
        assert response.status_code == 403

    def test_admin_delete_announcement_requires_admin(self, app, user_factory, auth_client_factory):
        """Обычный пользователь не может удалить оповещение — 403."""
        user = user_factory('regular5@example.com', 'Regular5', is_admin=False)
        client = auth_client_factory(user_data=user)

        response = client.delete('/auth/api/announcement')
        assert response.status_code == 403


# =============================================================================
# 4. КРИПТОГРАФИЯ
# =============================================================================

class TestEncryption:
    """Тесты шифрования сообщений."""

    def test_encrypt_decrypt_roundtrip(self, test_encryption_key):
        """Шифрование + расшифровка = оригинальный текст."""
        test_fernet = Fernet(test_encryption_key)
        with patch.object(crypto, '_fernet', test_fernet):
            original = 'Секретное сообщение с кириллицей и символами !@#$%'
            encrypted = crypto.encrypt(original)
            assert encrypted != original
            assert len(encrypted) > len(original)
            assert crypto.decrypt(encrypted) == original

    def test_encrypt_empty_string(self, test_encryption_key):
        """Пустая строка возвращается как есть."""
        test_fernet = Fernet(test_encryption_key)
        with patch.object(crypto, '_fernet', test_fernet):
            assert crypto.encrypt('') == ''

    def test_decrypt_invalid_returns_empty(self, test_encryption_key):
        """Невалидный ciphertext возвращает пустую строку."""
        test_fernet = Fernet(test_encryption_key)
        with patch.object(crypto, '_fernet', test_fernet):
            invalid = 'not_valid_encrypted_data_12345'
            assert crypto.decrypt(invalid) == ''

    def test_message_stored_encrypted(self, app, socket_client_factory,
                                       auth_client_factory, private_chat_fixture):
        """Интеграционный тест: сообщение в БД зашифровано, API возвращает plain text."""
        chat_id, user1, user2 = private_chat_fixture
        socket_client = socket_client_factory(user1)

        socket_client.emit('join_chat', {'chat_id': chat_id})
        socket_client.emit('send_message', {
            'chat_id': chat_id,
            'text': 'Интеграционный тест шифрования'
        })

        with app.app_context():
            msg = Message.query.filter_by(chat_id=chat_id).first()
            assert msg is not None
            assert msg.text != 'Интеграционный тест шифрования'
            assert crypto.decrypt(msg.text) == 'Интеграционный тест шифрования'

        client = auth_client_factory(user_data=user1)
        response = client.get(f'/api/chats/{chat_id}/messages')
        assert response.status_code == 200
        messages = response.get_json()
        assert len(messages) == 1
        assert messages[0]['text'] == 'Интеграционный тест шифрования'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
