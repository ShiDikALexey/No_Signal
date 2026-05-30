<p align="center">
  <img src="static/favicon.svg" width="80" alt="No_Signal" />
</p>

<h1 align="center">No_Signal</h1>

<p align="center">Приватный мессенджер с шифрованием сообщений</p>

<p align="center">
  <a href="https://nosignal.su"><strong>nosignal.su</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12-3776AB?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/flask-3.1-000000?style=flat-square&logo=flask" />
  <img src="https://img.shields.io/badge/postgresql-16-4169E1?style=flat-square&logo=postgresql" />
  <img src="https://img.shields.io/badge/https-22c55e?style=flat-square" />
</p>

---

## Возможности

- 💬 Моментальные сообщения через WebSocket
- 🔒 Шифрование сообщений (AES-128)
- 🎤 Голосовые сообщения
- 📎 Отправка файлов: картинки, видео, документы, архивы
- 😊 Встроенная панель эмодзи
- 👥 Личные и групповые чаты
- 📌 Закрепление, архивация, mute чатов
- 🟢 Онлайн-статус пользователей
- 📱 Адаптивный дизайн (телефон, планшет, десктоп)
- 🌙 Тёмная тема
- ✏️ Смена никнейма, статуса, аватара, пароля

---

## Технологии

| Слой | Стек |
|------|------|
| Backend | Python, Flask, Flask-SocketIO |
| База данных | PostgreSQL |
| Real-time | Socket.IO (WebSocket) |
| Шифрование | Fernet (AES-128 CBC) |
| Frontend | Vanilla JS, CSS |
| Сервер | Nginx, Gunicorn, Let's Encrypt |

---

## Запуск локально

```bash
git clone git@github.com:ShiDikALexey/No_Signal.git
cd No_Signal
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Открой `http://localhost:8080`

---

## Лицензия

MIT