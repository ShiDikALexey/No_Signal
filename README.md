<p align="center">
  <img src="static/favicon.svg" width="80" alt="NoSignal" />
</p>

<h3 align="center">NoSignal</h3>
<p align="center">Приватный мессенджер с шифрованием</p>

<p align="center">
  <a href="https://nosignal.su">🌐 nosignal.su</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/ShiDikALexey/No_Signal/releases">📱 APK</a>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/python-3.12+-3776AB?logo=python&logoColor=white">
  <img alt="Flask" src="https://img.shields.io/badge/flask-3.x-000?logo=flask">
  <img alt="Socket.IO" src="https://img.shields.io/badge/socket.io-realtime-010101?logo=socket.io">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blue">
</p>

---

### ✨ Возможности

<table>
<tr><td>💬</td><td><b>Real-time чаты</b> — WebSocket, мгновенная доставка, индикаторы печати</td></tr>
<tr><td>🎤</td><td><b>Голосовые сообщения</b> — запись с визуализацией волны, swipe-to-cancel</td></tr>
<tr><td>📎</td><td><b>Файлы</b> — drag & drop, фото/видео/аудио/документы, превью</td></tr>
<tr><td>👥</td><td><b>Группы</b> — создание, pin, mute, архив, контекстное меню</td></tr>
<tr><td>🔐</td><td><b>Шифрование</b> — сообщения шифруются перед записью в БД</td></tr>
<tr><td>📱</td><td><b>PWA + Android</b> — сайт, веб-приложение или APK из одного кода</td></tr>
</table>

### 🚀 Быстрый старт

```bash
git clone https://github.com/ShiDikALexey/No_Signal.git
cd No_Signal
pip install -r requirements.txt
python app.py
# → http://localhost:8080
```

### 🏗 Production

```bash
gunicorn -k gthread --threads 20 -w 2 wsgi:app -b 127.0.0.1:8080
```

Затем nginx/Caddy для HTTPS-проксирования.

---

<p align="center">
  <sub>MIT &copy; 2026 &nbsp;·&nbsp; <a href="https://github.com/ShiDikALexey/No_Signal/issues">Report bug</a></sub>
</p>
