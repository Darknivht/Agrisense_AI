#!/bin/bash

# AgriSense AI - Production Deployment Script
# This script sets up AgriSense AI on a production server

set -e

echo "🌾 AgriSense AI - Production Deployment Script"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="agrisense-ai"
DOMAIN="agrisense.ai"
ADMIN_EMAIL="admin@agrisense.ai"
DB_NAME="agrisense_ai"
DB_USER="agrisense"
DB_PASSWORD=$(openssl rand -base64 32)

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   log_error "This script should not be run as root for security reasons"
   exit 1
fi

# Check OS
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    log_error "This script is designed for Linux systems"
    exit 1
fi

log_info "Starting AgriSense AI deployment..."

# Update system
log_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
log_info "Installing system dependencies..."
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    certbot \
    python3-certbot-nginx \
    docker.io \
    docker-compose \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    libpq-dev \
    libmagic1 \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    supervisor

log_success "System dependencies installed"

# Configure PostgreSQL
log_info "Configuring PostgreSQL..."
sudo -u postgres psql << EOF
CREATE DATABASE ${DB_NAME};
CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
ALTER USER ${DB_USER} CREATEDB;
\q
EOF

log_success "PostgreSQL configured"

# Configure Redis
log_info "Configuring Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Set up application directory
APP_DIR="/opt/${PROJECT_NAME}"
log_info "Setting up application directory: ${APP_DIR}"

sudo mkdir -p ${APP_DIR}
sudo chown $USER:$USER ${APP_DIR}

# Clone or copy application
if [ -d ".git" ]; then
    log_info "Copying current directory to ${APP_DIR}..."
    cp -r . ${APP_DIR}/
else
    log_info "Please ensure your AgriSense AI code is in ${APP_DIR}"
fi

cd ${APP_DIR}

# Create virtual environment
log_info "Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
log_info "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create environment file
log_info "Creating environment configuration..."
cat > .env << EOF
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$(openssl rand -base64 32)

# Database Configuration
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# AI Service API Keys (CONFIGURE THESE!)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Weather Service
OPENWEATHER_API_KEY=your-openweathermap-api-key-here

# Communication Platform API Keys (CONFIGURE THESE!)
WHATSAPP_ACCESS_TOKEN=your-whatsapp-access-token
WHATSAPP_PHONE_NUMBER_ID=your-whatsapp-phone-number-id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=$(openssl rand -base64 16)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
DISCORD_BOT_TOKEN=your-discord-bot-token
INSTAGRAM_ACCESS_TOKEN=your-instagram-access-token
INSTAGRAM_PAGE_ID=your-instagram-page-id
AT_API_KEY=your-africas-talking-api-key
AT_USERNAME=your-africas-talking-username

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-email-password

# Security
JWT_SECRET_KEY=$(openssl rand -base64 32)

# File Storage
UPLOAD_FOLDER=${APP_DIR}/uploads
VECTORDB_PATH=${APP_DIR}/data/vectordb
MAX_CONTENT_LENGTH=16777216

# Feature Flags
ENABLE_RAG=True
ENABLE_VOICE=True
ENABLE_SMS=True
ENABLE_WHATSAPP=True
ENABLE_TELEGRAM=True
ENABLE_DISCORD=True
ENABLE_WEATHER=True

# Monitoring
SENTRY_DSN=your-sentry-dsn-for-error-tracking
EOF

log_success "Environment configuration created"

# Create necessary directories
log_info "Creating application directories..."
mkdir -p uploads logs data/vectordb static/uploads

# Initialize database
log_info "Initializing database..."
export FLASK_APP=app.py
flask db init || true
flask db migrate -m "Initial migration" || true
flask db upgrade

log_success "Database initialized"

# Set up systemd service
log_info "Creating systemd service..."
sudo tee /etc/systemd/system/${PROJECT_NAME}.service > /dev/null << EOF
[Unit]
Description=AgriSense AI Flask Application
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=${APP_DIR}
Environment=PATH=${APP_DIR}/venv/bin
ExecStart=${APP_DIR}/venv/bin/gunicorn --bind unix:${APP_DIR}/${PROJECT_NAME}.sock --workers 4 --worker-class gevent --timeout 120 app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Set up Celery services
sudo tee /etc/systemd/system/${PROJECT_NAME}-worker.service > /dev/null << EOF
[Unit]
Description=AgriSense AI Celery Worker
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=${APP_DIR}
Environment=PATH=${APP_DIR}/venv/bin
ExecStart=${APP_DIR}/venv/bin/celery -A app.celery worker --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/${PROJECT_NAME}-beat.service > /dev/null << EOF
[Unit]
Description=AgriSense AI Celery Beat
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=${APP_DIR}
Environment=PATH=${APP_DIR}/venv/bin
ExecStart=${APP_DIR}/venv/bin/celery -A app.celery beat --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable ${PROJECT_NAME}
sudo systemctl enable ${PROJECT_NAME}-worker
sudo systemctl enable ${PROJECT_NAME}-beat

