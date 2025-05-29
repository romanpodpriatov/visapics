#!/bin/bash

# Test Email Integration Script for VisaPics Production
set -e

echo "📧 Testing email integration..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Run ./scripts/setup-env.sh first"
    exit 1
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Check if required email variables are set
if [ -n "$MAIL_API" ]; then
    echo "✅ Brevo API key configured"
    echo "🧪 Testing Brevo email service..."
    
    # Test Brevo API using Python script
    docker-compose exec visapics python -c "
import os
from dotenv import load_dotenv
load_dotenv()

try:
    import sib_api_v3_sdk
    from sib_api_v3_sdk.rest import ApiException
    
    # Initialize Brevo client
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv('MAIL_API')
    client = sib_api_v3_sdk.ApiClient(configuration)
    smtp_api = sib_api_v3_sdk.TransactionalEmailsApi(client)
    
    # Test email
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{'email': 'test@example.com', 'name': 'Test User'}],
        sender={'email': os.getenv('MAIL_DEFAULT_SENDER', 'support@visapics.org'), 'name': 'VisaPics Test'},
        subject='VisaPics Email Test',
        text_content='This is a test email from VisaPics production deployment.',
        html_content='<h1>VisaPics Email Test</h1><p>This is a test email from VisaPics production deployment.</p>'
    )
    
    response = smtp_api.send_transac_email(send_smtp_email)
    print('✅ Brevo email test successful! Message ID:', response.message_id)
    
except ImportError:
    print('❌ Brevo SDK not installed. Run: pip install sib-api-v3-sdk')
except ApiException as e:
    print('❌ Brevo API error:', e.status, e.reason)
    print('   Check your API key and sender email verification')
except Exception as e:
    print('❌ Email test failed:', str(e))
"

elif [ -n "$MAIL_USERNAME" ] && [ -n "$MAIL_PASSWORD" ]; then
    echo "✅ Traditional SMTP configured"
    echo "🧪 Testing SMTP email service..."
    
    # Test SMTP connection
    docker-compose exec visapics python -c "
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    # Load environment variables
    mail_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    mail_port = int(os.getenv('MAIL_PORT', 587))
    mail_username = os.getenv('MAIL_USERNAME')
    mail_password = os.getenv('MAIL_PASSWORD')
    mail_sender = os.getenv('MAIL_DEFAULT_SENDER')
    
    # Test SMTP connection
    server = smtplib.SMTP(mail_server, mail_port)
    server.starttls()
    server.login(mail_username, mail_password)
    
    # Create test email
    msg = MIMEMultipart()
    msg['From'] = mail_sender
    msg['To'] = 'test@example.com'
    msg['Subject'] = 'VisaPics SMTP Test'
    msg.attach(MIMEText('This is a test email from VisaPics SMTP configuration.', 'plain'))
    
    # Note: Not actually sending to avoid spam
    server.quit()
    print('✅ SMTP connection test successful!')
    
except Exception as e:
    print('❌ SMTP test failed:', str(e))
"

else
    echo "❌ No email configuration found"
    echo "   Please configure either MAIL_API (Brevo) or MAIL_USERNAME/MAIL_PASSWORD (SMTP)"
    exit 1
fi

echo ""
echo "📊 Email Configuration Summary:"
if [ -n "$MAIL_API" ]; then
    echo "   Service: Brevo API"
    echo "   Sender: ${MAIL_DEFAULT_SENDER:-support@visapics.org}"
    echo "   API Key: ${MAIL_API:0:15}..."
else
    echo "   Service: Traditional SMTP"
    echo "   Server: ${MAIL_SERVER:-smtp.gmail.com}:${MAIL_PORT:-587}"
    echo "   Username: ${MAIL_USERNAME}"
    echo "   Sender: ${MAIL_DEFAULT_SENDER}"
fi

echo ""
echo "✅ Email integration test completed!"
echo "💡 To send a real test email, modify the recipient in this script"