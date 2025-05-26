#!/bin/bash

# SSL Certificate Setup Script for VisaPics
set -e

echo "🔒 Setting up SSL certificates..."

# Create ssl directory
mkdir -p ssl

# Check if certificates already exist in Docker format
if [ -f "ssl/cert.pem" ] && [ -f "ssl/key.pem" ]; then
    echo "✅ SSL certificates already configured"
    exit 0
fi

# Method 1: Copy from system locations (Cloudflare Origin certs)
if [ -f "/etc/ssl/certs/visapics.org.crt" ] && [ -f "/etc/ssl/private/visapics.org.key" ]; then
    echo "📋 Found existing Cloudflare certificates, copying..."
    cp /etc/ssl/certs/visapics.org.crt ssl/cert.pem
    cp /etc/ssl/private/visapics.org.key ssl/key.pem
    chmod 644 ssl/cert.pem
    chmod 600 ssl/key.pem
    echo "✅ Cloudflare certificates configured"
    
# Method 2: Let's Encrypt certificates
elif [ -f "/etc/letsencrypt/live/visapics.org/fullchain.pem" ]; then
    echo "📋 Found Let's Encrypt certificates, copying..."
    cp /etc/letsencrypt/live/visapics.org/fullchain.pem ssl/cert.pem
    cp /etc/letsencrypt/live/visapics.org/privkey.pem ssl/key.pem
    chmod 644 ssl/cert.pem
    chmod 600 ssl/key.pem
    echo "✅ Let's Encrypt certificates configured"

# Method 3: Generate self-signed certificates for testing
else
    echo "⚠️  No existing certificates found. Generating self-signed certificates for testing..."
    echo "🔔 Remember to replace with proper certificates for production!"
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem \
        -out ssl/cert.pem \
        -subj "/C=US/ST=CA/L=San Francisco/O=VisaPics/CN=visapics.org" \
        -addext "subjectAltName=DNS:visapics.org,DNS:www.visapics.org"
    
    chmod 644 ssl/cert.pem
    chmod 600 ssl/key.pem
    echo "⚠️  Self-signed certificates generated (NOT for production use)"
fi

# Verify certificates
echo "🔍 Verifying certificates..."
if openssl x509 -in ssl/cert.pem -text -noout | grep -q "visapics.org"; then
    echo "✅ Certificate verification passed"
    
    # Show certificate details
    echo "📜 Certificate details:"
    openssl x509 -in ssl/cert.pem -noout -subject -issuer -dates
else
    echo "❌ Certificate verification failed"
    exit 1
fi

echo "🔒 SSL setup completed successfully!"