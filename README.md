<p align="center">
  <img src="static/favicon.svg" width="80" alt="No_Signal" />
</p>

<h1 align="center">No_Signal</h1>

<p align="center">
  <strong>Приватный мессенджер с end-to-end шифрованием</strong><br>
  Работает в локальной сети или на облачном сервере. PostgreSQL, Nginx, HTTPS.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/flask-3.1+-black?style=flat-square&logo=flask" />
  <img src="https://img.shields.io/badge/postgresql-16-blue?style=flat-square&logo=postgresql" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" />
  <img src="https://img.shields.io/badge/status-active-brightgreen?style=flat-square" />
</p>

---

## Возможности

<table>
<tr>
<td width="33%">

### Общение
- **Real-time** сообщения через WebSocket (Socket.IO)
- **Индикатор печати** — видно, когда собеседник набирает текст
- **Эмодзи-пикер** — встроенная панель с поиском и категориями
- **Шифрование** — каждое сообщение шифруется Fernet (AES-128 CBC)

</td>
<td width="33%">

### Чаты и пользователи
- **Приватные чаты** — общение один на один
- **Групповые чаты** — создавай группы из любых пользователей
- **Закрепление** — важные чаты всегда сверху
- **Архивация** — скрывай неактуальные диалоги
- **Mute** — отключи уведомления у чатов

</td>
<td width="33%">

### Файлы и медиа
- **Картинки** — PNG, JPG, GIF, WebP, SVG, BMP
- **Видео** — MP4, WebM, MOV, AVI, MKV
- **Аудио / Войсы** — MP3, WAV, OGG, FLAC + запись голосовых
- **Документы** — PDF, Word, Excel, TXT, CSV, JSON
- **Архивы** — ZIP, RAR, 7z, TAR, GZ
- **Лайтбокс** — просмотр картинок во весь экран

</td>
</tr>
<tr>
<td>

### Аккаунт и профиль
- Регистрация / вход / выход
- 15 цветов аватара на выбор
- Загрузка фото профиля
- Смена никнейма и статуса
- Смена пароля
- Удаление аккаунта

</td>
<td>

### Безопасность
- **HTTPS** — Nginx + Let's Encrypt (production)
- **Шифрование** — Fernet (cryptography), ключ через переменные окружения
- **Без внешних API** — никаких звонков в облака
- **PostgreSQL** — надёжное хранение данных

</td>
<td>

### Интерфейс
- **Тёмная тема** — в стиле GitHub Dark
- **Mobile-first** — адаптивный дизайн под телефоны
- **Drag & Drop** — перетаскивай файлы прямо в чат
- **Контекстное меню** — правый клик по чату
- **Анимации** — плавные переходы и эффекты

</td>
</tr>
</table>

---

## Архитектура

```
📁 No_Signal
├── 📄 app.py               # Точка входа, фабрика приложений
├── 📄 wsgi.py               # Точка входа для gunicorn (production)
├── 📄 config.py             # Конфигурация (из env vars, SQLite/PostgreSQL)
├── 📄 extensions.py         # Flask-расширения (SQLAlchemy, SocketIO, Login)
├── 📄 models.py             # ORM-модели (User, Chat, Message)
├── 📄 auth.py               # Blueprint: логин, регистрация, профиль
├── 📄 chat_routes.py        # Blueprint: чаты, сообщения, файлы
├── 📄 socket_handlers.py    # Socket.IO события (connect, message, typing)
├── 📄 crypto.py             # Шифрование (Fernet)
├── 📄 requirements.txt      # Зависимости
├── 📄 .env.example          # Шаблон переменных окружения
├── 📁 static/
│   ├── 📄 style.css         # Тёмная тема
│   ├── 📄 main.js           # Фронтенд-логика
│   ├── 📄 socket.io.min.js  # Socket.IO клиент
│   └── 📄 favicon.svg       # Иконка
├── 📁 templates/
│   ├── 📄 base.html         # Базовый шаблон
│   ├── 📄 chat.html         # Интерфейс мессенджера
│   ├── 📄 login.html        # Страница входа
│   └── 📄 register.html     # Страница регистрации
└── 📁 uploads/              # Загруженные файлы (игнорируются git)
```

---

## Быстрый старт (локальная разработка)

### 1. Клонирование
```bash
git clone git@github.com:ShiDikALexey/No_Signal.git
cd No_Signal
```

