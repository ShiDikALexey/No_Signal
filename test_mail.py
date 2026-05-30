"""Тестовый скрипт для проверки отправки email"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from mail import send_test_email

def main():
    if len(sys.argv) < 2:
        print('Использование: python test_mail.py <email>')
        print('Пример: python test_mail.py your@email.com')
        sys.exit(1)
    
    test_email = sys.argv[1]
    
    print(f'Отправка тестового письма на {test_email}...')
    
    if send_test_email(test_email):
        print('[OK] Письмо успешно отправлено!')
        print('Проверьте почтовый ящик (и папку Спам на всякий случай)')
    else:
        print('[ERROR] Ошибка отправки письма')
        print('Проверьте настройки MAIL_USERNAME и MAIL_PASSWORD в .env')

if __name__ == '__main__':
    main()
