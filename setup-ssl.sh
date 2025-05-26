#!/bin/bash

# SSL Setup Script for visapics.org production deployment

echo "Setting up SSL certificates for Docker deployment..."

# Create ssl directory
mkdir -p ssl

# Copy certificates from system locations to Docker ssl directory
echo "Copying SSL certificates..."
cp /etc/ssl/certs/visapics.org.crt ssl/cert.pem
cp /etc/ssl/private/visapics.org.key ssl/key.pem

# Set proper permissions
chmod 644 ssl/cert.pem
chmod 600 ssl/key.pem

# Verify certificates
echo "Verifying certificates..."
openssl x509 -in ssl/cert.pem -text -noout | grep -E "(Subject:|Issuer:|Not After)"

echo "SSL certificates setup complete!"
echo "Certificate: ssl/cert.pem"
echo "Private key: ssl/key.pem"

# Test certificate validity
echo "Testing certificate validity..."
openssl x509 -in ssl/cert.pem -noout -dates

echo "Ready to deploy with docker-compose up -d"