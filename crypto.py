import os
import sys
from cryptography.fernet import Fernet

KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.encryption_key')


def get_or_create_key():
    env_key = os.environ.get('ENCRYPTION_KEY', '')
    if env_key:
        return env_key.encode('utf-8')

    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            return f.read()

    import secrets
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as f:
        f.write(key)
    print('WARNING: ENCRYPTION_KEY not set. Generated temporary key. Set in .env for production.', file=sys.stderr)
    return key


_key = get_or_create_key()
_fernet = Fernet(_key)


def encrypt(text):
    if not text:
        return text
    return _fernet.encrypt(text.encode('utf-8')).decode('utf-8')


def decrypt(ciphertext):
    if not ciphertext:
        return ciphertext
    try:
        return _fernet.decrypt(ciphertext.encode('utf-8')).decode('utf-8')
    except Exception:
        return ''
