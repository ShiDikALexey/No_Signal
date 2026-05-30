<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="static/favicon.svg">
    <img src="static/favicon.svg" width="96" alt="No_Signal">
  </picture>
</p>

<h1 align="center">No_Signal</h1>

<p align="center">
  <strong>Приватный мессенджер с end-to-end шифрованием и real-time синхронизацией</strong>
</p>

<p align="center">
  <a href="https://nosignal.su">nosignal.su</a> ·
  <a href="#особенности">Особенности</a> ·
  <a href="#быстрый-старт">Установка</a> ·
  <a href="#changelog">Changelog</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/postgresql-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/socket.io-010101?style=for-the-badge&logo=socket.io&logoColor=white" alt="Socket.IO">
  <br>
  <img src="https://img.shields.io/badge/gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white" alt="Gunicorn">
  <img src="https://img.shields.io/badge/nginx-009639?style=for-the-badge&logo=nginx&logoColor=white" alt="Nginx">
  <img src="https://img.shields.io/badge/Let%27s%20Encrypt-003A70?style=for-the-badge&logo=letsencrypt&logoColor=white" alt="Let's Encrypt">
  <img src="https://img.shields.io/badge/AES%20128%20CBC-blue?style=for-the-badge" alt="AES-128">
</p>

> **⚠️ Тестовый релиз** — Функционал может содержать ошибки и будет дорабатываться.

---

## Особенности

### 💬 Сообщения

| | |
|---|---|
| **Real-time WebSocket** | Мгновенная доставка через Flask-SocketIO |
| **AES-128 CBC шифрование** | Все сообщения шифруются перед сохранением в БД |
| **Read receipts (✓✓)** | Серые — доставлено, синие — прочитано, авто-обновление |
| **Typing indicators** | Анимированные точки, debounce 2с, отключается при отправке |
| **Date separators** | "Сегодня", "Вчера", полная дата для старых сообщений |
| **Message grouping** | Сообщения от одного отправителя группируются |
| **Auto-scroll** | Прокрутка к последнему сообщению при новых |

### 📎 Файлы

| | |
|---|---|
| **Drag & drop** | Перетащите файл в окно — мгновенная отправка в текущий чат |
| **50+ форматов** | Изображения, видео, аудио, документы, архивы, код |
| **25 MB лимит** | Настроен в config.py, покрывает 95% сценариев |
| **Превью перед отправкой** | Миниатюра для фото, имя+размер для остальных |
| **Прогресс-бар** | Анимация загрузки файла на сервер |
| **Auto-detection** | Определение типа файла: image/video/audio/document/archive/other |
| **UUID-filenames** | Безопасные имена файлов, предотвращение перезаписи |

### 🎤 Голосовые сообщения

| | |
|---|---|
| **Запись через 🎤** | Web Audio API + MediaRecorder |
| **Waveform визуализация** | Живой график амплитуды при записи |
| **Playback с прогрессом** | Анимированная волна при воспроизведении |
| **Swipe-to-cancel** | Свайп вверх на мобильных для отмены записи |
| **Пульсация** | Анимация кнопки записи, мигающий индикатор |
| **Длительность** | Отображение времени записи и воспроизведения |

### 👥 Чаты

| | |
|---|---|
| **Личные (1-on-1)** | Создание через поиск пользователей |
| **Групповые** | С выбором участников и именем |
| **Chip-селектор** | Выбранные участники отображаются с возможностью удаления |
| **Pin** | Закрепление чата вверху списка |
| **Archive** | Архивация с отдельной вкладкой и счётчиком |
| **Mute** | Отключение уведомлений, 🔕 бейдж |
| **Контекстное меню** | ПКМ или долгое нажатие на мобильных |
| **Поиск по чатам** | Фильтрация списка по названию |
| **Очистка истории** | Удаление всех сообщений в чате |
| **Удалить/выйти** | Удаление чата или выход из группы |

### 😊 Emoji

| | |
|---|---|
| **8 категорий** | Smileys, Gestures, Hearts, Animals, Food, Travel, Objects, Symbols |
| **Поиск** | Фильтрация по тексту |
| **Табы** | Быстрое переключение между категориями |
| **Вставка в курсор** | Emoji вставляется в позицию курсора в поле ввода |

### 🖼 Lightbox

| | |
|---|---|
| **Клик по фото** | Открытие полноэкранного просмотра |
| **Закрытие** | ✕ кнопка, клик вне фото, Escape |

### 🔐 Аккаунт и профиль

| | |
|---|---|
| **Регистрация / Логин** | Email + пароль, client-side валидация совпадения паролей |
| **Сброс пароля** | Самостоятельный — ввод email + новый пароль |
| **Смена никнейма** | 2-30 символов, проверка уникальности |
| **Смена статуса** | До 100 символов |
| **Аватар** | Загрузка фото (png/jpg/gif/webp), удаление, 15 цветов на выбор |
| **Смена пароля** | С подтверждением старого пароля |
| **Удаление аккаунта** | Каскадное удаление всех чатов и сообщений |

