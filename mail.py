import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to_email, subject, html_content):
    """Отправка email через SMTP Gmail"""
    
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


def send_password_reset_email(to_email, reset_url):
    """Отправка письма для сброса пароля"""
    
    subject = 'No_Signal — Сброс пароля'
    
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #0d1117;
                color: #f0f6fc;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 16px;
                padding: 40px;
            }}
            .logo {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo-icon {{
                width: 64px;
                height: 64px;
            }}
            .logo-text {{
                font-size: 24px;
                font-weight: 800;
                color: #58a6ff;
                margin-top: 10px;
            }}
            h1 {{
                font-size: 20px;
                font-weight: 600;
                color: #8b949e;
                text-align: center;
                margin-bottom: 30px;
            }}
            .button {{
                display: block;
                width: 100%;
                max-width: 300px;
                margin: 30px auto;
                padding: 14px 24px;
                background-color: #1f6feb;
                color: #ffffff;
                text-decoration: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                text-align: center;
            }}
            .button:hover {{
                background-color: #58a6ff;
            }}
            .warning {{
                background-color: rgba(233, 69, 96, 0.15);
                border: 1px solid #e94560;
                border-radius: 10px;
                padding: 16px;
                margin: 20px 0;
                font-size: 14px;
                color: #e94560;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #30363d;
                font-size: 12px;
                color: #484f58;
                text-align: center;
            }}
            .link {{
                color: #58a6ff;
                word-break: break-all;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                <svg class="logo-icon" viewBox="0 0 64 64" width="64" height="64">
                    <defs>
                        <linearGradient id="lg" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#58a6ff"/>
                            <stop offset="100%" stop-color="#1f6feb"/>
                        </linearGradient>
                    </defs>
                    <rect width="64" height="64" rx="14" fill="#0d1117"/>
                    <g transform="translate(4, 20) scale(2.5)">
                        <path d="M2 12h5l2-4 2 8 2-6 1 3h8" fill="none" stroke="url(#lg)" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                        <line x1="13" y1="12" x2="22" y2="12" stroke="#e94560" stroke-width="1.5" stroke-linecap="round"/>
                        <circle cx="17" cy="12" r="1.5" fill="#e94560"/>
                        <line x1="15" y1="10" x2="19" y2="14" stroke="#e94560" stroke-width="1.5" stroke-linecap="round"/>
                        <line x1="19" y1="10" x2="15" y2="14" stroke="#e94560" stroke-width="1.5" stroke-linecap="round"/>
                    </g>
                </svg>
                <div class="logo-text">No_Signal</div>
            </div>
            
            <h1>Сброс пароля</h1>
            
            <p>Вы запросили сброс пароля для вашего аккаунта No_Signal.</p>
            
            <a href="{reset_url}" class="button">Сбросить пароль</a>
            
            <div class="warning">
                ⚠️ Ссылка действительна в течение <strong>1 часа</strong>. Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.
            </div>
            
            <p>Если кнопка не работает, скопируйте эту ссылку в браузер:</p>
            <p class="link">{reset_url}</p>
            
            <div class="footer">
                <p>Это автоматическое письмо. Не отвечайте на него.</p>
                <p>© 2026 No_Signal. Все права защищены.</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return send_email(to_email, subject, html_content)


def send_test_email(to_email):
    """Отправка тестового письма"""
    
    subject = 'No_Signal — Тестовое письмо'
    
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #0d1117;
                color: #f0f6fc;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 16px;
                padding: 40px;
            }}
            h1 {{
                color: #58a6ff;
                font-size: 24px;
            }}
            .success {{
                background-color: rgba(46, 164, 79, 0.15);
                border: 1px solid #2ea44f;
                border-radius: 10px;
                padding: 16px;
                margin: 20px 0;
                color: #2ea44f;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✅ Тестовое письмо</h1>
            <div class="success">
                <strong>Поздравляем!</strong><br>
                Email-интеграция No_Signal работает корректно.
            </div>
            <p>Это тестовое письмо подтверждает, что система отправки email настроена правильно.</p>
            <p>Теперь пользователи смогут получать письма для сброса пароля.</p>
        </div>
    </body>
    </html>
    '''
    
    return send_email(to_email, subject, html_content)
