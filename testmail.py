# test_mail.py
import os, smtplib
from email.message import EmailMessage

# Формируем письмо
msg = EmailMessage()
msg['Subject'] = 'Тестовое письмо от visapics'
msg['From']    = os.getenv('MAIL_DEFAULT_SENDER')
msg['To']      = 'cooki.fc@gmail.com'
msg.set_content('Это тестовое письмо, отправленное скриптом на вашем сервере.')

server = smtplib.SMTP(os.getenv('MAIL_SERVER'), int(os.getenv('MAIL_PORT')))
if os.getenv('MAIL_USE_TLS', 'False').lower() in ('true','1'):
    server.starttls()
server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))

# Отправляем и закрываем соединение
server.send_message(msg)
server.quit()

print('✅ Тестовое письмо отправлено на cooki.fc@gmail.com')
