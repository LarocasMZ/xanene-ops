# XANENE OPS

**Production-Ready Operations Management System for Circular Economy**

A modern web application for managing operations at Xa Nene - a circular economy company working with organic waste collection, Black Soldier Fly production, animal feed production, logistics, and field operations.

![Dashboard Preview](docs/dashboard.png)

## Features

- 🔐 **User Authentication** - JWT-based secure login with role-based access control
- 👥 **Role-Based Access** - Admin, Operations Manager, Field Staff, and Sales roles
- 📅 **Shared Calendar** - Team calendar with events for collections, production, deliveries, training, and sales
- ✅ **Task Management** - Kanban board and list views with priority levels and status tracking
- 📊 **Dashboard** - Real-time metrics and overview of operations
- 📱 **Mobile Responsive** - Works seamlessly on desktop, tablet, and mobile devices
- 🎨 **Modern UI** - Clean dark theme with green accents inspired by Linear and Notion

## Tech Stack

### Backend
- **Python 3.11** with **FastAPI**
- **PostgreSQL** database
- **SQLAlchemy** ORM
- **JWT** authentication with bcrypt password hashing
- **Gunicorn** with Uvicorn workers

### Frontend
- **Vanilla JavaScript** (no build step required)
- **TailwindCSS** via CDN
- **Font Awesome** icons
- Responsive design with mobile-first approach

### Deployment
- **Docker** & **Docker Compose**
- **Nginx** reverse proxy
- **Systemd** service (for non-Docker deployment)
- **Certbot** ready for SSL

## Project Structure

```
xanene_ops/
├── backend/
│   └── app/
│       ├── api/
│       │   ├── __init__.py
│       │   ├── auth.py        # Authentication endpoints
│       │   ├── dashboard.py   # Dashboard metrics
│       │   ├── deps.py        # Dependencies & auth guards
│       │   ├── events.py      # Calendar events CRUD
│       │   └── tasks.py       # Task management CRUD
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py      # Application settings
│       │   ├── database.py    # Database connection
│       │   └── security.py    # JWT & password hashing
│       ├── models/
│       │   ├── __init__.py
│       │   ├── event.py       # Event model
│       │   ├── task.py        # Task model
│       │   └── user.py        # User model
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── dashboard.py   # Dashboard schemas
│       │   ├── event.py       # Event schemas
│       │   ├── task.py        # Task schemas
│       │   └── user.py        # User schemas
│       └── main.py            # FastAPI application
├── frontend/
│   ├── css/                   # Static styles (if needed)
│   ├── js/
│   │   └── app.js             # Frontend application
│   ├── images/                # Static images
│   └── index.html             # Main HTML file
├── nginx/
│   └── nginx.conf             # Nginx configuration
├── docker/
│   ├── schema.sql             # Database schema
│   └── xanene-ops.service     # Systemd service file
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## Quick Start (Docker)

### Prerequisites
- Docker and Docker Compose installed
- Ubuntu 20.04+ or similar Linux distribution

### 1. Clone and Setup

```bash
cd /opt
git clone <repository-url> xanene_ops
cd xanene_ops
```

### 2. Configure Environment

```bash
cp .env.example .env
nano .env
```

Update the following in `.env`:
```bash
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(32))">
DB_PASSWORD=<your-secure-database-password>
```

### 3. Start with Docker Compose

```bash
docker-compose up -d --build
```

### 4. Access the Application

- **Web Interface**: http://your-server-ip:8000
- **API Documentation**: http://your-server-ip:8000/docs
- **Default Login**: admin@xanene.com / admin123

## Production Deployment (Ubuntu Server)

### Option A: Docker Compose (Recommended)

#### 1. Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Setup Application

```bash
# Create directory
sudo mkdir -p /opt/xanene_ops
sudo chown $USER:$USER /opt/xanene_ops

# Copy files to /opt/xanene_ops
cd /opt/xanene_ops

# Create .env file
cp .env.example .env
nano .env  # Update with your values
```

#### 3. Configure SSL with Certbot

```bash
# Create SSL directory
sudo mkdir -p /opt/xanene_ops/nginx/ssl

# Install Certbot
sudo apt install certbot -y

# Get SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /opt/xanene_ops/nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem /opt/xanene_ops/nginx/ssl/

# Auto-renewal setup
sudo crontab -e
# Add: 0 3 * * * certbot renew --quiet && docker-compose restart nginx
```

#### 4. Update Nginx Config

Edit `nginx/nginx.conf` and replace `server_name _;` with:
```nginx
server_name your-domain.com www.your-domain.com;
```

#### 5. Start Services

```bash
docker-compose up -d --build
```

#### 6. Verify

```bash
docker-compose ps
docker-compose logs -f
```

### Option B: Native Installation (Systemd)

#### 1. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Python
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Nginx
sudo apt install nginx -y
```