### 2. Установка
```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
# venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

### 3. Запуск (HTTP, SQLite)
```bash
python app.py
```
```
============================================================
No_Signal server running (HTTP)
============================================================
  Локально:  http://localhost:8080
  По сети:   http://192.168.1.xxx:8080
============================================================
```

---

## Production деплой (облачный сервер)

### Переменные окружения

Создай файл `.env` (скопируй из `.env.example`):

```bash
SECRET_KEY=сгенерируй-случайную-строку
DATABASE_URL=postgresql://пользователь:пароль@localhost:5432/nosignal
ENCRYPTION_KEY=сгенерируй-fernet-ключ
UPLOAD_FOLDER=/opt/nosignal/uploads
```

### Генерация ключей
```bash
python -c "
from cryptography.fernet import Fernet
import secrets
print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())
print('SECRET_KEY=' + secrets.token_hex(32))
"
```

### PostgreSQL
```bash
sudo -u postgres psql
CREATE USER nosignal WITH PASSWORD 'password';
CREATE DATABASE nosignal OWNER nosignal;
GRANT ALL PRIVILEGES ON DATABASE nosignal TO nosignal;
\c nosignal
GRANT ALL ON SCHEMA public TO nosignal;
```

### Gunicorn + systemd

Создай `/etc/systemd/system/nosignal.service`:

```ini
[Unit]
Description=No_Signal Messenger
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/nosignal
EnvironmentFile=/opt/nosignal/.env
ExecStart=/opt/nosignal/venv/bin/gunicorn --worker-class gevent -w 1 wsgi:app -b 127.0.0.1:8080
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now nosignal
```

### Nginx + HTTPS
```nginx
server {
    listen 80;
    server_name nosignal.su;
    client_max_body_size 25M;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
sudo certbot --nginx -d nosignal.su
```

---

## Администрирование

### Управление сервисом
```bash
sudo systemctl status nosignal    # статус
sudo systemctl restart nosignal   # перезапуск
sudo systemctl stop nosignal      # остановка
```

### Логи
```bash
sudo journalctl -u nosignal -f    # логи мессенджера (real-time)
sudo tail -f /var/log/nginx/error.log  # ошибки Nginx
```

### База данных
```bash
# Дамп (бекап)
pg_dump -U nosignal nosignal > nosignal_backup.sql

# Восстановление
psql -U nosignal nosignal < nosignal_backup.sql

# Прямое подключение к БД
psql -h localhost -U nosignal -d nosignal
```

### Обновление кода
```bash
cd /opt/nosignal
git pull
sudo systemctl restart nosignal
```

---

## Технологии

| Категория | Стек |
|---|---|
| **Backend** | Python 3.9+, Flask, Flask-SocketIO |
| **ORM / БД** | Flask-SQLAlchemy, SQLite (dev) / PostgreSQL (production) |
| **Production WSGI** | Gunicorn + gevent worker |
| **Аутентификация** | Flask-Login, werkzeug (bcrypt) |
| **Шифрование** | `cryptography` (Fernet / AES-128 CBC) |
| **Real-time** | Socket.IO (WebSocket + polling fallback) |
| **Reverse Proxy** | Nginx + Let's Encrypt (HTTPS) |
| **Frontend** | Vanilla JS, Socket.IO Client |
| **Стили** | CSS3 (тёмная тема, CSS-переменные, анимации) |

---

## Важно

- Шифрование защищает сообщения **в базе данных** — в памяти и по сети они передаются расшифрованными
- Не используй `SECRET_KEY` по умолчанию в production
- Файл `.encryption_key` / `ENCRYPTION_KEY` — ключ шифрования всех сообщений. **Не теряй** и не заливай в git!
- При смене `ENCRYPTION_KEY` все старые сообщения станут нечитаемыми
- `.gitignore` исключает: `.env`, `.encryption_key`, `*.db`, `certs/`, `uploads/`, `__pycache__/`, `*.log`

---

## Roadmap

- [ ] Редактирование сообщений
- [ ] Удаление сообщений
- [ ] Реакции на сообщения
- [ ] Цитирование (reply)
- [ ] Поиск по сообщениям
- [ ] PWA / Service Worker
- [ ] Экспорт чатов
- [ ] Двухфакторная аутентификация (2FA)

---

<p align="center">
  <sub>Сделано на Flask</sub>
</p>
