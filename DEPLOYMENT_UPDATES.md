# Deployment Updates - Brevo Email Integration

## Recent Changes

### 🆕 Added Brevo API Email Support
- **Primary Email Service**: Brevo API for reliable transactional emails
- **Fallback Support**: Traditional SMTP still supported
- **New Environment Variable**: `MAIL_API` for Brevo API key

### 📧 Email Configuration Options

#### Option 1: Brevo API (Recommended)
```bash
MAIL_API=xkeysib-your-api-key-here
MAIL_DEFAULT_SENDER=support@visapics.org
```

#### Option 2: Traditional SMTP (Fallback)
```bash
MAIL_SERVER=smtp-relay.brevo.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-brevo-smtp-username  
MAIL_PASSWORD=your-brevo-smtp-password
MAIL_DEFAULT_SENDER=support@visapics.org
```

### 🔧 Updated Files

1. **docker-compose.yml**
   - Added `MAIL_API` environment variable
   - Updated default MAIL_SERVER to Brevo
   - Added `DOMAIN` environment variable

2. **scripts/setup-env.sh**
   - Interactive email service selection (Brevo vs SMTP)
   - Automatic Brevo configuration
   - Enhanced validation for email settings

3. **requirements.txt**
   - Added `sib-api-v3-sdk>=7.6.0` for Brevo API

4. **email_service.py**
   - Brevo API integration with fallback to Flask-Mail
   - Enhanced error handling for API exceptions
   - Context-aware URL generation for emails

### 🧪 Testing

#### Test Email Integration
```bash
./scripts/test-email.sh
```

#### Manual Email Test
```bash
# Test Brevo API directly
python sendmailv2.py
```

### 🚀 Deployment Instructions

1. **Fresh Deployment**:
   ```bash
   sudo ./deploy.sh
   ```
   - Choose Brevo during email configuration
   - Enter your Brevo API key

2. **Update Existing Deployment**:
   ```bash
   # Update configuration
   ./scripts/setup-env.sh
   
   # Rebuild and restart
   docker-compose build
   docker-compose down
   docker-compose up -d
   ```

3. **Environment Variables Update**:
   ```bash
   # Add to your .env file
   echo "MAIL_API=your-brevo-api-key" >> .env
   echo "MAIL_DEFAULT_SENDER=support@visapics.org" >> .env
   ```

### 📋 Stripe Webhook Configuration

**Important**: Update your Stripe webhook URL to:
```
https://visapics.org/api/webhook
```

**Required Events**:
- `payment_intent.succeeded`
- `payment_intent.payment_failed`
- `payment_intent.requires_action`
- `payment_intent.canceled`

### 🔍 Monitoring

#### Check Email Logs
```bash
# Application logs
docker-compose logs visapics | grep -i email

# Brevo dashboard
https://app.brevo.com/sms-campaign/logs
```

#### Health Check
```bash
curl https://visapics.org/health
```

### 🆘 Troubleshooting

#### Email Not Sending
1. Check API key is correct
2. Verify sender email is verified in Brevo
3. Check logs: `docker-compose logs visapics`

#### Payment Issues
1. Verify Stripe webhook URL is updated
2. Check webhook secret matches
3. Test with Stripe CLI: `stripe listen --forward-to https://visapics.org/api/webhook`

#### Dependencies
```bash
# Reinstall Brevo SDK if needed
docker-compose exec visapics pip install sib-api-v3-sdk>=7.6.0
```

### 🎯 Benefits of Brevo Integration

- **Higher Delivery Rate**: Dedicated transactional email service
- **Better Analytics**: Email delivery tracking and stats
- **No SMTP Limits**: Avoid Gmail/provider restrictions
- **Fallback Support**: Graceful degradation to SMTP if needed
- **Production Ready**: Enterprise-grade email infrastructure

---

For support: Check logs and Brevo dashboard for detailed error messages.