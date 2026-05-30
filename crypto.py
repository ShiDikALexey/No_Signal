import os
from cryptography.fernet import Fernet

KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.encryption_key')


def get_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as f:
        f.write(key)
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
        return ciphertext
