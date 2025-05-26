#!/bin/bash

# Fix Docker permissions for VisaPics deployment
set -e

echo "🔧 Fixing Docker permissions..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run this script as root or with sudo"
    exit 1
fi

# Create visapics user if doesn't exist
if ! id "visapics" &>/dev/null; then
    echo "👤 Creating visapics user..."
    useradd -m -s /bin/bash visapics
fi

# Add user to docker group
echo "🐳 Adding visapics to docker group..."
usermod -aG docker visapics

# Create Docker directory for user
echo "📁 Setting up Docker directory..."
mkdir -p /home/visapics/.docker
chown visapics:visapics /home/visapics/.docker

# Set proper ownership of application directory
echo "📂 Setting application directory permissions..."
chown -R visapics:visapics /opt/visapics

# Restart Docker to apply group changes
echo "🔄 Restarting Docker service..."
systemctl restart docker

# Test Docker access
echo "🧪 Testing Docker access..."
if su - visapics -c "docker ps" >/dev/null 2>&1; then
    echo "✅ Docker permissions fixed successfully!"
else
    echo "❌ Docker permission test failed"
    exit 1
fi

echo "🎉 Permissions setup completed!"