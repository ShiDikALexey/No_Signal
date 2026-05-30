import os
from cryptography.fernet import Fernet

KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.encryption_key')

_fernet = None


def _get_fernet():
    global _fernet
    if _fernet is None:
        env_key = os.environ.get('ENCRYPTION_KEY', '')
        if env_key:
            key = env_key.encode('utf-8')
        elif os.path.exists(KEY_FILE):
            with open(KEY_FILE, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(KEY_FILE, 'wb') as f:
                f.write(key)
        _fernet = Fernet(key)
    return _fernet


def encrypt(text):
    if not text:
        return text
    return _get_fernet().encrypt(text.encode('utf-8')).decode('utf-8')


def decrypt(ciphertext):
    if not ciphertext:
        return ciphertext
    try:
        return _get_fernet().decrypt(ciphertext.encode('utf-8')).decode('utf-8')
    except Exception:
        return ciphertext
