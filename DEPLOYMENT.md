# SmartGriev Production Deployment Guide

## Prerequisites

- Ubuntu 22.04 LTS server (minimum 2GB RAM, 2 CPU cores)
- Domain name pointed to server IP
- SSL certificate (Let's Encrypt recommended)
- PostgreSQL 15
- Redis 7
- Python 3.10+
- Node.js 18+

## 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.10 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Docker (optional, for containerized deployment)
curl -fssl https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

## 2. Database Setup

```bash
# Create PostgreSQL database and user
sudo -u postgres psql

CREATE DATABASE smartgriev_prod;
CREATE USER smartgriev_user WITH PASSWORD 'your-strong-password';
ALTER ROLE smartgriev_user SET client_encoding TO 'utf8';
ALTER ROLE smartgriev_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE smartgriev_user SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE smartgriev_prod TO smartgriev_user;
\q
```

## 3. Backend Deployment

```bash
# Clone repository
cd /var/www
git clone https://github.com/jenish2917/smartgriev.git
cd smartgriev/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements/production.txt

# Configure environment
cp .env.production.example .env.production
nano .env.production  # Update with actual values

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

## 4. Gunicorn Setup

```bash
# Create gunicorn socket
sudo nano /etc/systemd/system/gunicorn.socket
```

Content:
```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

```bash
# Create gunicorn service
sudo nano /etc/systemd/system/gunicorn.service
```

Content:
```ini
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/smartgriev/backend
ExecStart=/var/www/smartgriev/backend/venv/bin/gunicorn \
          --access-logfile - \
          --workers 4 \
          --bind unix:/run/gunicorn.sock \
          smartgriev.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Start gunicorn
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl status gunicorn
```

## 5. Frontend Deployment

```bash
cd /var/www/smartgriev/frontend

# Install dependencies
npm install

# Build production bundle
npm run build

# Files will be in dist/ directory
```

## 6. Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/smartgriev
```

Content:
```nginx
upstream backend {
    server unix:/run/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Frontend
    location / {
        root /var/www/smartgriev/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Admin
    location /admin/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Static files
    location /static/ {
        alias /var/www/smartgriev/backend/static/;
    }

    # Media files
    location /media/ {
        alias /var/www/smartgriev/backend/media/;
    }

    # Logs
    access_log /var/log/nginx/smartgriev_access.log;
    error_log /var/log/nginx/smartgriev_error.log;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/smartgriev /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 7. SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

## 8. Docker Deployment (Alternative)

```bash
cd /var/www/smartgriev

# Create .env files
cp backend/.env.production.example backend/.env.production
# Update values in .env.production

# Build and run
docker-compose -f docker-compose.prod.yml up -d --build

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser
```

## 9. Monitoring Setup

### Sentry (Error Tracking)
1. Create account at sentry.io
2. Create new project for SmartGriev
3. Add DSN to `.env.production`
4. Errors will be automatically tracked

### System Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Check logs
sudo journalctl -u gunicorn -f
sudo tail -f /var/log/nginx/smartgriev_error.log
```

## 10. Backup Strategy

```bash
# Create backup script
sudo nano /usr/local/bin/backup-smartgriev.sh
```

Content:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/smartgriev"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump -U smartgriev_user smartgriev_prod > $BACKUP_DIR/db_$DATE.sql

# Media files backup
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/smartgriev/backend/media/

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-smartgriev.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
0 2 * * * /usr/local/bin/backup-smartgriev.sh
```

## 11. Post-Deployment

```bash
# Test endpoints
curl https://yourdomain.com/api/
curl https://yourdomain.com/admin/

# Monitor logs
sudo journalctl -u gunicorn -f

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

## 12. Maintenance

```bash
# Update code
cd /var/www/smartgriev
git pull origin main
source backend/venv/bin/activate
pip install -r backend/requirements/production.txt
python backend/manage.py migrate
python backend/manage.py collectstatic --noinput
sudo systemctl restart gunicorn

# Frontend update
cd frontend
npm install
npm run build
```

## Security Checklist

- [ ] DEBUG=False in production
- [ ] Strong SECRET_KEY
- [ ] HTTPS enabled
- [ ] Firewall configured (UFW)
- [ ] Database password is strong
- [ ] Regular backups enabled
- [ ] Sentry error tracking configured
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Security headers set

## Performance Optimization

1. Enable Redis caching
2. Use CDN for static files (CloudFlare)
3. Enable gzip compression
4. Optimize database queries
5. Use connection pooling
6. Monitor with New Relic/DataDog

## Support

For issues:
- Check logs: `/var/log/nginx/` and `journalctl -u gunicorn`
- GitHub Issues: https://github.com/jenish2917/smartgriev/issues
- Email: support@yourdomain.com
