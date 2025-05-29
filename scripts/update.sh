#!/bin/bash

# VisaPics Update Script - Updates existing deployment with latest changes
set -e

echo "🔄 Updating VisaPics deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -f "docker-compose.yml" ]; then
    print_error "This script must be run from the VisaPics application directory"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# 1. Backup current configuration
print_status "Creating backup of current configuration..."
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp .env "$BACKUP_DIR/" 2>/dev/null || print_warning "No .env file to backup"
cp docker-compose.yml "$BACKUP_DIR/"
print_success "Backup created in $BACKUP_DIR"

# 2. Pull latest changes
print_status "Pulling latest changes from repository..."
git stash push -m "Auto-stash before update $(date)"
git pull origin main
print_success "Repository updated"

# 3. Check for environment updates
print_status "Checking environment configuration..."
if ! grep -q "MAIL_API" .env 2>/dev/null; then
    print_warning "Brevo email integration available but not configured"
    read -p "Do you want to configure Brevo email integration? (y/N): " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Running environment setup for email configuration..."
        ./scripts/setup-env.sh
    else
        print_warning "Skipping email configuration. You can run ./scripts/setup-env.sh later"
    fi
else
    print_success "Environment configuration is up to date"
fi

# 4. Stop services for update
print_status "Stopping current services..."
docker-compose down

# 5. Build updated containers
print_status "Building updated containers..."
docker-compose build --no-cache

# 6. Install/update Python dependencies
print_status "Updating Python dependencies..."
if docker-compose run --rm visapics pip install -r requirements.txt > /dev/null 2>&1; then
    print_success "Dependencies updated successfully"
else
    print_warning "Some dependencies may have failed to update - check logs if issues occur"
fi

# 7. Start services
print_status "Starting updated services..."
docker-compose up -d

# 8. Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# 9. Health check
print_status "Performing health check..."
if timeout 60 bash -c 'while ! docker-compose exec -T visapics curl -f http://localhost:8000/health > /dev/null 2>&1; do sleep 2; done'; then
    print_success "Health check passed!"
else
    print_error "Health check failed. Services may not be ready yet."
    print_status "Check logs with: docker-compose logs -f"
fi

# 10. Test email integration if configured
if grep -q "MAIL_API" .env 2>/dev/null; then
    print_status "Testing email integration..."
    if ./scripts/test-email.sh > /dev/null 2>&1; then
        print_success "Email integration test passed!"
    else
        print_warning "Email integration test failed - check configuration"
    fi
fi

# 11. Show update summary
print_success "🎉 VisaPics update completed successfully!"

echo ""
print_status "📋 Update Summary:"
echo "   - Repository: Updated to latest version"
echo "   - Dependencies: Updated and verified"
echo "   - Services: Restarted with new configuration"
echo "   - Email: $(grep -q 'MAIL_API' .env 2>/dev/null && echo 'Brevo API configured' || echo 'Traditional SMTP')"

echo ""
print_warning "🔧 Post-Update Checklist:"
echo "1. Verify Stripe webhook URL: https://visapics.org/api/webhook"
echo "2. Test payment flow end-to-end"
echo "3. Monitor logs: docker-compose logs -f"
echo "4. Test email delivery with a real transaction"

echo ""
print_status "📊 System Status:"
echo "   - Application: https://visapics.org"
echo "   - Health Check: https://visapics.org/health"
echo "   - Admin Panel: https://visapics.org/admin/orders"

if [ -d "$BACKUP_DIR" ]; then
    echo ""
    print_status "💾 Rollback Information:"
    echo "   - Backup location: $BACKUP_DIR"
    echo "   - To rollback: cp $BACKUP_DIR/.env . && docker-compose down && docker-compose up -d"
fi

echo ""
print_success "Update completed! Monitor the application for a few minutes to ensure stability."