log_success "Systemd services configured"

# Configure Nginx
log_info "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/${PROJECT_NAME} > /dev/null << EOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:${APP_DIR}/${PROJECT_NAME}.sock;
    }

    location /static/ {
        alias ${APP_DIR}/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    client_max_body_size 16M;
}
EOF

sudo ln -sf /etc/nginx/sites-available/${PROJECT_NAME} /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

log_success "Nginx configured"

# Start services
log_info "Starting services..."
sudo systemctl start ${PROJECT_NAME}
sudo systemctl start ${PROJECT_NAME}-worker
sudo systemctl start ${PROJECT_NAME}-beat
sudo systemctl reload nginx

# Obtain SSL certificate
log_info "Obtaining SSL certificate..."
sudo certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} --non-interactive --agree-tos --email ${ADMIN_EMAIL} || log_warning "SSL certificate generation failed. You can run 'sudo certbot --nginx -d ${DOMAIN}' manually later."

# Set up automatic SSL renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -

# Create log rotation
sudo tee /etc/logrotate.d/${PROJECT_NAME} > /dev/null << EOF
${APP_DIR}/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
    postrotate
        systemctl reload ${PROJECT_NAME}
    endscript
}
EOF

# Set up firewall
log_info "Configuring firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

log_success "Firewall configured"

# Create backup script
log_info "Creating backup script..."
sudo tee /usr/local/bin/${PROJECT_NAME}-backup > /dev/null << EOF
#!/bin/bash
BACKUP_DIR="/opt/backups/${PROJECT_NAME}"
DATE=\$(date +%Y%m%d_%H%M%S)

mkdir -p \${BACKUP_DIR}

# Database backup
pg_dump ${DB_NAME} | gzip > \${BACKUP_DIR}/db_\${DATE}.sql.gz

# Application files backup
tar -czf \${BACKUP_DIR}/app_\${DATE}.tar.gz -C ${APP_DIR} uploads data logs .env

# Keep only last 7 days of backups
find \${BACKUP_DIR} -name "*.gz" -mtime +7 -delete
find \${BACKUP_DIR} -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: \${DATE}"
EOF

sudo chmod +x /usr/local/bin/${PROJECT_NAME}-backup

# Schedule daily backups
echo "0 2 * * * /usr/local/bin/${PROJECT_NAME}-backup" | sudo crontab -

log_success "Backup system configured"

# Final status check
log_info "Checking service status..."
sudo systemctl status ${PROJECT_NAME} --no-pager
sudo systemctl status nginx --no-pager

echo ""
echo "🎉 AgriSense AI deployment completed!"
echo "======================================"
echo ""
echo "📋 Deployment Summary:"
echo "• Application URL: https://${DOMAIN}"
echo "• Application directory: ${APP_DIR}"
echo "• Database: ${DB_NAME}"
echo "• SSL: Automatically configured with Let's Encrypt"
echo "• Services: ${PROJECT_NAME}, ${PROJECT_NAME}-worker, ${PROJECT_NAME}-beat"
echo ""
echo "🔧 Next Steps:"
echo "1. Configure API keys in ${APP_DIR}/.env"
echo "2. Restart services: sudo systemctl restart ${PROJECT_NAME}"
echo "3. Test all integrations (WhatsApp, Telegram, etc.)"
echo "4. Set up monitoring and alerts"
echo ""
echo "📝 Important Files:"
echo "• Environment: ${APP_DIR}/.env"
echo "• Logs: ${APP_DIR}/logs/"
echo "• Nginx config: /etc/nginx/sites-available/${PROJECT_NAME}"
echo "• Systemd services: /etc/systemd/system/${PROJECT_NAME}*"
echo ""
echo "🔒 Security:"
echo "• Firewall configured (SSH + HTTP/HTTPS only)"
echo "• SSL certificate auto-renewal enabled"
echo "• Daily backups scheduled"
echo ""
echo "📞 Support:"
echo "• Documentation: Check README.md"
echo "• Logs: journalctl -u ${PROJECT_NAME}"
echo "• Backup script: /usr/local/bin/${PROJECT_NAME}-backup"
echo ""
log_success "Deployment completed successfully!"

# Prompt for API key configuration
log_warning "IMPORTANT: Configure your API keys in ${APP_DIR}/.env before using the application!"