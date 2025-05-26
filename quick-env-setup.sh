#!/bin/bash

# Quick Environment Setup for VisaPics
# Run this if the automated setup failed

set -e

echo "🔧 Quick Environment Setup for VisaPics"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📋 Creating .env from template..."
    cp .env.production .env
fi

echo ""
echo "📝 Please provide your configuration values:"

# Helper function to update env var
update_env_var() {
    local var_name=$1
    local var_value=$2
    
    # Remove existing line and add new one
    grep -v "^${var_name}=" .env > .env.tmp || true
    echo "${var_name}=${var_value}" >> .env.tmp
    mv .env.tmp .env
}

# Generate SECRET_KEY
echo "🔑 Generating SECRET_KEY..."
SECRET_KEY=$(openssl rand -base64 32)
update_env_var "SECRET_KEY" "$SECRET_KEY"

# Get Stripe keys
echo ""
echo "💳 Enter your Stripe keys (from https://dashboard.stripe.com/apikeys):"
read -p "Stripe Publishable Key (pk_live_...): " STRIPE_PK
read -p "Stripe Secret Key (sk_live_...): " -s STRIPE_SK
echo ""
read -p "Stripe Webhook Secret (whsec_...): " -s WEBHOOK_SECRET
echo ""

# Update Stripe configuration
update_env_var "STRIPE_PUBLISHABLE_KEY" "$STRIPE_PK"
update_env_var "STRIPE_SECRET_KEY" "$STRIPE_SK"
update_env_var "STRIPE_WEBHOOK_SECRET" "$WEBHOOK_SECRET"

# Email configuration
echo ""
echo "📧 Email configuration:"
read -p "Email address: " EMAIL_USER
read -p "Email password: " -s EMAIL_PASS
echo ""
read -p "Sender email [noreply@visapics.org]: " EMAIL_SENDER
EMAIL_SENDER=${EMAIL_SENDER:-"noreply@visapics.org"}

update_env_var "MAIL_USERNAME" "$EMAIL_USER"
update_env_var "MAIL_PASSWORD" "$EMAIL_PASS"
update_env_var "MAIL_DEFAULT_SENDER" "$EMAIL_SENDER"

# Set permissions
chmod 600 .env

echo ""
echo "✅ Environment configuration completed!"

# Show final configuration (without secrets)
echo ""
echo "📋 Configuration Summary:"
echo "Domain: visapics.org"
echo "Environment: production"
echo "Stripe Mode: $(echo $STRIPE_PK | grep -q 'pk_live' && echo 'Live' || echo 'Test')"
echo "Email: $EMAIL_USER"

echo ""
echo "🚀 Ready to start application with: docker-compose up -d"