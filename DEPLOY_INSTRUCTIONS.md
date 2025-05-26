# VisaPics Deployment Instructions

## Environment Configuration

After running the deploy script, if environment setup fails, create `.env` file manually:

```bash
cat > .env << 'EOF'
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SERVER_NAME=visapics.org

# Generate secure secret key
SECRET_KEY=$(openssl rand -base64 32)

# Stripe Configuration (Use your actual keys)
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY_HERE
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE

# Email Configuration (iCloud Mail)
MAIL_SERVER=smtp.mail.me.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=support@visapics.org
MAIL_PASSWORD=YOUR_EMAIL_APP_PASSWORD
MAIL_DEFAULT_SENDER=support@visapics.org

# Database
DATABASE_URL=sqlite:///payment_data/payments.db

# Domain
DOMAIN=visapics.org
EOF

chmod 600 .env
```

## SSL Certificate Setup

Your Cloudflare certificates are at:
- `/etc/ssl/certs/visapics.org.crt`
- `/etc/ssl/private/visapics.org.key`

Copy them to the project:
```bash
mkdir -p ssl
cp /etc/ssl/certs/visapics.org.crt ssl/cert.pem
cp /etc/ssl/private/visapics.org.key ssl/key.pem
chmod 644 ssl/cert.pem
chmod 600 ssl/key.pem
```

## Quick Deployment

1. Run the automated deploy:
```bash
curl -sSL https://raw.githubusercontent.com/romanpodpriatov/visapics/main/deploy.sh | sudo bash
```

2. If environment setup fails, use the manual .env setup above

3. Start the application:
```bash
docker-compose up -d
```

4. Check status:
```bash
docker-compose ps
docker-compose logs -f visapics
```

## Stripe Keys for visapics.org

Use the test keys provided for initial setup, then switch to live keys for production.

## Health Check

Verify deployment:
```bash
curl https://visapics.org/health
```