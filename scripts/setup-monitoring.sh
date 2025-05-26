#!/bin/bash

# Monitoring and Backup Setup Script for VisaPics
set -e

echo "📊 Setting up monitoring and backup..."

# Create monitoring directory
mkdir -p /opt/visapics/monitoring
mkdir -p /opt/visapics/backups

# 1. Log rotation setup
echo "📝 Setting up log rotation..."
cat > /etc/logrotate.d/visapics << 'EOF'
/opt/visapics/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    su visapics visapics
}
EOF

# Create logs directory
mkdir -p logs
chown visapics:visapics logs

echo "✅ Log rotation configured"

# 2. System monitoring cron jobs
echo "⏰ Setting up monitoring cron jobs..."

# Health check every 5 minutes
crontab -l 2>/dev/null | grep -v "visapics-health" > /tmp/crontab_temp || true
echo "*/5 * * * * cd /opt/visapics && ./scripts/health-check.sh >> logs/health.log 2>&1 # visapics-health" >> /tmp/crontab_temp

# Daily backup at 2 AM
echo "0 2 * * * cd /opt/visapics && ./scripts/backup.sh >> logs/backup.log 2>&1 # visapics-backup" >> /tmp/crontab_temp

# Weekly cleanup at 3 AM Sunday
echo "0 3 * * 0 cd /opt/visapics && ./scripts/cleanup.sh >> logs/cleanup.log 2>&1 # visapics-cleanup" >> /tmp/crontab_temp

# SSL certificate check daily at 6 AM
echo "0 6 * * * cd /opt/visapics && ./scripts/ssl-check.sh >> logs/ssl.log 2>&1 # visapics-ssl" >> /tmp/crontab_temp

crontab /tmp/crontab_temp
rm /tmp/crontab_temp

echo "✅ Cron jobs configured"

# 3. Backup script
cat > scripts/backup.sh << 'EOF'
#!/bin/bash

# VisaPics Backup Script
set -e

BACKUP_DIR="/opt/visapics/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="visapics_backup_$DATE"

echo "🗄️  Starting backup: $BACKUP_NAME"

# Create backup directory
mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

# Backup database
echo "📊 Backing up database..."
docker-compose exec -T visapics cp /app/payment_data/payments.db /tmp/backup_db.db
docker cp $(docker-compose ps -q visapics):/tmp/backup_db.db "$BACKUP_DIR/$BACKUP_NAME/payments.db"

# Backup configuration
echo "⚙️  Backing up configuration..."
cp .env "$BACKUP_DIR/$BACKUP_NAME/"
cp docker-compose.yml "$BACKUP_DIR/$BACKUP_NAME/"
cp -r ssl "$BACKUP_DIR/$BACKUP_NAME/" 2>/dev/null || true

# Backup processed images (last 7 days)
echo "🖼️  Backing up recent processed images..."
find processed -type f -mtime -7 -exec cp {} "$BACKUP_DIR/$BACKUP_NAME/" \; 2>/dev/null || true

# Compress backup
echo "🗜️  Compressing backup..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

# Remove old backups (keep last 7 days)
find "$BACKUP_DIR" -name "visapics_backup_*.tar.gz" -mtime +7 -delete

echo "✅ Backup completed: ${BACKUP_NAME}.tar.gz"
ls -lh "$BACKUP_DIR/${BACKUP_NAME}.tar.gz"
EOF

chmod +x scripts/backup.sh

# 4. Cleanup script
cat > scripts/cleanup.sh << 'EOF'
#!/bin/bash

# VisaPics Cleanup Script
set -e

echo "🧹 Starting cleanup..."

# Clean old uploaded files (older than 1 day)
echo "🗑️  Cleaning old uploads..."
find uploads -type f -mtime +1 -delete 2>/dev/null || true

# Clean old processed files (older than 7 days)
echo "🗑️  Cleaning old processed files..."
find processed -type f -mtime +7 -delete 2>/dev/null || true

