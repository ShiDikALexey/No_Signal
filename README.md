<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="static/favicon.svg">
    <img src="static/favicon.svg" width="96" alt="No_Signal">
  </picture>
</p>

<h1 align="center">No_Signal</h1>

<p align="center">
  <strong>Приватный мессенджер с real-time шифрованием</strong>
</p>

<p align="center">
  <a href="https://nosignal.su">nosignal.su</a> ·
  <a href="#возможности">Возможности</a> ·
  <a href="#скриншоты">Скриншоты</a> ·
  <a href="#установка">Установка</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/postgresql-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/redis-7.0-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis">
  <br>
  <img src="https://img.shields.io/badge/socket.io-010101?style=for-the-badge&logo=socket.io&logoColor=white" alt="Socket.IO">
  <img src="https://img.shields.io/badge/gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white" alt="Gunicorn">
  <img src="https://img.shields.io/badge/nginx-009639?style=for-the-badge&logo=nginx&logoColor=white" alt="Nginx">
  <img src="https://img.shields.io/badge/Let's%20Encrypt-003A70?style=for-the-badge&logo=letsencrypt&logoColor=white" alt="Let's Encrypt">
</p>

> **⚠️ TEST RELEASE** — Это тестовый запуск, а не финальный релиз. Функционал может содержать ошибки и будет дорабатываться.

---

## Возможности

| | |
|---|---|
| 💬 **Мгновенные сообщения** | WebSocket real-time, без задержек |
| 🔒 **Шифрование** | AES-128 CBC (Fernet) — сообщения защищены |
| 🎤 **Голосовые сообщения** | Запись, отправка и прослушивание в чате |
| 📎 **Файлы** | Картинки, видео, документы, архивы — drag & drop |
| 👥 **Чаты** | Личные и групповые, с онлайн-статусом |
| 📌 **Управление чатами** | Закрепление, архивация, mute, очистка |
| 😊 **Эмодзи** | Встроенная панель с поиском и категориями |
| ✏️ **Профиль** | Смена никнейма, аватара, статуса, пароля |
| 🌙 **Тёмная тема** | Глаза не устают |
| 📱 **Адаптивность** | Телефон, планшет, десктоп |
| 🛡 **Админ-панель** | Системные оповещения, управление пользователями |

---

## Скриншоты

<p align="center">
  <i>(скоро)</i>
</p>

---

## Архитектура

```
Client (JS, CSS)
       │ Socket.IO (WebSocket)
       ▼
Flask + Flask-SocketIO
       │
       ├── PostgreSQL (сообщения, пользователи, чаты)
       ├── Nginx (статический контент, SSL)
       └── Let's Encrypt (HTTPS)
```

---

## Установка

```bash
# Клонировать
git clone git@github.com:ShiDikALexey/No_Signal.git
cd No_Signal

# Виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Зависимости
pip install -r requirements.txt

# Настройки
cp .env.example .env

# Запуск
python app.py
```

Открой `http://localhost:8080` и зарегистрируйся.

---

## Тесты

```bash
pip install pytest
pytest tests/ -v
```

---

## Changelog

### v0.2.0-test (текущий)
- ✅ Lightbox: крестик, клик вне фото, Esc для закрытия
- ✅ Chat header: фото пользователя (не только буква)
- ✅ Message status: галочки ✓✓ отправлено/доставлено/прочитано
- ✅ Mobile profile: кнопка профиля в chat-header на телефоне
- ✅ Context menu: фикс позиционирования, закрытие по клику вне
- ✅ Убран крестик выхода (accidental logout fix)
- ✅ WebSocket reconnect: автопереподключение при обрыве

### v0.1.0-test
- ✅ WebSocket real-time — сообщения без задержек
- ✅ Фикс двойной инициализации Socket.IO (главная причина зависаний)
- ✅ Голосовые сообщения — фикс touch-событий на мобильных
- ✅ Десктоп layout — max-width 1200px, центрирование как в VK/Telegram
- ✅ Автопереподключение WebSocket при обрыве (50 попыток)
- ✅ Смена никнейма — красивое модальное окно вместо prompt()
- ✅ Поиск пользователей — добавлена обработка ошибок
- ✅ 19 автотестов (19 passed)

---

<p align="center">
  <a href="https://nosignal.su">nosignal.su</a> ·
  <a href="https://github.com/ShiDikALexey/No_Signal/issues">Сообщить о баге</a>
</p>

<p align="center">
  MIT © 2026
</p>
