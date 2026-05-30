# No_Signal

Secure private messaging server for local networks.

## Features

- Real-time messaging via Socket.IO
- End-to-end encryption for message content
- User registration and authentication
- Private and group chats
- File sharing (images, documents, etc.)
- Online status tracking
- HTTPS support with auto-generated self-signed certificates
- LAN discovery — accessible from any device on the network

## Tech Stack

- **Backend:** Flask, Flask-SocketIO, Flask-SQLAlchemy
- **Auth:** Flask-Login
- **Crypto:** `cryptography` (Fernet)
- **Frontend:** Vanilla JS, Socket.IO client
- **Database:** SQLite

## Quick Start

1. Clone the repo and install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the server:

```bash
python app.py
```

3. Open in browser:

```
https://localhost:8080
```

The server will automatically generate a self-signed SSL certificate. Other devices on the same network can connect via the LAN IP shown in the console.

## Build Executable

```bash
pip install pyinstaller
pyinstaller no_signal.spec
```

The standalone executable will be in the `dist/` folder.