#### 2. Setup PostgreSQL

```bash
sudo -u postgres psql << EOF
CREATE DATABASE xanene_ops;
CREATE USER xanene WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE xanene_ops TO xanene;
\c xanene_ops
GRANT ALL ON SCHEMA public TO xanene;
EOF
```

#### 3. Setup Application

```bash
# Create directory
sudo mkdir -p /opt/xanene_ops
sudo chown $USER:$USER /opt/xanene_ops
cd /opt/xanene_ops

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy files
# ... copy backend, frontend, etc.
```

#### 4. Setup Database Schema

```bash
sudo -u postgres psql xanene_ops < docker/schema.sql
```

#### 5. Configure Environment

```bash
cp .env.example .env
nano .env
```

#### 6. Setup Systemd Service

```bash
sudo cp docker/xanene-ops.service /etc/systemd/system/
sudo nano /etc/systemd/system/xanene-ops.service  # Update paths and secrets
sudo systemctl daemon-reload
sudo systemctl enable xanene-ops
sudo systemctl start xanene-ops
```

#### 7. Configure Nginx

```bash
sudo cp nginx/nginx.conf /etc/nginx/nginx.conf
sudo nginx -t
sudo systemctl restart nginx
```

#### 8. Setup SSL

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User login |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/users` | Create user (Admin) |
| GET | `/api/auth/users` | List users (Admin) |
| GET | `/api/auth/users/{id}` | Get user (Admin) |
| PUT | `/api/auth/users/{id}` | Update user (Admin) |
| DELETE | `/api/auth/users/{id}` | Delete user (Admin) |

### Events (Calendar)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/events` | Create event |
| GET | `/api/events` | List events |
| GET | `/api/events/today` | Today's events |
| GET | `/api/events/upcoming` | Upcoming events |
| GET | `/api/events/{id}` | Get event |
| PUT | `/api/events/{id}` | Update event |
| DELETE | `/api/events/{id}` | Delete event |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tasks` | Create task |
| GET | `/api/tasks` | List tasks |
| GET | `/api/tasks/my-tasks` | Get assigned tasks |
| GET | `/api/tasks/overdue` | Get overdue tasks |
| GET | `/api/tasks/kanban` | Get Kanban board |
| GET | `/api/tasks/{id}` | Get task |
| PUT | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard` | Get dashboard data |

## User Roles & Permissions

| Role | Permissions |
|------|-------------|
| **Admin** | Full access - manage users, events, tasks |
| **Operations Manager** | Create/edit events and tasks |
| **Field Staff** | Update assigned tasks only |
| **Sales** | Create follow-up tasks, view calendar |

## Security Features

- ✅ JWT token-based authentication
- ✅ Bcrypt password hashing
- ✅ Role-based access control
- ✅ CORS protection
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Input validation (Pydantic)
- ✅ Secure headers (Nginx)
- ✅ Rate limiting (Nginx)
- ✅ HTTPS/SSL ready

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT signing key (min 32 chars) | Required |
| `DEBUG` | Debug mode | `false` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `1440` |
| `CORS_ORIGINS` | Allowed origins | `[]` |

## Maintenance

### Backup Database

```bash
# Docker
docker-compose exec db pg_dump -U xanene xanene_ops > backup.sql

# Native
pg_dump -U xanene xanene_ops > backup.sql
```

### Restore Database

```bash
psql -U xanene xanene_ops < backup.sql
```

### View Logs

```bash
# Docker
docker-compose logs -f app
docker-compose logs -f nginx

# Systemd
journalctl -u xanene-ops -f
```

### Update Application

```bash
# Docker
git pull
docker-compose down
docker-compose up -d --build

# Systemd
git pull
sudo systemctl restart xanene-ops
```

## Troubleshooting

### Application won't start
```bash
# Check logs
docker-compose logs app

# Verify database connection
docker-compose exec db pg_isready -U xanene
```

### SSL certificate issues
```bash
# Renew certificate
sudo certbot renew

# Check Nginx config
sudo nginx -t
```

### Database connection errors
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Verify credentials in .env
```

## Future Extensions

The codebase is modular and ready for:
- 📦 Inventory tracking (BSF batches)
- 🚜 Waste supplier management
- 💰 Animal feed sales tracking
- 📱 WhatsApp reminder integration
- 📲 Mobile PWA mode
- 📈 Advanced analytics & reporting

## License

Proprietary - Xa Nene Operations

## Support

For issues and questions, contact the development team.

---

**Built with ❤️ for Circular Economy**
