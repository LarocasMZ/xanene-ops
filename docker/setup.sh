#!/bin/bash
# XANENE OPS - Ubuntu Server Setup Script
# Run this script on a fresh Ubuntu 20.04+ server

set -e

echo "🚀 XANENE OPS - Server Setup"
echo "============================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (sudo)$NC"
    exit 1
fi

# Configuration
APP_USER="xanene"
APP_DIR="/opt/xanene_ops"
DB_NAME="xanene_ops"
DB_USER="xanene"

echo -e "${YELLOW}Step 1: System Update${NC}"
apt update && apt upgrade -y

echo -e "${YELLOW}Step 2: Install Dependencies${NC}"
apt install -y \
    postgresql postgresql-contrib \
    python3.11 python3.11-venv python3-pip \
    nginx \
    certbot python3-certbot-nginx \
    git curl wget \
    build-essential libpq-dev

echo -e "${YELLOW}Step 3: Setup PostgreSQL${NC}"
read -p "Enter database password for '$DB_USER': " -s DB_PASSWORD
echo

sudo -u postgres psql << EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
\\c $DB_NAME
GRANT ALL ON SCHEMA public TO $DB_USER;
EOF

echo -e "${GREEN}✓ Database created${NC}"

echo -e "${YELLOW}Step 4: Create Application User${NC}"
if ! id "$APP_USER" &>/dev/null; then
    useradd -m -s /bin/bash $APP_USER
    echo -e "${GREEN}✓ User '$APP_USER' created${NC}"
else
    echo -e "${GREEN}✓ User '$APP_USER' already exists${NC}"
fi

echo -e "${YELLOW}Step 5: Setup Application Directory${NC}"
mkdir -p $APP_DIR
chown $APP_USER:$APP_USER $APP_DIR
chmod 755 $APP_DIR

echo -e "${YELLOW}Step 6: Setup Python Virtual Environment${NC}"
sudo -u $APP_USER bash << EOF
cd $APP_DIR
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
EOF

echo -e "${GREEN}✓ Virtual environment created${NC}"

echo -e "${YELLOW}Step 7: Configure Firewall${NC}"
if command -v ufw &> /dev/null; then
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
    echo -e "${GREEN}✓ Firewall configured${NC}"
else
    echo -e "${YELLOW}⚠ UFW not installed, skipping firewall${NC}"
fi

echo -e "${YELLOW}Step 8: Create Environment File${NC}"
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

cat > $APP_DIR/.env << EOF
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
SECRET_KEY=$SECRET_KEY
DEBUG=false
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=["http://localhost:8000"]
EOF

chown $APP_USER:$APP_USER $APP_DIR/.env
chmod 600 $APP_DIR/.env
echo -e "${GREEN}✓ Environment file created${NC}"

echo -e "${YELLOW}Step 9: Setup Nginx Configuration${NC}"
cat > /etc/nginx/sites-available/xanene_ops << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/xanene_ops /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
echo -e "${GREEN}✓ Nginx configured${NC}"

echo -e "${YELLOW}Step 10: Setup Systemd Service${NC}"
cat > /etc/systemd/system/xanene-ops.service << EOF
[Unit]
Description=XANENE OPS
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable xanene-ops
echo -e "${GREEN}✓ Systemd service created${NC}"

echo ""
echo "============================================"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Copy your application files to: $APP_DIR"
echo "2. Install Python dependencies:"
echo "   sudo -u $APP_USER bash -c 'cd $APP_DIR && source venv/bin/activate && pip install -r requirements.txt'"
echo "3. Run database migrations:"
echo "   sudo -u postgres psql $DB_NAME < $APP_DIR/docker/schema.sql"
echo "4. Start the application:"
echo "   sudo systemctl start xanene-ops"
echo "5. Setup SSL (after DNS is configured):"
echo "   sudo certbot --nginx -d your-domain.com"
echo ""
echo "Default login: admin@xanene.com / admin123"
echo "============================================"
