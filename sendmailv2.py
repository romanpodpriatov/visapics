#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

def main():
    # 1) Загрузить .env и взять API‑ключ
    load_dotenv()
    api_key = os.getenv('MAIL_API')
    if not api_key:
        print("❌ Переменная MAIL_API не найдена в .env")
        return

    # 2) Настроить клиент SibApiV3Sdk
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key
    client = sib_api_v3_sdk.ApiClient(configuration)
    smtp_api = sib_api_v3_sdk.TransactionalEmailsApi(client)

    # 3) Сформировать тестовое письмо
    mail = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": "cooki.fc@gmail.com", "name": "Test Recipient"}],
        sender={"email": "support@visapics.org", "name": "Роман Подприятов"},
        reply_to={"email": "support@visapics.org", "name": "Роман Подприятов"},
        subject="🔔 Тестовое письмо от visapics.org",
        text_content="Это тестовое письмо, отправленное через Brevo Transactional API.",
        html_content="<strong>Это тестовое письмо, отправленное через Brevo Transactional API.</strong>"
    )

    # 4) Попытаться отправить
    try:
        response = smtp_api.send_transac_email(mail)
        print("✅ Письмо успешно отправлено! Ответ API:")
        print(response)
    except ApiException as e:
        print(f"❌ Ошибка при отправке: {e.status} {e.reason}")
        print(e.body)

if __name__ == "__main__":
    main()
