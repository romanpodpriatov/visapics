# Payment System Setup Guide

This guide explains how to set up the Stripe payment integration for the VisaPicture application.

## Overview

The payment system allows users to:
- Purchase high-quality visa photos without watermarks ($2.99)
- Purchase photo + printable 4x6" layout bundle ($4.99)
- Receive download links via email
- Track orders and downloads
- Handle refunds when needed

## Features

✅ **Modern Payment Element**: Stripe's latest payment interface with tabs layout  
✅ **Multiple Payment Methods**: Cards, wallets, bank transfers automatically enabled  
✅ **Secure Payments**: Stripe integration with PCI compliance  
✅ **Email Notifications**: Automatic receipt and download links  
✅ **Order Management**: Unique order numbers and tracking  
✅ **Download Protection**: Time-limited and count-limited downloads  
✅ **Enhanced Webhooks**: Comprehensive event handling with detailed logging  
✅ **Admin Dashboard**: Order monitoring and management  

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies added:
- `stripe>=5.0.0` - Stripe payment processing
- `flask-mail>=0.9.1` - Email notifications
- `python-dotenv>=1.0.0` - Environment variable loading

### 2. Create Stripe Account

1. Go to [stripe.com](https://stripe.com) and create an account
2. Get your API keys from the Stripe Dashboard:
   - **Publishable key** (starts with `pk_test_` or `pk_live_`)
   - **Secret key** (starts with `sk_test_` or `sk_live_`)
3. Set up a webhook endpoint for payment confirmations

### 3. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```bash
# Required for payments
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Required for Flask
SECRET_KEY=your-random-secret-key-here

# Optional for email notifications
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 4. Set Up Stripe Webhooks

1. In your Stripe Dashboard, go to **Developers** → **Webhooks**
2. Click **Add endpoint**
3. Set the endpoint URL to: `https://yourdomain.com/api/webhook`
4. Select these events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `payment_intent.requires_action`
   - `payment_intent.canceled`
5. Copy the webhook signing secret to your `.env` file

**For local testing**, use Stripe CLI:
```bash
# Install Stripe CLI
# Forward events to your local server
stripe listen --forward-to localhost:8000/api/webhook
# Use the webhook secret from CLI output in your .env
```

### 5. Configure Email (Optional)

For Gmail, you'll need to:
1. Enable 2-factor authentication
2. Generate an "App Password" for the application
3. Use the app password in `MAIL_PASSWORD`

## Testing

### Test with Stripe Test Cards

Use these test card numbers:
- **Success**: `4242424242424242`
- **Declined**: `4000000000000002`
- **Requires authentication**: `4000002500003155`

### Test Email Delivery

The system works in "demo mode" without email configuration - it will log email content to the console instead of sending actual emails.

## API Endpoints

### Public Endpoints
- `GET /api/pricing` - Get pricing information
- `POST /api/create-payment-intent` - Create payment intent
- `POST /api/webhook` - Stripe webhook handler
- `GET /download/<order_number>/<file_type>` - Download paid files
- `GET /order/<order_number>` - Get order status
- `GET /payment` - Payment page

### Admin Endpoints (Protect in production!)
- `GET /admin/orders` - View all orders

## Database Schema

The system automatically creates SQLite tables:

- **orders** - Payment orders and status
- **download_logs** - Download tracking
- **email_logs** - Email delivery tracking

## File Structure

```
├── models.py              # Database models and order management
├── payment_service.py     # Stripe integration
├── email_service.py       # Email notifications
├── templates/
│   └── payment.html       # Payment page
├── .env.example           # Environment variables template
└── payments.db           # SQLite database (auto-created)
```

## Security Considerations

⚠️ **Important Security Notes:**

1. **Never commit** `.env` files or API keys to git
2. **Protect admin endpoints** with authentication in production
3. **Use HTTPS** for all payment pages
4. **Validate webhooks** using Stripe signatures
5. **Limit download attempts** to prevent abuse

## Production Deployment

Before going live:

1. **Switch to live Stripe keys** (remove `_test_` from keys)
2. **Set up proper domain** for webhook endpoints
3. **Configure email service** for production
4. **Add authentication** to admin endpoints
5. **Set up monitoring** for failed payments
6. **Test the complete flow** with real payments

## Pricing Configuration

Modify pricing in `payment_service.py`:

```python
PRICING = {
    'single_photo': {
        'amount_cents': 299,  # $2.99
        'currency': 'usd',
        'description': 'Single Visa Photo Download'
    },
    'photo_with_printable': {
        'amount_cents': 499,  # $4.99
        'currency': 'usd', 
        'description': 'Visa Photo + Printable 4x6" Layout'
    }
}
```

## Troubleshooting

### Common Issues

1. **Stripe not initialized**: Check your API keys in `.env`
2. **Webhook failures**: Verify webhook URL and secret
3. **Email not sending**: Check email credentials and Gmail settings
4. **Payment not completing**: Check browser console for JavaScript errors

### Logs

Check application logs for payment-related errors:
```bash
tail -f app.log | grep -i "payment\|stripe\|order"
```

## Support

For payment issues:
- Check order status: `GET /order/<order_number>`
- Review admin dashboard: `GET /admin/orders`
- Process refunds through Stripe Dashboard or API

## Development Notes

- Payment buttons appear after successful photo processing
- All sensitive operations use server-side validation
- Download links are protected and time-limited
- Email templates are responsive and professional
- System gracefully handles network failures and retries