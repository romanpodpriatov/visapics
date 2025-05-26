#!/bin/bash

# Docker Installation Script for CentOS/RHEL
set -e

echo "🐳 Installing Docker on CentOS/RHEL..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run this script as root or with sudo"
    exit 1
fi

# Remove old Docker versions
echo "🧹 Removing old Docker versions..."
yum remove -y docker \
    docker-client \
    docker-client-latest \
    docker-common \
    docker-latest \
    docker-latest-logrotate \
    docker-logrotate \
    docker-engine \
    podman \
    runc 2>/dev/null || true

# Install required packages
echo "📦 Installing required packages..."
yum install -y yum-utils device-mapper-persistent-data lvm2

# Add Docker repository
echo "📋 Adding Docker repository..."
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker
echo "🐳 Installing Docker CE..."
yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start and enable Docker
echo "🚀 Starting Docker service..."
systemctl start docker
systemctl enable docker

# Install Docker Compose (standalone)
echo "📦 Installing Docker Compose..."
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
echo "Latest Docker Compose version: $DOCKER_COMPOSE_VERSION"

curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create symlink for easy access
ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# Verify installation
echo "✅ Verifying Docker installation..."
docker --version
docker-compose --version

# Test Docker
echo "🧪 Testing Docker..."
docker run --rm hello-world

echo "🎉 Docker installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Add users to docker group: usermod -aG docker username"
echo "2. Log out and back in for group changes to take effect"
echo "3. Test with: docker run hello-world"