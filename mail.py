import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


LOGO_SVG = '''
<svg width="56" height="56" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="64" height="64" rx="14" fill="#0d1117"/>
  <defs>
    <linearGradient id="lg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#58a6ff"/>
      <stop offset="100%" stop-color="#1f6feb"/>
    </linearGradient>
  </defs>
  <g transform="translate(4, 20) scale(2.5)">
    <path d="M2 12h5l2-4 2 8 2-6 1 3h8" fill="none" stroke="url(#lg)" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
    <line x1="13" y1="12" x2="22" y2="12" stroke="#e94560" stroke-width="1.5" stroke-linecap="round"/>
    <circle cx="17" cy="12" r="1.5" fill="#e94560"/>
    <line x1="15" y1="10" x2="19" y2="14" stroke="#e94560" stroke-width="1.5" stroke-linecap="round"/>
    <line x1="19" y1="10" x2="15" y2="14" stroke="#e94560" stroke-width="1.5" stroke-linecap="round"/>
  </g>
</svg>
'''

BASE_STYLES = '''
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    background-color: #f4f6f9;
    margin: 0;
    padding: 0;
    -webkit-font-smoothing: antialiased;
}
.container {
    max-width: 560px;
    margin: 32px auto;
    background-color: #ffffff;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.header {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    padding: 32px 40px 24px;
    text-align: center;
}
.header-logo {
    display: inline-flex;
    align-items: center;
    gap: 12px;
}
.header-logo svg {
    width: 48px;
    height: 48px;
    display: block;
}
.header-logo-text {
    font-size: 22px;
    font-weight: 800;
    color: #58a6ff;
    letter-spacing: -0.5px;
}
.body-content {
    padding: 28px 40px 20px;
}
.body-content p {
    font-size: 15px;
    line-height: 1.6;
    color: #333333;
    margin: 0 0 16px;
}
.body-content p:last-child {
    margin-bottom: 0;
}
h1 {
    font-size: 18px;
    font-weight: 700;
    color: #1a1a2e;
    text-align: center;
    margin: 0 0 20px;
}
.button-wrap {
    text-align: center;
    margin: 24px 0;
}
.button {
    display: inline-block;
    padding: 14px 36px;
    background: linear-gradient(135deg, #1f6feb 0%, #58a6ff 100%);
    color: #ffffff;
    text-decoration: none;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.3px;
}
.alert {
    padding: 14px 18px;
    border-radius: 10px;
    font-size: 13.5px;
    line-height: 1.5;
    margin: 16px 0;
}
.alert-warning {
    background-color: #fff5f5;
    border: 1px solid #fecaca;
    color: #b91c1c;
}
.alert-info {
    background-color: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1e40af;
}
.alert-success {
    background-color: #f0fdf4;
    border: 1px solid #bbf7d0;
    color: #166534;
}
.fallback-link {
    font-size: 12.5px;
    color: #888888;
    word-break: break-all;
    background: #f9fafb;
    padding: 12px 14px;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    margin: 12px 0 0;
}
.fallback-link a {
    color: #1f6feb;
}
.footer {
    padding: 20px 40px 28px;
    border-top: 1px solid #e5e7eb;
    text-align: center;
    font-size: 12px;
    color: #9ca3af;
    line-height: 1.6;
}
.footer a {
    color: #1f6feb;
    text-decoration: none;
}
'''


def send_email(to_email, subject, html_content):
    smtp_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('MAIL_PORT', 587))
    username = os.environ.get('MAIL_USERNAME')
    password = os.environ.get('MAIL_PASSWORD')
    sender = os.environ.get('MAIL_DEFAULT_SENDER', username)

    if not username or not password:
        print('WARNING: MAIL_USERNAME or MAIL_PASSWORD not set in environment')
        return False

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_email

    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f'Error sending email: {e}')
        return False


def _build_html(body_html):
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>{BASE_STYLES}</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="header-logo">
        {LOGO_SVG}
        <span class="header-logo-text">No_Signal</span>
      </div>
    </div>
    <div class="body-content">
      {body_html}
    </div>
    <div class="footer">
      <p>Это автоматическое письмо. Не отвечайте на него.</p>
      <p>No_Signal &mdash; приватный мессенджер с шифрованием</p>
      <p>&copy; 2026 No_Signal. Все права защищены.</p>
    </div>
  </div>
</body>
</html>'''


def send_password_reset_email(to_email, reset_url):
    body = '''
    <h1>Сброс пароля</h1>
    <p>Вы запросили сброс пароля для вашего аккаунта в <strong>No_Signal</strong>.</p>
    <div class="button-wrap">
      <a href="''' + reset_url + '''" class="button">Сбросить пароль</a>
    </div>
    <div class="alert alert-warning">
      <strong>Внимание:</strong> Ссылка действительна в течение <strong>1 часа</strong>.
      Если вы не запрашивали сброс пароля — просто проигнорируйте это письмо.
    </div>
    <div class="fallback-link">
      Если кнопка не работает, скопируйте ссылку в браузер:<br>
      <a href="''' + reset_url + '''">''' + reset_url + '''</a>
    </div>
    '''

    return send_email(to_email, 'No_Signal — Сброс пароля', _build_html(body))


def send_verification_email(to_email, verify_url, nickname):
    body = '''
    <h1>Подтверждение регистрации</h1>
    <p>Привет, <strong>''' + nickname + '''</strong>!</p>
    <p>Спасибо за регистрацию в <strong>No_Signal</strong>. Остался последний шаг &mdash; подтвердите ваш email.</p>
    <div class="button-wrap">
      <a href="''' + verify_url + '''" class="button">Подтвердить email</a>
    </div>
    <div class="alert alert-success">
      После подтверждения вам станут доступны: чаты, файлы, голосовые сообщения, шифрование и real-time синхронизация.
    </div>
    <div class="alert alert-warning">
      <strong>Внимание:</strong> Ссылка действительна в течение <strong>24 часов</strong>.
      Если вы не регистрировались в No_Signal — просто проигнорируйте это письмо.
    </div>
    <div class="fallback-link">
      Если кнопка не работает, скопируйте ссылку в браузер:<br>
      <a href="''' + verify_url + '''">''' + verify_url + '''</a>
    </div>
    '''

    return send_email(to_email, 'No_Signal — Подтверждение регистрации', _build_html(body))


def send_test_email(to_email):
    body = '''
    <h1>Тестовое письмо</h1>
    <div class="alert alert-success">
      <strong>Всё работает!</strong> Email-интеграция No_Signal настроена корректно.
    </div>
    <p>Это тестовое письмо подтверждает, что система отправки email через Gmail SMTP функционирует правильно.</p>
    <p>Теперь пользователи смогут:</p>
    <ul style="color:#333;font-size:15px;line-height:1.7;padding-left:20px;">
      <li>подтверждать email при регистрации</li>
      <li>восстанавливать пароль через email</li>
    </ul>
    '''

    return send_email(to_email, 'No_Signal — Тестовое письмо', _build_html(body))
