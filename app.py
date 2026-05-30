import os
import sys
import socket

from flask import Flask
from dotenv import load_dotenv

load_dotenv()

from config import Config, BASE_DIR
from extensions import db, socketio, login_manager, limiter
from models import User


def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


def create_app():
    template_dir = get_resource_path('templates')
    static_dir = get_resource_path('static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)

    db.init_app(app)
    socketio.init_app(app, async_mode='threading', cors_allowed_origins='*', logger=False, engineio_logger=False)
    login_manager.init_app(app)
    limiter.init_app(app)

    from auth import auth
    from chat_routes import chat
    from socket_handlers import register_socket_handlers

    app.register_blueprint(auth)
    app.register_blueprint(chat)
    register_socket_handlers(socketio)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app


if __name__ == '__main__':
    app = create_app()

    port = int(os.environ.get('PORT', 8080))
    lan_ip = get_lan_ip()

    print('\n' + '='*60)
    print('No_Signal server running (HTTP)')
    print('='*60)
    print(f'  Локально:  http://localhost:{port}')
    print(f'  По сети:   http://{lan_ip}:{port}')
    print('='*60 + '\n')
    socketio.run(app, host='0.0.0.0', port=port, debug=False,
                 allow_unsafe_werkzeug=True)