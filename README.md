<p align="center">
  <img src="static/favicon.svg" width="80" alt="No_Signal" />
</p>

<h1 align="center">📡 No_Signal</h1>

<p align="center">
  <strong>Приватный корпоративный мессенджер для локальной сети</strong><br>
  Без облаков, без слежки, без сигнала во внешний мир — только твоя сеть и твои данные.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/flask-3.1+-black?style=flat-square&logo=flask" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" />
  <img src="https://img.shields.io/badge/status-active-brightgreen?style=flat-square" />
</p>

---

## ✨ Возможности

<table>
<tr>
<td width="33%">

### 💬 Общение
- 🔄 **Real-time** сообщения через WebSocket (Socket.IO)
- ✍️ **Индикатор печати** — видно, когда собеседник набирает текст
- 😀 **Эмодзи-пикер** — встроенная панель эмодзи с поиском и категориями
- 🔒 **Шифрование** — каждое сообщение шифруется Fernet (AES-128 CBC)

</td>
<td width="33%">

### 👥 Чаты и пользователи
- 👤 **Приватные чаты** — общение один на один
- 👨‍👩‍👧 **Групповые чаты** — создавай группы из любых пользователей
- 📌 **Закрепление** — важные чаты всегда сверху
- 📦 **Архивация** — скрывай неактуальные диалоги
- 🔕 **Mute** — отключи уведомления у надоедливых чатов

</td>
<td width="33%">

### 📎 Файлы и медиа
- 🖼️ **Картинки** — PNG, JPG, GIF, WebP, SVG, BMP
- 🎬 **Видео** — MP4, WebM, MOV, AVI, MKV
- 🎵 **Аудио / Войсы** — MP3, WAV, OGG, FLAC + запись голосовых
- 📄 **Документы** — PDF, Word, Excel, TXT, CSV, JSON
- 📦 **Архивы** — ZIP, RAR, 7z, TAR, GZ
- 🔆 **Лайтбокс** — просмотр картинок во весь экран

</td>
</tr>
<tr>
<td>

### 🔐 Аккаунт и профиль
- 📧 Регистрация / вход / выход
- 🎨 15 цветов аватара на выбор
- 📷 Загрузка фото профиля
- ✏️ Смена никнейма и статуса
- 🔑 Смена пароля
- 🗑️ Удаление аккаунта

</td>
<td>

### 🛡️ Безопасность
- 🔐 **HTTPS** — авто-генерация самоподписанных SSL-сертификатов
- 🔑 **Шифрование** — Fernet (cryptography), ключ на стороне сервера
- 🌐 **Локально** — сервер сам определяет LAN IP, другие устройства подключаются по сети
- 🚫 **Без внешних API** — никаких звонков в облака

</td>
<td>

### 🎨 Интерфейс
- 🌙 **Тёмная тема** — в стиле GitHub Dark
- 📱 **Mobile-first** — адаптивный дизайн под телефоны
- 🖱️ **Drag & Drop** — перетаскивай файлы прямо в чат
- ⚡ **Контекстное меню** — правый клик по чату
- 🪄 **Анимации** — плавные переходы и эффекты

</td>
</tr>
</table>

---

## 🧱 Архитектура

```
📁 No_Signal
├── 📄 app.py               # Точка входа, инициализация, SSL, запуск
├── 📄 config.py            # Конфигурация (БД, секретный ключ, пути)
├── 📄 extensions.py        # Flask-расширения (SQLAlchemy, SocketIO, Login)
├── 📄 models.py            # ORM-модели (User, Chat, Message)
├── 📄 auth.py              # Blueprint: логин, регистрация, профиль
├── 📄 chat_routes.py       # Blueprint: чаты, сообщения, файлы
├── 📄 socket_handlers.py   # Socket.IO события (connect, message, typing)
├── 📄 crypto.py            # Шифрование (Fernet)
├── 📄 requirements.txt     # Зависимости
├── 📁 static/
│   ├── 📄 style.css        # 2000+ строк тёмной темы
│   ├── 📄 main.js          # Фронтенд-логика
│   ├── 📄 socket.io.min.js # Socket.IO клиент
│   └── 📄 favicon.svg      # Иконка приложения
├── 📁 templates/
│   ├── 📄 base.html        # Базовый шаблон
│   ├── 📄 chat.html        # Интерфейс мессенджера
│   ├── 📄 login.html       # Страница входа
│   └── 📄 register.html    # Страница регистрации
└── 📁 uploads/             # Загруженные файлы (игнорируются git)
```

---

## 🚀 Быстрый старт

### 1️⃣ Клонирование

```bash
git clone https://github.com/ShiDikALexey/No_Signal.git
cd No_Signal
```

### 2️⃣ Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3️⃣ Запуск

```bash
python app.py
```

Сервер стартует на порту **8080** с авто-сгенерированным SSL:

```
============================================================
No_Signal server running (HTTPS)
============================================================
  Локально:  https://localhost:8080
  По сети:   https://192.168.1.xxx:8080
============================================================
```

### 4️⃣ Подключение с других устройств

1. Убедись, что устройства в одной локальной сети
2. Открой на другом устройстве `https://<LAN-IP>:8080`
3. Прими предупреждение о самоподписанном сертификате
4. Зарегистрируйся — и чаться!

---

## 📦 Сборка в EXE

```bash
pip install pyinstaller
pyinstaller no_signal.spec
```

Готовый `.exe` будет в папке `dist/`. Запускается как обычная программа — двойным кликом.

---

## 🔧 Технологии

| Категория | Стек |
|---|---|
| **Backend** | Python 3.9+, Flask, Flask-SocketIO |
| **ORM / БД** | Flask-SQLAlchemy, SQLite |
| **Аутентификация** | Flask-Login, werkzeug (bcrypt) |
| **Шифрование** | `cryptography` (Fernet / AES-128 CBC) |
| **Real-time** | Socket.IO (WebSocket + polling fallback) |
| **SSL** | `cryptography.x509` (auto self-signed) |
| **Frontend** | Vanilla JS, Socket.IO Client |
| **Стили** | CSS3 (2000+ строк, CSS-переменные, анимации) |
| **Сборка** | PyInstaller (standalone .exe) |

---

## 📸 Скриншоты

> _Добавь скриншоты в папку `screenshots/` и вставь сюда:_
>
> ```html
> <img src="screenshots/chat.png" width="600" />
> <img src="screenshots/emoji.png" width="600" />
> <img src="screenshots/login.png" width="600" />
> ```

---

## 🗺️ Roadmap

- [ ] **Редактирование сообщений**
- [ ] **Удаление сообщений**
- [ ] **Реакции на сообщения**
- [ ] **Цитирование (reply)**
- [ ] **Поиск по сообщениям**
- [ ] **PWA / Service Worker**
- [ ] **Экспорт чатов**
- [ ] **Двухфакторная аутентификация (2FA)**

---

## ⚠️ Важно

- Шифрование защищает сообщения **в базе данных** — в памяти и по сети они передаются расшифрованными (в рамках доверенной локальной сети)
- Не используй в production-окружении с секретным ключом по умолчанию (`SECRET_KEY`)
- Файл `.encryption_key` — ключ шифрования всех сообщений. Не теряй его и не заливай в публичный git!
- Самоподписанный SSL-сертификат генерируется автоматически. Браузеры будут ругаться — это нормально для локальной сети

---

<p align="center">
  <sub>Сделано с 🔥 на Flask</sub>
</p>
