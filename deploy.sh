#!/bin/bash

# VisaPics Production Deployment Script
# Run this script on your production server to automatically deploy the application

set -e  # Exit on any error

echo "🚀 Starting VisaPics Production Deployment..."

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

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root or with sudo"
    exit 1
fi

# 1. System Dependencies
print_status "Installing system dependencies..."
if command -v apt &> /dev/null; then
    apt update
    apt install -y curl wget git docker.io docker-compose openssl
elif command -v yum &> /dev/null; then
    yum update -y
    yum install -y curl wget git openssl
    
    # Install Docker for CentOS/RHEL
    print_status "Installing Docker for CentOS/RHEL..."
    yum install -y yum-utils
    yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin
    
    # Install Docker Compose
    print_status "Installing Docker Compose..."
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    systemctl start docker
    systemctl enable docker
else
    print_error "Unsupported package manager. Please install Docker and Docker Compose manually."
    exit 1
fi

# Start Docker service
systemctl start docker
systemctl enable docker

print_success "System dependencies installed"

# 2. Create application user
print_status "Creating application user..."
if ! id "visapics" &>/dev/null; then
    useradd -m -s /bin/bash visapics
    print_success "User 'visapics' created"
else
    print_warning "User 'visapics' already exists"
fi

# Add user to docker group and setup Docker directory
usermod -aG docker visapics
mkdir -p /home/visapics/.docker
chown visapics:visapics /home/visapics/.docker
print_success "User added to docker group"

# 3. Create application directory
APP_DIR="/opt/visapics"
print_status "Setting up application directory at $APP_DIR..."
mkdir -p $APP_DIR
cd $APP_DIR

# 4. Fix Git ownership and clone/update repository
print_status "Setting up Git repository..."
git config --global --add safe.directory $APP_DIR

if [ ! -d ".git" ]; then
    print_status "Cloning repository..."
    git clone https://github.com/romanpodpriatov/visapics.git .
else
    print_status "Updating repository..."
    git pull origin main
fi

# Fix ownership after Git operations
chown -R visapics:visapics $APP_DIR

print_success "Repository ready"

# 5. SSL Certificate Setup
print_status "Setting up SSL certificates..."
./scripts/setup-ssl.sh

# 6. Environment Configuration
print_status "Setting up environment configuration..."
./scripts/setup-env.sh

# 7. Download AI Models
print_status "Downloading AI models..."
./scripts/download-models.sh

# 8. Set proper permissions
print_status "Setting file permissions..."
chown -R visapics:visapics $APP_DIR
chmod +x scripts/*.sh

# 9. Restart Docker to apply group changes
print_status "Restarting Docker service..."
systemctl restart docker
sleep 5

# 10. Build and deploy production and development environments
print_status "Building Docker containers..."
cd $APP_DIR
docker-compose build

print_status "Starting production services..."
docker-compose up -d

print_status "Starting development services..."
docker-compose -f docker-compose.dev.yml up -d

# 11. Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# 12. Health check
print_status "Performing health check..."
if cd $APP_DIR && ./scripts/health-check.sh; then
    print_success "Health check passed!"
else
    print_error "Health check failed. Check logs with: docker-compose logs"
    exit 1
fi

# 13. Setup monitoring and backup
print_status "Setting up monitoring and backup..."
cd $APP_DIR && ./scripts/setup-monitoring.sh

print_success "🎉 VisaPics deployment completed successfully!"
print_status "Production environment: https://visapics.org"
print_status "Development environment: https://dev.visapics.org (ports 8080/8443)"
print_status "Admin panel: https://visapics.org/admin/orders"
print_status "Health check: https://visapics.org/health"

echo ""
print_warning "Next steps:"
echo "1. Configure your Stripe webhook URL: https://visapics.org/api/webhook"
echo "2. Test payment flow with Brevo email delivery"
echo "3. Monitor logs: docker-compose logs -f"
echo "4. Setup SSL certificate auto-renewal if using Let's Encrypt"
echo "5. Test email delivery: check Brevo logs at https://app.brevo.com/sms-campaign/logs"

echo ""
print_status "📋 Useful commands:"
echo "  - View production logs: docker-compose logs -f"
echo "  - View dev logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "  - Restart production: docker-compose restart"
echo "  - Restart dev: docker-compose -f docker-compose.dev.yml restart"
echo "  - Update: ./scripts/update.sh"
echo "  - Test email: ./scripts/test-email.sh"
echo "  - Environment: ./scripts/setup-env.sh"

echo ""
print_status "📊 Monitoring:"
echo "  - Application logs: docker-compose logs visapics"
echo "  - Email delivery: https://app.brevo.com/sms-campaign/logs"
echo "  - Stripe dashboard: https://dashboard.stripe.com/webhooks"