### 🛡 Безопасность

| | |
|---|---|
| **AES-128 CBC (Fernet)** | Сообщения шифруются перед сохранением в БД |
| **Ключ шифрования** | Хранится в файле `.encryption_key` или `ENCRYPTION_KEY` env |
| **CSRF защита** | `credentials: 'same-origin'` на всех API-запросах |
| **Flask-Login** | Сессии с remember-me |
| **UUID filenames** | Предотвращение path traversal и перезаписи |
| **Admin decorator** | Защита админ-роутов с 403 fallback |
| **Login required** | Все роуты, кроме рег/логин/сброс пароля |
| **`.gitignore`** | Ключи и `.env` исключены из репозитория |

### 🎨 UI / UX

| | |
|---|---|
| **Тёмная тема** | Палитра GitHub-dark, не нагружает глаза |
| **Адаптивность** | Мобильные (≤768px), планшеты, десктоп (>1024px) |
| **Desktop max-width** | 1200px центрирование как в Telegram/VK |
| **Safe area insets** | Поддержка notch и home indicator на мобильных |
| **Keyboard handling** | Auto-scroll при фокусе ввода, коррекция viewport |
| **Анимации** | fade-in, scale, slide-up для сообщений, модалок, emoji, lightbox |
| **Dropdown профиля** | Аватар + ник + статус + смена никнейма + настройки + выход |
| **Chat header profile** | Кнопка профиля на мобильных |
| **No-chat placeholder** | Логотип и подсказка когда чат не выбран |
| **Кастомный scrollbar** | Тонкий, тёмный, под темы |

### 🛠 Админ-панель

| | |
|---|---|
| **Системные оповещения** | Публикация/удаление, отображается всем пользователям как баннер |
| **Управление пользователями** | Таблица: ID, ник, email, роль, last_seen |
| **Удаление пользователей** | Каскадное удаление чатов и сообщений, запрет на самоудаление |

### 🔌 Real-time (Socket.IO)

| | |
|---|---|
| **Online/offline статус** | Широковещательные события при connect/disconnect |
| **Typing / Stop typing** | Исключая отправителя |
| **Mark read** | Авто-пометка прочитанных, уведомление отправителя |
| **New message** | Мгновенная доставка в комнату чата |
| **Chat updated** | Обновление списка чатов у всех участников |
| **New chat** | Создание чата в реальном времени |
| **Reconnect** | 50 попыток, задержка 1-5с, авто-переподключение к комнатам |

### ⚙️ Инфраструктура

| | |
|---|---|
| **Flask + Gunicorn** | WSGI сервер, `--threads 20 -w 2` |
| **Nginx** | Проксирование WebSocket, статика, SSL termination |
| **PostgreSQL / SQLite** | PostgreSQL в production, SQLite для разработки |
| **Let's Encrypt** | Автоматическое обновление SSL сертификатов |

---

## Скриншоты

<p align="center">
  <i>(скоро)</i>
</p>

---

## Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                     Browser (Client)                      │
│  main.js · style.css · chat.html · socket.io.min.js      │
└──────────────────────┬──────────────────────────────────┘
                       │
                Socket.IO (WebSocket)
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Flask + Flask-SocketIO (Gunicorn)            │
│                                                          │
│  app.py · auth.py · chat_routes.py · socket_handlers.py  │
└──────┬──────────────────────────────────────┬───────────┘
       │                                      │
       ▼                                      ▼
┌──────────────┐                    ┌────────────────────┐
│  PostgreSQL   │                    │      Nginx          │
│  (данные)     │                    │  /static/ · SSL     │
└──────────────┘                    └────────────────────┘
                                               │
                                               ▼
                                      ┌────────────────┐
                                      │  Let's Encrypt  │
                                      │  (HTTPS)        │
                                      └────────────────┘
```

---

## Быстрый старт

### Требования
- Python 3.12+
- pip

### Установка

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

# Запуск
python app.py
```

Открой `http://localhost:8080` и зарегистрируйся.

> По умолчанию используется SQLite. Для PostgreSQL установи `DATABASE_URL` в `.env`.

---

## Деплой

```bash
# Production с Gunicorn
pip install gunicorn psycopg2-binary

# Запуск
gunicorn --worker-class gthread --threads 20 -w 2 wsgi:app -b 127.0.0.1:8080
```

### Nginx

```nginx
server {
    listen 443 ssl;
    server_name nosignal.su;

    ssl_certificate     /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400s;
    }

    location /static/ {
        alias /path/to/static/;
        expires 30d;
    }
}
```

---

## Использование

### Основные возможности

