import os
import sys
import ssl
import socket

from flask import Flask
from config import Config, BASE_DIR
from extensions import db, socketio, login_manager
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


def generate_self_signed_cert(cert_dir, lan_ip):
    cert_file = os.path.join(cert_dir, 'cert.pem')
    key_file = os.path.join(cert_dir, 'key.pem')
    ip_record_file = os.path.join(cert_dir, 'cert_ip.txt')
    
    need_regenerate = False
    if os.path.exists(cert_file) and os.path.exists(key_file):
        if os.path.exists(ip_record_file):
            with open(ip_record_file, 'r') as f:
                saved_ip = f.read().strip()
                if saved_ip != lan_ip:
                    print(f'[INFO] LAN IP изменился: {saved_ip} → {lan_ip}, пересоздаю сертификат...')
                    need_regenerate = True
        else:
            need_regenerate = True
    else:
        need_regenerate = True
    
    if not need_regenerate:
        return cert_file, key_file
    
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime
        import ipaddress

        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, 'No_Signal'),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'No_Signal'),
        ])
        
        san_list = [
            x509.DNSName('localhost'),
            x509.IPAddress(ipaddress.IPv4Address('127.0.0.1')),
        ]
        if lan_ip != '127.0.0.1':
            san_list.append(x509.IPAddress(ipaddress.IPv4Address(lan_ip)))
        
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=3650))
            .add_extension(x509.SubjectAlternativeName(san_list), critical=False)
            .sign(key, hashes.SHA256())
        )

        os.makedirs(cert_dir, exist_ok=True)
        with open(cert_file, 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        with open(key_file, 'wb') as f:
            f.write(key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption()
            ))
        with open(ip_record_file, 'w') as f:
            f.write(lan_ip)
        
        print(f'[INFO] SSL-сертификат создан для: localhost, 127.0.0.1, {lan_ip}')
        return cert_file, key_file
    except Exception as e:
        print(f'[WARN] Не удалось сгенерировать SSL-сертификат: {e}')
        return None, None


def create_app():
    template_dir = get_resource_path('templates')
    static_dir = get_resource_path('static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)

    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins='*')
    login_manager.init_app(app)

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

    lan_ip = get_lan_ip()
    cert_dir = os.path.join(BASE_DIR, 'certs')
    cert_file, key_file = generate_self_signed_cert(cert_dir, lan_ip)

    if cert_file and key_file:
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_ctx.load_cert_chain(certfile=cert_file, keyfile=key_file)
        print('\n' + '='*60)
        print('No_Signal server running (HTTPS)')
        print('='*60)
        print(f'  Локально:  https://localhost:8080')
        print(f'  По сети:   https://{lan_ip}:8080')
        print('='*60)
        print('Другие устройства в сети могут подключиться по адресу выше')
        print('='*60 + '\n')
        socketio.run(app, host='0.0.0.0', port=8080, debug=False,
                     allow_unsafe_werkzeug=True,
                     ssl_context=ssl_ctx)
    else:
        print('\n' + '='*60)
        print('No_Signal server running (HTTP)')
        print('='*60)
        print(f'  Локально:  http://localhost:8080')
        print(f'  По сети:   http://{lan_ip}:8080')
        print('='*60 + '\n')
        socketio.run(app, host='0.0.0.0', port=8080, debug=False,
                     allow_unsafe_werkzeug=True)