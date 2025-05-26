# VisaPics - AI-Powered Visa Photo Processing Service

🤖 **Automated visa and passport photo processing with Stripe payment integration**

Transform any portrait into compliant visa/passport photos for 190+ countries using advanced AI models including BiRefNet for precise background removal and GFPGAN for facial enhancement.

## 🌟 Features

- **AI-Powered Processing**: BiRefNet + GFPGAN for professional results
- **190+ Country Support**: Comprehensive visa/passport photo specifications
- **Stripe Payment Integration**: Secure payment processing with modern Payment Element
- **Real-time Updates**: WebSocket-based progress tracking
- **Professional Quality**: Millimeter-precision measurements and compliance
- **Cloudflare Ready**: Optimized for production deployment

## 🚀 Quick Production Deployment

### One-Command Deployment
```bash
# Clone and deploy in one command
curl -sSL https://raw.githubusercontent.com/romanpodpriatov/visapics/main/deploy.sh | sudo bash
```

### Manual Deployment
```bash
# 1. Clone repository
git clone https://github.com/romanpodpriatov/visapics.git
cd visapics

# 2. Run deployment script
sudo ./deploy.sh
```

The deployment script will automatically:
- ✅ Install Docker and dependencies
- ✅ Setup SSL certificates (Cloudflare/Let's Encrypt/Self-signed)
- ✅ Configure environment variables interactively
- ✅ Download AI models (~1.5GB)
- ✅ Build and start services
- ✅ Setup monitoring and backups
- ✅ Perform health checks

## ⚙️ Configuration

### Required Environment Variables
```bash
# Stripe (get from https://dashboard.stripe.com/apikeys)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email notifications
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Stripe Webhook Setup
1. Go to [Stripe Webhooks](https://dashboard.stripe.com/webhooks)
2. Add endpoint: `https://visapics.org/webhook`
3. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed` 
   - `payment_intent.requires_action`
   - `payment_intent.canceled`

## 🛠️ Management Commands

```bash
# View logs
docker-compose logs -f visapics

# Health check
./scripts/health-check.sh

# Update application
./scripts/update.sh

# Manual backup
./scripts/backup.sh

# SSL certificate check
./scripts/ssl-check.sh
```

## 📊 Monitoring

The deployment includes automated monitoring:
- 🏥 Health checks every 5 minutes
- 🗄️ Daily backups at 2 AM
- 🧹 Weekly cleanup (Sunday 3 AM)
- 🔒 Daily SSL certificate checks
- 📝 Log rotation (30 days retention)

## 🏗️ Architecture

### Core Components
- **Flask Application**: Main web service with SocketIO
- **Nginx**: Reverse proxy with SSL termination
- **AI Models**: BiRefNet (background removal) + GFPGAN (enhancement)
- **Stripe Integration**: Payment processing with webhooks
- **SQLite Database**: Order management and tracking

### Processing Pipeline
1. **Upload & Validation** → Document type selection
2. **AI Processing** → BiRefNet background removal
3. **Face Enhancement** → GFPGAN facial improvement  
4. **Compliance Check** → Measurements and positioning
5. **Preview Generation** → Watermarked previews
6. **Payment Flow** → Stripe Payment Element
7. **Final Download** → High-quality results

## 🔧 Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your keys

# Download models
./scripts/download-models.sh

# Run application
python main.py
```

### Testing
```bash
# Run tests
python -m unittest discover -s tests -v

# Test specific component
python -m unittest tests.test_main
```

## 📝 API Endpoints

- `GET /` - Main application interface
- `POST /upload` - Image upload and processing
- `GET /health` - Health check endpoint
- `POST /api/create-payment-intent` - Payment processing
- `POST /webhook` - Stripe webhook handler
- `GET /admin/orders` - Order management (admin)

## 🔒 Security Features

- 🛡️ Rate limiting (nginx)
- 🔒 HTTPS enforcement  
- 🔐 Secure headers
- 🗂️ File upload validation
- 💳 Stripe security compliance
- 👤 User session management

## 📋 Requirements

### System Requirements
- Linux server (Ubuntu 20.04+ recommended)
- 4GB+ RAM (8GB recommended for AI models)
- 20GB+ storage
- Docker & Docker Compose

### AI Models (~1.5GB total)
- BiRefNet: Background removal (930MB)
- GFPGAN: Face enhancement (332MB) 
- Detection models: Face detection (104MB + 81MB)

## 🌍 Domain Configuration

The application is configured for `visapics.org` with Cloudflare:
- 🌐 DNS: A records pointing to server IP
- 🔒 SSL: Origin certificates or Let's Encrypt
- ⚡ CDN: Cloudflare proxy enabled

## 📞 Support

### Troubleshooting
- Check logs: `docker-compose logs visapics`
- Health status: `./scripts/health-check.sh`
- System resources: `docker stats`

### Common Issues
1. **Models not loading**: Run `./scripts/download-models.sh`
2. **SSL errors**: Check certificate files in `ssl/` directory
3. **Payment issues**: Verify Stripe webhook configuration
4. **Performance**: Monitor memory usage, increase if needed

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

**Live Demo**: [https://visapics.org](https://visapics.org)

**Repository**: [https://github.com/romanpodpriatov/visapics](https://github.com/romanpodpriatov/visapics)