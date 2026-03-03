# 🚀 XANENE OPS - Production Deployment Guide

## Pre-Deployment Checklist

- [ ] Domain name purchased and DNS configured
- [ ] Ubuntu server (20.04+) with sudo access
- [ ] Docker and Docker Compose installed
- [ ] SSL certificate (Let's Encrypt)
- [ ] Secure passwords generated
- [ ] Environment variables configured

---

## Step 1: Server Setup

### Install Docker (if not installed)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

---

## Step 2: Application Setup

### Create Application Directory

```bash
sudo mkdir -p /opt/xanene_ops
sudo chown $USER:$USER /opt/xanene_ops
cd /opt/xanene_ops
```

### Copy Application Files

```bash
# Copy from your development machine
scp -r /path/to/xenene_to.do/* user@your-server:/opt/xanene_ops/

# Or clone from git repository
# git clone <your-repo-url> /opt/xanene_ops
```

---

## Step 3: Generate Secure Secrets

```bash
# Generate secure database password
DB_PASSWORD=$(openssl rand -base64 32)
echo "DB_PASSWORD: $DB_PASSWORD"

# Generate secure JWT secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "SECRET_KEY: $SECRET_KEY"
```

**Save these values!** You'll need them in the next step.

---

## Step 4: Configure Environment

```bash
cd /opt/xanene_ops
cp .env.example .env
nano .env
```

### Update .env with your values:

```bash
# Application
APP_NAME=XANENE OPS
APP_VERSION=1.0.0
DEBUG=false

# Database (use the generated password)
DATABASE_URL=postgresql://xanene:YOUR_GENERATED_DB_PASSWORD@db:5432/xanene_ops

# JWT Authentication (use the generated key)
SECRET_KEY=YOUR_GENERATED_SECRET_KEY_MIN_32_CHARACTERS

# Token expiration
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS Origins - IMPORTANT: Add your domain
CORS_ORIGINS=["https://your-domain.com","https://www.your-domain.com"]

# PostgreSQL
DB_PASSWORD=YOUR_GENERATED_DB_PASSWORD
POSTGRES_DB=xanene_ops
POSTGRES_USER=xanene
```

---

## Step 5: Configure Domain

### Update Nginx Configuration

```bash
nano nginx/nginx.conf
```

Find and replace `server_name _;` with your actual domain:

```nginx
server_name your-domain.com www.your-domain.com;
```

---

## Step 6: SSL Certificate (Let's Encrypt)

### Install Certbot

```bash
sudo apt install certbot -y
```

### Create SSL Directory

```bash
sudo mkdir -p /opt/xanene_ops/nginx/ssl
```

### Get SSL Certificate

**Option A: Standalone (port 80 must be free)**

```bash
# Stop nginx temporarily
docker compose down

# Get certificate
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /opt/xanene_ops/nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem /opt/xanene_ops/nginx/ssl/

# Set permissions
sudo chown -R 101:101 /opt/xanene_ops/nginx/ssl
sudo chmod 600 /opt/xanene_ops/nginx/ssl/*.pem
```

**Option B: Webroot (if you have existing web server)**

```bash
sudo certbot certonly --webroot -w /var/www/html -d your-domain.com -d www.your-domain.com
```

### Update Nginx for HTTPS

The nginx.conf already has HTTPS configuration. After getting certificates:

```bash
# Update docker-compose.yml to enable HTTPS
nano docker-compose.yml
```

Make sure nginx volumes include SSL:

```yaml
volumes:
  - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
  - ./nginx/ssl:/etc/nginx/ssl:ro
  - ./frontend:/var/www/frontend:ro
```

---

## Step 7: Deploy Application

### Start All Services

```bash
cd /opt/xanene_ops
docker compose up -d --build
```

### Verify Deployment

```bash
# Check all containers are running
docker compose ps

# View logs
docker compose logs -f app
docker compose logs -f nginx
docker compose logs -f db
```

### Test Application

```bash
# Test locally
curl http://localhost/health

# Test from browser
# https://your-domain.com
# https://your-domain.com/health
```

---

## Step 8: Database Initialization

The database is automatically created on first run. To verify:

```bash
# Check database is running
docker compose exec db psql -U xanene -c "\dt"

# Check tables exist
docker compose exec db psql -U xanene -d xanene_ops -c "SELECT * FROM users;"
```

**Default Admin Account:**
- Email: `admin@xanene.com`
- Password: `admin123`

**⚠️ CHANGE THIS IMMEDIATELY after first login!**

---

## Step 9: Setup Auto-Renewal for SSL

```bash
# Create renewal script
sudo nano /etc/cron.d/certbot-renewal
```

Add this line:

```bash
0 3 * * * root certbot renew --quiet && docker compose -f /opt/xanene_ops/docker-compose.yml restart nginx
```

### Test Renewal

```bash
sudo certbot renew --dry-run
```

---

## Step 10: Firewall Configuration

```bash
# Enable UFW firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

---

## Monitoring & Maintenance

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f app
docker compose logs -f nginx
docker compose logs -f db
```

### Backup Database

```bash
# Create backup
docker compose exec db pg_dump -U xanene xanene_ops > backup_$(date +%Y%m%d).sql

# Restore from backup
cat backup_20260302.sql | docker compose exec -T db psql -U xanene xanene_ops
```

### Update Application

```bash
cd /opt/xanene_ops

# Pull latest changes (if using git)
git pull

# Rebuild and restart
docker compose down
docker compose up -d --build

# Check logs
docker compose logs -f
```

### Restart Services

```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart app
```

### Stop Application

```bash
# Stop all services
docker compose down

# Stop and remove volumes (WARNING: deletes data!)
docker compose down -v
```

---

## Troubleshooting

### Application Won't Start

```bash
# Check logs
docker compose logs app

# Check database connection
docker compose logs db

# Verify environment variables
docker compose exec app env | grep -E "(DATABASE|SECRET)"
```

### SSL Certificate Issues

```bash
# Check certificate expiry
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Check nginx configuration
docker compose exec nginx nginx -t
```

### Database Connection Errors

```bash
# Check database is healthy
docker compose ps db

# Test connection
docker compose exec db pg_isready -U xanene

# View database logs
docker compose logs db
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Restart services
docker compose restart

# Scale down workers if needed (edit docker-compose.yml)
```

---

## Production URLs

After deployment, access:

- **Main App:** https://your-domain.com
- **API:** https://your-domain.com/api
- **API Docs:** https://your-domain.com/docs
- **Health Check:** https://your-domain.com/health

---

## Security Recommendations

1. ✅ Change default admin password immediately
2. ✅ Use strong, unique passwords for database
3. ✅ Enable firewall (UFW)
4. ✅ Setup automatic security updates
5. ✅ Regular database backups
6. ✅ Monitor logs for suspicious activity
7. ✅ Keep Docker and system updated
8. ✅ Use HTTPS only (no HTTP)
9. ✅ Restrict database port access
10. ✅ Setup fail2ban for SSH protection

---

## Support

For issues or questions, check:
- Application logs: `docker compose logs -f`
- Nginx logs: `docker compose exec nginx tail -f /var/log/nginx/error.log`
- Database logs: `docker compose logs db`

---

**Deployment Complete! 🎉**

Your XANENE OPS application is now live and accessible at https://your-domain.com
