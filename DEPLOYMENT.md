# Production Deployment Guide for VisaPics

## Prerequisites

1. **Server Requirements:**
   - Linux server (Ubuntu 20.04+ recommended)
   - Docker and Docker Compose installed
   - At least 4GB RAM (8GB recommended)
   - At least 20GB storage

2. **Domain Setup (Cloudflare):**
   - Domain: `visapics.org` 
   - Point A record to your server IP
   - Enable Cloudflare proxy (orange cloud)

3. **SSL Certificate:**
   - Use Cloudflare Origin certificates or Let's Encrypt

## Quick Deployment Steps

### 1. Clone Repository
```bash
git clone https://github.com/romanpodpriatov/visapics.git
cd visapics
```

### 2. Download AI Models
```bash
# Create model directories
mkdir -p gfpgan/weights models

# Download GFPGAN model (auto-downloads on first run)
# Download BiRefNet model manually and place in models/
wget -O models/BiRefNet-portrait-epoch_150.onnx "YOUR_BIREFNET_MODEL_URL"
```

### 3. Environment Configuration
```bash
# Copy production environment template
cp .env.production .env

# Edit with your actual values
nano .env
```

Required environment variables:
- `SECRET_KEY`: Strong random key for Flask sessions
- `STRIPE_SECRET_KEY`: Your live Stripe secret key
- `STRIPE_PUBLISHABLE_KEY`: Your live Stripe publishable key  
- `STRIPE_WEBHOOK_SECRET`: Your production webhook secret
- Email settings for notifications

### 4. SSL Certificate Setup

#### Option A: Cloudflare Origin Certificate
```bash
mkdir ssl
# Download origin certificate from Cloudflare dashboard
# Save as ssl/cert.pem and ssl/key.pem
```

#### Option B: Let's Encrypt with Certbot
```bash
# Install certbot
sudo apt update && sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d visapics.org -d www.visapics.org

# Copy certificates
sudo cp /etc/letsencrypt/live/visapics.org/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/visapics.org/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/*
```

### 5. Build and Deploy
```bash
# Build the application
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f visapics
```

### 6. Stripe Webhook Configuration

1. Go to Stripe Dashboard > Webhooks
2. Add endpoint: `https://visapics.org/webhook`
3. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `payment_intent.requires_action`
   - `payment_intent.canceled`
4. Copy webhook secret to `.env` file

### 7. Cloudflare Configuration

1. **DNS Settings:**
   - A record: `visapics.org` → Your server IP (Orange cloud ON)
   - A record: `www.visapics.org` → Your server IP (Orange cloud ON)

2. **SSL/TLS Settings:**
   - SSL/TLS mode: Full (strict) if using origin certificates
   - Edge Certificates: Enable HTTPS

3. **Page Rules (Optional):**
   - `www.visapics.org/*` → Forwarding URL to `https://visapics.org/$1`

## Management Commands

### View Logs
```bash
docker-compose logs -f visapics
docker-compose logs nginx
```

### Update Application
```bash
git pull origin main
docker-compose build
docker-compose up -d
```

### Backup Database
```bash
docker-compose exec visapics cp /app/payment_data/payments.db /app/backup_$(date +%Y%m%d).db
docker cp visapics_visapics_1:/app/backup_$(date +%Y%m%d).db ./
```

### Restart Services
```bash
docker-compose restart visapics
docker-compose restart nginx
```

## Monitoring

### Health Check
```bash
curl https://visapics.org/health
```

### System Resources
```bash
docker stats
df -h
free -h
```

## Troubleshooting

### Common Issues

1. **Application won't start:**
   ```bash
   docker-compose logs visapics
   # Check environment variables and model files
   ```

2. **SSL errors:**
   ```bash
   # Verify certificate files
   ls -la ssl/
   # Check nginx configuration
   docker-compose logs nginx
   ```

3. **Payment issues:**
   ```bash
   # Check Stripe configuration
   grep STRIPE .env
   # Verify webhook endpoint in Stripe dashboard
   ```

4. **Model loading errors:**
   ```bash
   # Verify model files exist
   ls -la gfpgan/weights/ models/
   # Check file permissions
   ```

### Performance Optimization

1. **Enable Cloudflare caching** for static assets
2. **Monitor memory usage** - increase if needed
3. **Regular database cleanup** of old orders
4. **Log rotation** to prevent disk space issues

## Security Checklist

- ✅ Use strong random SECRET_KEY
- ✅ Enable HTTPS only (redirect HTTP)
- ✅ Configure rate limiting in nginx
- ✅ Secure file upload validation
- ✅ Regular security updates
- ✅ Monitor application logs
- ✅ Backup database regularly

## Support

For deployment issues, check:
1. Application logs: `docker-compose logs visapics`
2. Nginx logs: `docker-compose logs nginx`  
3. System resources: `docker stats`
4. Network connectivity: `curl https://visapics.org/health`