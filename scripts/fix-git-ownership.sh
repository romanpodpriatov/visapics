#!/bin/bash

# Fix Git ownership issues for VisaPics
set -e

echo "🔧 Fixing Git ownership issues..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run this script as root or with sudo"
    exit 1
fi

APP_DIR="/opt/visapics"

# Add safe directory for Git
echo "📁 Adding safe directory for Git..."
git config --global --add safe.directory $APP_DIR

# Fix ownership of entire directory
echo "👤 Setting correct ownership..."
chown -R visapics:visapics $APP_DIR

# Fix Git directory permissions
echo "🔒 Fixing Git directory permissions..."
if [ -d "$APP_DIR/.git" ]; then
    chmod -R 755 $APP_DIR/.git
    chown -R visapics:visapics $APP_DIR/.git
fi

# Test Git access
echo "🧪 Testing Git access..."
if cd $APP_DIR && su - visapics -c "cd $APP_DIR && git status" >/dev/null 2>&1; then
    echo "✅ Git ownership fixed successfully!"
else
    echo "❌ Git access test failed"
    exit 1
fi

echo "🎉 Git ownership setup completed!"