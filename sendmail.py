#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

def main():
    # 1) Подгружаем .env
    load_dotenv()
    api_key = os.getenv('MAIL_API')
    if not api_key:
        print("❌ Переменная MAIL_API не найдена в .env")
        return

    # 2) Конфигурируем клиент с API‑ключом
    configuration = sib_api_v3_sdk.Configuration()
    # здесь важно именно 'api-key'
    configuration.api_key['api-key'] = api_key
    api_client = sib_api_v3_sdk.ApiClient(configuration)

    # 3) Проверяем аутентификацию — получаем данные аккаунта
    account_api = sib_api_v3_sdk.AccountApi(api_client)
    try:
        account_info = account_api.get_account()
        print("✅ Аутентификация прошла успешно. Ваш аккаунт:")
        print(f"   Email: {account_info.email}")
        print(f"   Plan:  {account_info.plan_code}")
    except ApiException as e:
        print("❌ Не удалось аутентифицироваться:", e)
        return

    # 4) Отправляем тестовое письмо через Transactional API
    smtp_api = sib_api_v3_sdk.TransactionalEmailsApi(api_client)
    mail = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": "cooki.fc@gmail.com", "name": "Test Recipient"}],
        sender={"email": "support@visapics.org", "name": "Roman Podpriatov"},
        subject="🔔 Тестовое письмо от visapics (V2)",
        text_content="Это тестовое письмо, отправленное через Brevo Transactional API (V2).",
        html_content="<strong>Это тестовое письмо, отправленное через Brevo Transactional API (V2).</strong>"
    )
    try:
        resp = smtp_api.send_transac_email(mail)
        print("✅ Письмо отправлено. Ответ API:")
        print(resp)
    except ApiException as e:
        print("❌ Ошибка при отправке письма:", e)

if __name__ == '__main__':
    main()
