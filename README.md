<p align="center">
  <img src="static/favicon.svg" width="96" alt="NoSignal" />
  <h1>NoSignal</h1>
  <p>Приватный мессенджер с шифрованием на сервере и real-time синхронизацией</p>
</p>

<p align="center">
  <a href="https://nosignal.su">🌐 nosignal.su</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/ShiDikALexey/No_Signal/releases">📱 Скачать APK</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/ShiDikALexey/No_Signal/issues">🐛 Report bug</a>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/python-3.12+-3776AB?logo=python&logoColor=white">
  <img alt="Flask" src="https://img.shields.io/badge/flask-3.x-000?logo=flask">
  <img alt="Socket.IO" src="https://img.shields.io/badge/socket.io-realtime-010101?logo=socket.io">
  <img alt="Android" src="https://img.shields.io/badge/android-APK-3DDC84?logo=android&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blue">
</p>

---

## ✨ Возможности

- **💬 Real-time чаты** — мгновенная доставка через WebSocket, индикаторы печати, read receipts (✓✓)
- **🎤 Голосовые сообщения** — запись с живой визуализацией волны, swipe-to-cancel на мобильных, воспроизведение с прогрессом
- **📎 Файлы** — drag & drop, превью изображений, 50+ форматов (фото, видео, аудио, документы, архивы)
- **👥 Группы и чаты** — личные и групповые, pin, mute, архив с отдельной вкладкой, контекстное меню, поиск
- **🔐 Шифрование** — сообщения шифруются перед записью в БД, проверка паролей, CSRF-защита
- **😊 Emoji** — 8 категорий, поиск, вставка в позицию курсора
- **🖼 Lightbox** — полноэкранный просмотр фото по клику
- **🛡 Админ-панель** — системные оповещения, управление пользователями
- **🎨 Тёмная тема** — GitHub-dark палитра, кастомный скроллбар, анимации по всей UI
- **📱 PWA + Android APK** — сайт, мобильное веб-приложение и APK из одного кода

## 📸 Скриншоты

<p align="center">
  <sub>
    <a href="https://nosignal.su">Открыть в браузере</a>
  </sub>
</p>

## 🧱 Архитектура

```
┌───────────────────────────────────────┐
│           Клиент (браузер / APK)       │
│   Vanilla JS · CSS · Socket.IO Client  │
└──────────────────┬────────────────────┘
                   │  WebSocket / REST
                   ▼
┌───────────────────────────────────────┐
│         Flask + Socket.IO (Gunicorn)   │
│   app.py · auth · chat · socket        │
└──────┬───────────────────┬────────────┘
       │                   │
       ▼                   ▼
┌──────────┐      ┌──────────────┐
│ SQLite / │      │    Nginx      │
│PostgreSQL│      │ /static/ · SSL│
└──────────┘      └──────────────┘
```

## 🚀 Быстрый старт

```bash
git clone https://github.com/ShiDikALexey/No_Signal.git
cd No_Signal
python -m venv venv && venv\Scripts\activate   # или source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Открой [http://localhost:8080](http://localhost:8080) и зарегистрируйся.

## 📱 Android

Скачай [APK из Releases](https://github.com/ShiDikALexey/No_Signal/releases/latest) или открой [nosignal.su](https://nosignal.su) в Chrome → «Добавить на главный экран» → PWA без установки.

Приложение загружает интерфейс напрямую с сервера — новые версии доступны мгновенно, без обновления APK.

## 🏗 Production

```bash
gunicorn -k gthread --threads 20 -w 2 wsgi:app -b 127.0.0.1:8080
```

Nginx или Caddy для HTTPS-проксирования с WebSocket:

```nginx
server {
    listen 443 ssl;
    server_name nosignal.su;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

По умолчанию SQLite. Для PostgreSQL укажи `DATABASE_URL` в `.env`.

## 🔧 Стек

`Python` `Flask` `Socket.IO` `Flask-Login` `Flask-SQLAlchemy` `cryptography` `Gunicorn` `Nginx` `SQLite` `PostgreSQL`

---

<p align="center">
  <sub>MIT © 2026 &nbsp;·&nbsp; <a href="https://nosignal.su">nosignal.su</a></sub>
</p>