| Действие | Как |
|----------|-----|
| **Новый чат** | Кнопка `+` в сайдбаре → поиск пользователя или создание группы |
| **Отправить сообщение** | Ввод текста + Enter или кнопка отправки |
| **Прикрепить файл** | Кнопка 📎 или перетащите файл в окно |
| **Голосовое сообщение** | Зажмите 🎤, говорите, отпустите |
| **Emoji** | Кнопка 😊 в поле ввода |
| **Контекстное меню чата** | ПКМ или долгое нажатие на мобильных |
| **Профиль** | Клик по имени/аватару внизу сайдбара |
| **Поиск** | Поле поиска в сайдбаре |
| **Архив** | Кнопка архива в сайдбаре |

### Админ-панель

Доступна администраторам. Позволяет:
- Публиковать и удалять системные оповещения
- Просматривать список пользователей (ID, ник, email, роль, статус, last_seen)
- Удалять пользователей

---

## Socket.IO API

### Client → Server

| Событие | Данные | Описание |
|---------|--------|----------|
| `join_chat` | `{ chat_id }` | Подключиться к комнате чата |
| `send_message` | `{ chat_id, text?, file_url?, file_name?, file_type?, file_size? }` | Отправить сообщение |
| `typing` | `{ chat_id }` | Пользователь печатает |
| `stop_typing` | `{ chat_id }` | Пользователь перестал печатать |
| `mark_read` | `{ chat_id }` | Пометить сообщения как прочитанные |

### Server → Client

| Событие | Данные | Описание |
|---------|--------|----------|
| `new_message` | `{ id, chat_id, sender_id, text, timestamp, file_url, ... }` | Новое сообщение |
| `chat_updated` | `{ id, last_message, ... }` | Обновление чата |
| `new_chat` | `{ id, name, ... }` | Новый чат создан |
| `user_typing` | `{ chat_id, user_id, nickname }` | Пользователь печатает |
| `user_online` | `{ user_id, nickname }` | Пользователь онлайн |
| `user_offline` | `{ user_id, nickname }` | Пользователь офлайн |
| `message_read` | `{ message_id, chat_id, reader_id }` | Сообщение прочитано |

### REST API

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/api/chats` | Список чатов |
| `GET` | `/api/chats/<id>/messages` | Сообщения чата |
| `POST` | `/api/chats/private/<user_id>` | Создать личный чат |
| `POST` | `/api/chats/group` | Создать групповой чат |
| `POST` | `/api/upload` | Загрузить файл |
| `GET` | `/api/users?q=<query>` | Поиск пользователей |
| `GET` | `/api/users/online` | Список онлайн пользователей |
| `POST` | `/api/chats/<id>/pin` | Закрепить/открепить |
| `POST` | `/api/chats/<id>/archive` | Архивировать/разархивировать |
| `POST` | `/api/chats/<id>/mute` | Включить/выключить звук |
| `POST` | `/api/chats/<id>/clear` | Очистить историю |
| `DELETE` | `/api/chats/<id>` | Удалить чат |

---

## Тесты

```bash
pip install pytest
pytest tests/ -v
```

Текущий охват: 19 тестов (авторизация, профиль, чаты, статика).

---

## Changelog

### v0.3.0 (текущий)
- ✅ Drag & drop файлов — перетащите файл в окно для отправки
- ✅ Система друзей полностью удалена
- ✅ Полностью переписан README
- ✅ Фикс клавиатуры на мобильных — чат не уезжает вверх при открытии

### v0.2.0
- ✅ Lightbox: ✕, клик вне фото, Escape
- ✅ Read receipts: ✓✓ серые/синие с авто-обновлением
- ✅ Chat header: фото пользователя (не только буква)
- ✅ Mobile profile: кнопка профиля в chat-header
- ✅ Контекстное меню: фикс позиционирования, закрытие по клику вне
- ✅ Убран крестик выхода (accidental logout fix)
- ✅ WebSocket reconnect: 50 попыток, 1-5с задержка
- ✅ Desktop layout: max-width 1200px, центрирование
- ✅ Emoji picker: 8 категорий, поиск, табы
- ✅ Админ-панель: оповещения, управление пользователями
- ✅ Archive view: отдельная вкладка со счётчиком
- ✅ Online/offline статус в real-time
- ✅ Unread count badge (синий)
- ✅ База данных: PostgreSQL + SQLite

### v0.1.0
- ✅ WebSocket real-time — сообщения без задержек
- ✅ Фикс двойной инициализации Socket.IO
- ✅ Голосовые сообщения — запись и воспроизведение
- ✅ Смена никнейма — модальное окно
- ✅ Поиск пользователей с обработкой ошибок
- ✅ 19 автотестов

---

<p align="center">
  <a href="https://nosignal.su">nosignal.su</a> ·
  <a href="https://github.com/ShiDikALexey/No_Signal/issues">Сообщить о баге</a>
</p>

<p align="center">
  MIT © 2026
</p>
