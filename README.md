<p align="center">
  <img src="static/favicon.svg" width="72">
</p>

<h1 align="center">NoSignal</h1>

<p align="center">
  Приватный мессенджер с шифрованием на стороне сервера
</p>

<p align="center">
  <a href="https://nosignal.su">nosignal.su</a>
</p>

---

## Возможности

- **Real-time сообщения** — WebSocket через Socket.IO, без задержек
- **Голосовые сообщения** — запись с визуализацией, swipe-to-cancel
- **Файлы** — drag & drop, 50+ форматов, превью фото
- **Групповые чаты** — выбор участников, pin, mute, архив
- **Шифрование** — сообщения шифруются перед сохранением в БД
- **Адаптивный UI** — десктоп, планшеты, телефоны (PWA)

---

## Быстрый старт

```bash
git clone git@github.com:ShiDikALexey/No_Signal.git
cd No_Signal
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Открой `http://localhost:8080`.

## Android

Скачай APK из [Releases](https://github.com/ShiDikALexey/No_Signal/releases/latest) или открой [nosignal.su](https://nosignal.su) в Chrome → «Добавить на экран» (PWA).

## Production-деплой

```bash
gunicorn --worker-class gthread --threads 20 -w 2 wsgi:app -b 127.0.0.1:8080
```

Затем nginx (или Caddy) для HTTPS-проксирования с WebSocket:

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

## Стек

`Python` · `Flask` · `Socket.IO` · `SQLite/PostgreSQL` · `Gunicorn` · `Nginx`

---

<p align="center">
  <a href="https://nosignal.su">nosignal.su</a> ·
  <a href="https://github.com/ShiDikALexey/No_Signal/issues">Баг-репорты</a>
</p>
