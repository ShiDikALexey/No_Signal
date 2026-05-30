<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="static/favicon.svg">
    <img src="static/favicon.svg" width="96" alt="No_Signal">
  </picture>
</p>

<h1 align="center">No_Signal</h1>

<p align="center">
  <strong>Приватный мессенджер с шифрованием на стороне сервера и real-time синхронизацией</strong>
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
</p>

> **⚠️ Тестовый релиз v0.4.0** — Улучшенная безопасность, производительность и UX.

---

## Особенности

### 💬 Сообщения

| | |
|---|---|
| **Real-time WebSocket** | Мгновенная доставка через Flask-SocketIO |
| **Шифрование сообщений** | Все сообщения шифруются Fernet перед сохранением в БД |
| **Read receipts (✓✓)** | Серые — доставлено, синие — прочитано, авто-обновление |
| **Typing indicators** | Анимированные точки, debounce 2с, отключается при отправке |
| **Date separators** | "Сегодня", "Вчера", полной дата для старых сообщений |
| **Message grouping** | Сообщения от одного отправителя группируются |
| **Auto-scroll** | Прокрутка к последнему сообщению при новых |
| **Cursor-based пагинация** | Загрузка по 50 сообщений, оптимизация производительности |
| **Markdown** | **bold**, *italic*, `code`, ~~strikethrough~~, [links](url) |

### 📎 Файлы

| | |
|---|---|
| **Drag & drop** | Перетащите файл в окно — мгновенная отправка в текущий чат |
| **50+ форматов** | Изображения, видео, аудио, документы, архивы, код |
| **25 MB лимит** | Настроен на сервере, покрывает 95% сценариев |
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
| **Pin** | Закрепление чата вверху списка (per-user) |
| **Archive** | Архивация с отдельной вкладкой и счётчиком (per-user) |
| **Mute** | Отключение уведомлений, 🔕 бейдж (per-user) |
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
| **Сброс пароля** | Email verification с токеном (1 час валидность) |
| **Смена никнейма** | 2-30 символов, проверка уникальности |
| **Смена статуса** | До 100 символов |
| **Аватар** | Загрузка фото (png/jpg/gif/webp), удаление, 15 цветов на выбор |
| **Смена пароля** | С подтверждением старого пароля |
| **Удаление аккаунта** | Каскадное удаление всех чатов и сообщений |

### 🔐 Безопасность

| | |
|---|---|
| **Шифрование сообщений** | Все сообщения шифруются Fernet перед сохранением в БД |
| **Rate limiting** | Защита от brute-force: login (10/min), register (5/hour), reset (3/hour) |
| **Email verification** | Сброс пароля требует подтверждения через email с токеном (1 час) |
| **File access control** | Проверка прав доступа к загруженным файлам |
| **CSRF защита** | `credentials: 'same-origin'` на всех API-запросах |
| **Flask-Login** | Сессии с remember-me |
| **UUID filenames** | Предотвращение path traversal и перезаписи |
| **Admin decorator** | Защита админ-роутов с 403 fallback |
| **Login required** | Все роуты, кроме рег/логин/сброс пароля |

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
| **Toast notifications** | Современные уведомления вместо alert() |
| **Custom confirm dialogs** | Красивые диалоги подтверждения вместо confirm() |
| **Skeleton loaders** | Анимированные заглушки при загрузке контента |
| **Markdown поддержка** | **bold**, *italic*, `code`, ~~strikethrough~~, [links](url) |

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
| **Flask-Limiter** | Rate limiting для защиты от abuse |
| **Gmail SMTP** | Email-верификация для сброса пароля |
| **Database indexes** | Оптимизация запросов для Message, User, UserChatSettings |

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

### Email-верификация

No_Signal использует Gmail SMTP для отправки писем (сброс пароля). Настройка:

```env
# .env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your@gmail.com
```

Для получения пароля приложения:
1. Включить 2FA в Google Account
2. Создать пароль приложения: https://myaccount.google.com/apppasswords

Тестовая отправка:
```bash
python test_mail.py your@email.com
```

---

## Accessibility

No_Signal следует принципам доступности:

- **ARIA атрибуты**: Все интерактивные элементы имеют соответствующие ARIA labels
- **Keyboard navigation**: Полная навигация с клавиатуры (Tab, Enter, Space, Escape)
- **Screen reader support**: Семантическая разметка для программ чтения с экрана
- **Focus management**: Корректное управление фокусом в модальных окнах
- **High contrast**: Достаточный контраст текста для readability

---

## Changelog

### v0.4.0 (текущий)
- ✅ **Безопасность**: Убран hardcoded admin email
- ✅ **Безопасность**: SECRET_KEY теперь генерируется автоматически или берётся из .env
- ✅ **Безопасность**: Добавлен Flask-Limiter для rate limiting на критические endpoints
- ✅ **Безопасность**: Сброс пароля теперь требует email verification с токеном
- ✅ **Безопасность**: Добавлена проверка доступа к загруженным файлам
- ✅ **Архитектура**: Per-user настройки чатов (pin, archive, mute) через UserChatSettings
- ✅ **Производительность**: Пагинация сообщений с cursor-based загрузкой
- ✅ **Производительность**: Оптимизирован запрос списка чатов
- ✅ **Производительность**: Добавлены индексы БД для Message, User, UserChatSettings
- ✅ **UX**: Toast notifications вместо alert()
- ✅ **UX**: Custom confirm dialogs вместо confirm()
- ✅ **UX**: Skeleton loaders при загрузке чатов и сообщений
- ✅ **UX**: Markdown поддержка в сообщениях (bold, italic, code, links, strikethrough)
- ✅ **Email**: Интеграция Gmail SMTP для сброса пароля (HTML-письма с брендингом)
- ✅ **Infra**: python-dotenv для загрузки переменных окружения
- ✅ **Accessibility**: ARIA атрибуты для всех интерактивных элементов
- ✅ **Accessibility**: Keyboard navigation (Enter/Space для кнопок)
- ✅ **Code quality**: Исправлен deprecated datetime.utcnow() на timezone-aware datetime.now(timezone.utc)
- ✅ **Миграция**: Создан скрипт migrate.py для переноса данных в новую схему

### v0.3.0
- ✅ Drag & drop файлов — перетащите файл в окно для отправки
- ✅ Система друзей полностью удалена
- ✅ Полностью переписан README
- ✅ Фикс клавиатуры на мобильных — чат не уезжает вверх при открытии
- ✅ Упрощена обработка viewport — CSS 100dvh вместо JS visualViewport

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
