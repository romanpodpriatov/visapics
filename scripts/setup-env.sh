#!/bin/bash

# Environment Configuration Setup Script for VisaPics
set -e

echo "⚙️  Setting up environment configuration..."

# Check if .env already exists
if [ -f ".env" ]; then
    echo "📋 .env file already exists"
    read -p "Do you want to reconfigure? (y/N): " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "✅ Using existing .env configuration"
        exit 0
    fi
fi

# Copy template
cp .env.production .env

echo "🔧 Please provide the following configuration values:"

# Function to prompt for input with default
prompt_input() {
    local var_name=$1
    local prompt_text=$2
    local default_value=$3
    local is_secret=${4:-false}
    
    if [ "$is_secret" = true ]; then
        echo -n "$prompt_text: "
        read -s user_input
        echo ""
    else
        read -p "$prompt_text [$default_value]: " user_input
    fi
    
    if [ -z "$user_input" ]; then
        user_input=$default_value
    fi
    
    # Update .env file
    sed -i "s|${var_name}=.*|${var_name}=${user_input}|g" .env
}

# Generate random secret key
echo "🔑 Generating secure SECRET_KEY..."
SECRET_KEY=$(openssl rand -base64 32)
sed -i "s|SECRET_KEY=.*|SECRET_KEY=${SECRET_KEY}|g" .env

# Stripe Configuration
echo ""
echo "💳 Stripe Configuration (get keys from https://dashboard.stripe.com/apikeys):"
prompt_input "STRIPE_PUBLISHABLE_KEY" "Stripe Publishable Key (pk_live_...)" "pk_live_your_stripe_publishable_key_here"
prompt_input "STRIPE_SECRET_KEY" "Stripe Secret Key (sk_live_...)" "sk_live_your_stripe_secret_key_here" true

echo ""
echo "🪝 Stripe Webhook Configuration:"
echo "   Create webhook at: https://dashboard.stripe.com/webhooks"
echo "   Endpoint URL: https://visapics.org/webhook"
echo "   Events to select: payment_intent.succeeded, payment_intent.payment_failed, payment_intent.requires_action, payment_intent.canceled"
prompt_input "STRIPE_WEBHOOK_SECRET" "Stripe Webhook Secret (whsec_...)" "whsec_your_webhook_secret_here" true

# Email Configuration
echo ""
echo "📧 Email Configuration (for payment notifications):"
prompt_input "MAIL_USERNAME" "Email address" "your-email@gmail.com"
prompt_input "MAIL_PASSWORD" "Email app password" "your-app-password" true
prompt_input "MAIL_DEFAULT_SENDER" "Sender email" "noreply@visapics.org"

# Validate configuration
echo ""
echo "🔍 Validating configuration..."

# Check if required variables are set
required_vars=("SECRET_KEY" "STRIPE_SECRET_KEY" "STRIPE_PUBLISHABLE_KEY" "STRIPE_WEBHOOK_SECRET")
missing_vars=()

for var in "${required_vars[@]}"; do
    if grep -q "${var}=.*your.*here" .env; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "❌ Missing configuration for: ${missing_vars[*]}"
    echo "   Please edit .env file manually and set proper values"
    exit 1
fi

# Set proper permissions
chmod 600 .env

echo "✅ Environment configuration completed!"
echo "📁 Configuration saved to .env file"

# Show summary (without secrets)
echo ""
echo "📋 Configuration Summary:"
echo "   Domain: visapics.org"
echo "   Environment: production"
echo "   Stripe Mode: $(grep -q 'pk_live' .env && echo 'Live' || echo 'Test')"
echo "   Email: $(grep MAIL_USERNAME .env | cut -d'=' -f2)"

echo ""
echo "🔔 Important reminders:"
echo "   1. Configure Stripe webhook: https://visapics.org/webhook"
echo "   2. Test payment flow after deployment"
echo "   3. Keep .env file secure (600 permissions set)"