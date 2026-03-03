#!/bin/bash
# XANENE OPS - Quick Production Deployment Script
# Run this on your Ubuntu server

set -e

echo "=========================================="
echo "  XANENE OPS - Production Deployment"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run with sudo${NC}"
    exit 1
fi

# Configuration
APP_DIR="/opt/xanene_ops"
read -p "Enter your domain (e.g., xanene.com): " DOMAIN
read -p "Enter email for SSL certificate: " EMAIL

echo ""
echo -e "${YELLOW}Step 1: Installing Dependencies${NC}"
apt update && apt upgrade -y
apt install -y docker.io docker-compose certbot python3-certbot-nginx git curl

echo ""
echo -e "${YELLOW}Step 2: Setting Up Docker${NC}"
systemctl enable docker
systemctl start docker

echo ""
echo -e "${YELLOW}Step 3: Creating Application Directory${NC}"
mkdir -p $APP_DIR/nginx/ssl
chown -R $SUDO_USER:$SUDO_USER $APP_DIR
chmod 755 $APP_DIR

echo ""
echo -e "${YELLOW}Step 4: Generating Secure Passwords${NC}"
DB_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

echo -e "${GREEN}✓ Database Password: $DB_PASSWORD${NC}"
echo -e "${GREEN}✓ Secret Key: $SECRET_KEY${NC}"
echo ""
echo "⚠️  SAVE THESE VALUES! You'll need them later."
echo ""

# Create .env file
cat > $APP_DIR/.env << EOF
# Application
APP_NAME=XANENE OPS
APP_VERSION=1.0.0
DEBUG=false

# Database
DATABASE_URL=postgresql://xanene:$DB_PASSWORD@db:5432/xanene_ops

# JWT Authentication
SECRET_KEY=$SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS Origins
CORS_ORIGINS=["https://$DOMAIN","https://www.$DOMAIN"]

# PostgreSQL
DB_PASSWORD=$DB_PASSWORD
POSTGRES_DB=xanene_ops
POSTGRES_USER=xanene
EOF

chown $SUDO_USER:$SUDO_USER $APP_DIR/.env
chmod 600 $APP_DIR/.env

echo -e "${GREEN}✓ Environment file created${NC}"

echo ""
echo -e "${YELLOW}Step 5: Copying Application Files${NC}"
echo "Please copy your application files to $APP_DIR"
echo "Or clone from git repository."
echo ""
read -p "Press Enter when files are ready..."

echo ""
echo -e "${YELLOW}Step 6: Configuring Nginx${NC}"
# Update nginx config with domain
if [ -f "$APP_DIR/nginx/nginx.prod.conf" ]; then
    sed -i "s/your-domain.com/$DOMAIN/g" $APP_DIR/nginx/nginx.prod.conf
    cp $APP_DIR/nginx/nginx.prod.conf $APP_DIR/nginx/nginx.conf
    echo -e "${GREEN}✓ Nginx configured${NC}"
else
    echo -e "${RED}nginx.prod.conf not found!${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 7: Obtaining SSL Certificate${NC}"

# Stop nginx if running
docker compose -f $APP_DIR/docker-compose.prod.yml down 2>/dev/null || true

# Get SSL certificate
certbot certonly --standalone \
    -d $DOMAIN \
    -d www.$DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --non-interactive

# Copy certificates
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $APP_DIR/nginx/ssl/
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $APP_DIR/nginx/ssl/
chmod 600 $APP_DIR/nginx/ssl/*.pem

echo -e "${GREEN}✓ SSL certificate installed${NC}"

echo ""
echo -e "${YELLOW}Step 8: Starting Application${NC}"
cd $APP_DIR
docker compose -f docker-compose.prod.yml up -d --build

echo ""
echo -e "${YELLOW}Step 9: Verifying Deployment${NC}"
sleep 10

if docker compose ps | grep -q "xanene_app.*Up"; then
    echo -e "${GREEN}✓ Application is running${NC}"
else
    echo -e "${RED}✗ Application failed to start${NC}"
    docker compose logs app
    exit 1
fi

if docker compose ps | grep -q "xanene_db.*Up"; then
    echo -e "${GREEN}✓ Database is running${NC}"
else
    echo -e "${RED}✗ Database failed to start${NC}"
    exit 1
fi

if docker compose ps | grep -q "xanene_nginx.*Up"; then
    echo -e "${GREEN}✓ Nginx is running${NC}"
else
    echo -e "${RED}✗ Nginx failed to start${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}  Deployment Complete! 🎉${NC}"
echo "=========================================="
echo ""
echo "Your application is now live at:"
echo -e "${GREEN}  https://$DOMAIN${NC}"
echo ""
echo "Default admin credentials:"
echo "  Email: admin@xanene.com"
echo "  Password: admin123"
echo ""
echo -e "${RED}⚠️  CHANGE THE PASSWORD IMMEDIATELY!${NC}"
echo ""
echo "Useful commands:"
echo "  cd $APP_DIR"
echo "  docker compose logs -f     # View logs"
echo "  docker compose restart     # Restart services"
echo "  docker compose down        # Stop services"
echo ""
echo "Backup command:"
echo "  docker compose exec db pg_dump -U xanene xanene_ops > backup.sql"
echo ""
echo "=========================================="
