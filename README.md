<p align="center">
  <picture>
    <img src="static/favicon.svg" width="120" alt="No_Signal" />
  </picture>
</p>

<h1 align="center">📡 No_Signal</h1>

<p align="center">
  <strong>Приватный корпоративный мессенджер</strong><br>
  Шифрование • WebSocket • Тёмная тема • Без облаков
</p>

<p align="center">
  <a href="https://nosignal.su"><img src="https://img.shields.io/website?url=https%3A%2F%2Fnosignal.su&style=flat-square&label=nosignal.su" /></a>
  <img src="https://img.shields.io/badge/python-3.12-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/flask-3.1-000000?style=flat-square&logo=flask" />
  <img src="https://img.shields.io/badge/postgresql-16-4169E1?style=flat-square&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/nginx-1.24-009639?style=flat-square&logo=nginx&logoColor=white" />
  <img src="https://img.shields.io/badge/status-active-22c55e?style=flat-square" />
  <img src="https://img.shields.io/badge/license-MIT-8b5cf6?style=flat-square" />
</p>

<br>

---

## ✨ Что умеет

<table>
<tr>
<td width="50%" valign="top">

### 💬 Чаты и сообщения

<div align="center">
  <picture>
    <img src="https://img.icons8.com/fluency/48/chat.png" width="48" />
  </picture>
</div>

- ✍️ **Live-сообщения** — мгновенная доставка через WebSocket
- ⌨️ **Индикатор печати** — видно, когда печатают
- 😂 **Эмодзи** — панель с поиском и категориями
- 🖼️ **Картинки** — PNG, JPG, GIF, WebP, SVG, лайтбокс
- 📎 **Файлы любые** — PDF, Word, Excel, архивы, перетаскиванием
- 🎤 **Голосовые** — запись и отправка войсов
- 🎬 **Видео** — MP4, WebM, MOV с плеером
- 🔒 **Шифрование** — AES-128 (Fernet) каждое сообщение

</td>
<td width="50%" valign="top">

### 🔐 Аккаунт и профиль

<div align="center">
  <picture>
    <img src="https://img.icons8.com/fluency/48/user.png" width="48" />
  </picture>
</div>

- 📧 Регистрация / вход / выход
- 🎨 15 цветов аватара + своё фото
- ✏️ Никнейм, статус, смена пароля
- 🟢 Онлайн-статус пользователей
- 📌 Закрепление важных чатов
- 📦 Архивация неактуальных
- 🔕 Mute + очистка истории
- 👥 Групповые чаты с любым составом
- 🗑️ Удаление аккаунта

</td>
</tr>
</table>

### 🎨 Интерфейс

<br>

<table>
<tr>
<td>🌙</td><td><strong>Тёмная тема</strong></td><td>GitHub Dark, глаза не устают</td>
</tr>
<tr>
<td>📱</td><td><strong>Адаптивный</strong></td><td>Телефон, планшет, десктоп</td>
</tr>
<tr>
<td>🖱️</td><td><strong>Drag & Drop</strong></td><td>Перетащи файл — отправится</td>
</tr>
<tr>
<td>⚡</td><td><strong>Быстрый</strong></td><td>Nginx + gzip + кеширование</td>
</tr>
<tr>
<td>🔊</td><td><strong>Оповещения</strong></td><td>Звук + вибрация на телефоне</td>
</tr>
</table>

---

## 🏗️ Технологии

```
🔧 Flask 3.1          — веб-фреймворк
💬 Socket.IO          — real-time WebSocket
🗄️ PostgreSQL 16       — база данных (production)
📦 SQLite             — база данных (dev)
🔐 Flask-Login         — аутентификация
🔑 Fernet/AES-128      — шифрование сообщений
🌐 Nginx + Certbot     — HTTPS + прокси
⚡ Gunicorn + gevent   — production WSGI
```

---

## 🚀 Быстрый старт

### Локально (для разработки)

```bash
git clone git@github.com:ShiDikALexey/No_Signal.git
cd No_Signal
python -m venv venv
source venv/bin/activate       # или venv\Scripts\activate на Windows
pip install -r requirements.txt
cp .env.example .env           # отредактируй SECRET_KEY
python app.py
```

Открой `http://localhost:8080` — готово.

### Production (облачный сервер)

```bash
# 1. Создай .env
cp .env.example .env
# Сгенерируй SECRET_KEY и ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; import secrets; print('ENCRYPTION_KEY='+Fernet.generate_key().decode()); print('SECRET_KEY='+secrets.token_hex(32))"

# 2. Настрой PostgreSQL
sudo -u postgres psql
CREATE USER nosignal WITH PASSWORD 'твой_пароль';
CREATE DATABASE nosignal OWNER nosignal;

# 3. Заполни DATABASE_URL в .env
DATABASE_URL=postgresql://nosignal:твой_пароль@localhost:5432/nosignal

# 4. Установи и запусти
pip install -r requirements.txt
gunicorn --worker-class gevent -w 2 wsgi:app -b 127.0.0.1:8080

# 5. Настрой Nginx (см. .env.example)
sudo certbot --nginx -d твой-домен.ru
```

---

## 📱 Скриншоты

<p align="center">
  <i>Добавь скриншоты в папку screenshots/</i>
</p>

```html
<img src="screenshots/chat.png" width="600" />
<img src="screenshots/login.png" width="600" />
<img src="screenshots/emoji.png" width="600" />
```

---

## 🗺️ Что дальше

- [ ] Редактирование и удаление сообщений
- [ ] Реакции (👍❤️😂) на сообщения
- [ ] Ответы (reply/цитирование)
- [ ] Поиск по всем чатам
- [ ] Стикеры и GIF
- [ ] Видеозвонки (WebRTC)
- [ ] PWA — установка как приложение
- [ ] 2FA — двухфакторка

---

## ⚠️ Важно

- **Ключ шифрования** (`.encryption_key` / `ENCRYPTION_KEY`) — единолично расшифровывает ВСЕ сообщения. Не теряй. Не заливай в git.
- При смене ключа старые сообщения станут нечитаемыми.
- `.env`, `*.db`, `certs/`, `uploads/` исключены из git через `.gitignore`.

---

<br>

<p align="center">
  <sub>Built with ❤️ on Flask</sub><br>
  <sub>
    <a href="https://nosignal.su"><img src="https://img.icons8.com/fluency/24/domain.png" width="16" /> nosignal.su</a>
    &nbsp;·&nbsp;
    <a href="https://github.com/ShiDikALexey/No_Signal"><img src="https://img.icons8.com/fluency/24/github.png" width="16" /> GitHub</a>
  </sub>
</p>