# Clean old preview files (older than 1 day)
echo "🗑️  Cleaning old previews..."
find previews -type f -mtime +1 -delete 2>/dev/null || true

# Clean Docker logs
echo "🗑️  Cleaning Docker logs..."
docker system prune -f

# Clean old database entries (older than 90 days)
echo "🗑️  Cleaning old database entries..."
docker-compose exec -T visapics python3 -c "
import sqlite3
import datetime

conn = sqlite3.connect('/app/payment_data/payments.db')
cutoff_date = datetime.datetime.now() - datetime.timedelta(days=90)
cursor = conn.cursor()
cursor.execute('DELETE FROM orders WHERE created_at < ?', (cutoff_date.isoformat(),))
deleted = cursor.rowcount
conn.commit()
conn.close()
print(f'Deleted {deleted} old database entries')
"

echo "✅ Cleanup completed"
EOF

chmod +x scripts/cleanup.sh

# 5. SSL certificate check script
cat > scripts/ssl-check.sh << 'EOF'
#!/bin/bash

# SSL Certificate Check Script
set -e

echo "🔒 Checking SSL certificate..."

if [ -f "ssl/cert.pem" ]; then
    # Check certificate expiration
    EXPIRY_DATE=$(openssl x509 -in ssl/cert.pem -noout -enddate | cut -d= -f2)
    EXPIRY_TIMESTAMP=$(date -d "$EXPIRY_DATE" +%s)
    CURRENT_TIMESTAMP=$(date +%s)
    DAYS_UNTIL_EXPIRY=$(( (EXPIRY_TIMESTAMP - CURRENT_TIMESTAMP) / 86400 ))
    
    echo "📅 Certificate expires: $EXPIRY_DATE ($DAYS_UNTIL_EXPIRY days)"
    
    if [ $DAYS_UNTIL_EXPIRY -lt 30 ]; then
        echo "⚠️  Certificate expires in $DAYS_UNTIL_EXPIRY days - renewal needed!"
        # You can add notification logic here (email, webhook, etc.)
    else
        echo "✅ Certificate is valid for $DAYS_UNTIL_EXPIRY days"
    fi
else
    echo "❌ SSL certificate not found!"
fi
EOF

chmod +x scripts/ssl-check.sh

# 6. Update script
cat > scripts/update.sh << 'EOF'
#!/bin/bash

# VisaPics Update Script
set -e

echo "🔄 Updating VisaPics..."

# Backup before update
echo "🗄️  Creating backup before update..."
./scripts/backup.sh

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Rebuild containers
echo "🔨 Rebuilding containers..."
docker-compose build

# Restart services
echo "🔄 Restarting services..."
docker-compose down
docker-compose up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Health check
echo "🏥 Running health check..."
./scripts/health-check.sh

echo "✅ Update completed successfully!"
EOF

chmod +x scripts/update.sh

# Set proper ownership
chown -R visapics:visapics /opt/visapics 2>/dev/null || true

echo "📊 Monitoring setup completed!"
echo ""
echo "📋 Monitoring Features:"
echo "  ✅ Automated health checks every 5 minutes"
echo "  ✅ Daily database backups at 2 AM"
echo "  ✅ Weekly cleanup at 3 AM Sunday"
echo "  ✅ Daily SSL certificate checks at 6 AM"
echo "  ✅ Log rotation (30 days retention)"
echo ""
echo "🛠️  Available scripts:"
echo "  ./scripts/health-check.sh  - Manual health check"
echo "  ./scripts/backup.sh        - Manual backup"
echo "  ./scripts/cleanup.sh       - Manual cleanup"
echo "  ./scripts/ssl-check.sh     - Check SSL certificate"
echo "  ./scripts/update.sh        - Update application"
echo ""
echo "📁 Monitoring data:"
echo "  Logs: /opt/visapics/logs/"
echo "  Backups: /opt/visapics/backups/"