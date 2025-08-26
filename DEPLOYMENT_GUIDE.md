# SmartGriev Enterprise Deployment Guide

## 🚀 **Production Deployment Instructions**

### **📋 Prerequisites**

#### **System Requirements**
- **Operating System**: Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+
- **Python**: 3.10 or higher
- **Database**: PostgreSQL 13+ with PostGIS extension
- **Cache**: Redis 6.0+
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: 100GB+ SSD storage
- **CPU**: 4+ cores (8+ recommended)

#### **Network Requirements**
- **Ports**: 80 (HTTP), 443 (HTTPS), 5432 (PostgreSQL), 6379 (Redis)
- **SSL Certificate**: For HTTPS deployment
- **Domain**: Configured DNS pointing to server IP

### **🔧 Environment Setup**

#### **1. Clone Repository**
```bash
git clone https://github.com/your-org/smartgriev.git
cd smartgriev
```

#### **2. Create Virtual Environment**
```bash
python -m venv smartgriev_env
source smartgriev_env/bin/activate  # Linux/Mac
# OR
smartgriev_env\Scripts\activate     # Windows
```

#### **3. Install Dependencies**
```bash
# Install base requirements
pip install -r requirements/base.txt

# Install production requirements
pip install -r requirements/production.txt

# Install ML requirements (if using AI features)
pip install -r requirements/machine_learning.txt

# Install geospatial requirements (if using GIS features)
pip install -r requirements/geospatial.txt
```

### **🗄️ Database Configuration**

#### **PostgreSQL Setup**
```sql
-- Create database and user
CREATE DATABASE smartgriev_prod;
CREATE USER smartgriev_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE smartgriev_prod TO smartgriev_user;

-- Enable PostGIS extension
\c smartgriev_prod;
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
```

#### **Database Migration**
```bash
cd backend
python manage.py migrate --settings=config.production
python manage.py collectstatic --settings=config.production
```

### **⚙️ Production Configuration**

#### **Environment Variables (.env)**
```bash
# Database Configuration
DATABASE_URL=postgresql://smartgriev_user:password@localhost:5432/smartgriev_prod
DATABASE_NAME=smartgriev_prod
DATABASE_USER=smartgriev_user
DATABASE_PASSWORD=your_secure_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Security Settings
SECRET_KEY=your_super_secret_key_here_minimum_50_characters_long
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
CACHE_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/2

# Email Configuration (for notifications)
EMAIL_HOST=smtp.your-provider.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_USE_TLS=True

# SMS Configuration (optional)
SMS_API_KEY=your_sms_api_key
SMS_API_URL=https://api.sms-provider.com/v1/send

# AI/ML Configuration
OPENAI_API_KEY=your_openai_api_key  # Optional
HUGGINGFACE_TOKEN=your_hf_token     # Optional

# Security Headers
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/smartgriev/app.log
```

### **🐳 Docker Deployment**

#### **Dockerfile**
```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

# Copy application code
COPY backend/ /app/
COPY frontend/dist/ /app/static/

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "smartgriev.wsgi:application"]
```

#### **docker-compose.yml**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://smartgriev_user:password@db:5432/smartgriev_prod
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./media:/app/media
      - ./logs:/var/log/smartgriev

  db:
    image: postgis/postgis:13-3.1
    environment:
      POSTGRES_DB: smartgriev_prod
      POSTGRES_USER: smartgriev_user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  celery:
    build: .
    command: celery -A smartgriev worker -l info
    environment:
      - DATABASE_URL=postgresql://smartgriev_user:password@db:5432/smartgriev_prod
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - ./media:/var/www/media
      - ./static:/var/www/static
    depends_on:
      - web

volumes:
  postgres_data:
  redis_data:
```

### **🌐 Nginx Configuration**

#### **nginx.conf**
```nginx
upstream smartgriev_backend {
    server web:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/certificate.crt;
    ssl_certificate_key /etc/nginx/ssl/private.key;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Static files
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://smartgriev_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket support
    location /ws/ {
        proxy_pass http://smartgriev_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
    
    # Frontend application
    location / {
        try_files $uri $uri/ /index.html;
        root /var/www/static;
    }
}
```

### **🔄 Process Management**

#### **Systemd Service (smartgriev.service)**
```ini
[Unit]
Description=SmartGriev Django Application
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=smartgriev
Group=smartgriev
WorkingDirectory=/opt/smartgriev
Environment=DJANGO_SETTINGS_MODULE=config.production
ExecStart=/opt/smartgriev/venv/bin/gunicorn --bind unix:/run/smartgriev/smartgriev.sock --workers 4 smartgriev.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### **Celery Worker Service (smartgriev-celery.service)**
```ini
[Unit]
Description=SmartGriev Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=smartgriev
Group=smartgriev
WorkingDirectory=/opt/smartgriev
Environment=DJANGO_SETTINGS_MODULE=config.production
ExecStart=/opt/smartgriev/venv/bin/celery -A smartgriev worker -l info --detach
ExecStop=/opt/smartgriev/venv/bin/celery -A smartgriev control shutdown
ExecReload=/opt/smartgriev/venv/bin/celery -A smartgriev control reload
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **📊 Monitoring & Logging**

#### **Log Configuration**
```python
# In config/production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/smartgriev/app.log',
            'maxBytes': 1024*1024*50,  # 50MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

#### **Health Check Endpoint**
```python
# In main urls.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })

urlpatterns = [
    path('health/', health_check, name='health_check'),
    # ... other patterns
]
```

### **🔐 Security Checklist**

- [ ] **SSL/TLS Certificate**: Installed and configured
- [ ] **Database Security**: Strong passwords, restricted access
- [ ] **Environment Variables**: Stored securely, not in code
- [ ] **Firewall Rules**: Only necessary ports open
- [ ] **Regular Updates**: OS and dependency updates scheduled
- [ ] **Backup Strategy**: Database and media files backed up
- [ ] **Monitoring**: Application and system monitoring configured
- [ ] **Rate Limiting**: API rate limiting configured
- [ ] **CORS Settings**: Properly configured for frontend domain
- [ ] **Admin Access**: Strong passwords, 2FA enabled

### **🚀 Deployment Commands**

```bash
# 1. Start services
sudo systemctl start smartgriev
sudo systemctl start smartgriev-celery
sudo systemctl start nginx

# 2. Enable auto-start
sudo systemctl enable smartgriev
sudo systemctl enable smartgriev-celery
sudo systemctl enable nginx

# 3. Check status
sudo systemctl status smartgriev
sudo systemctl status smartgriev-celery
sudo systemctl status nginx

# 4. View logs
sudo journalctl -u smartgriev -f
sudo journalctl -u smartgriev-celery -f
sudo tail -f /var/log/nginx/access.log
```

### **📈 Performance Optimization**

#### **Database Optimization**
```sql
-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_complaints_status ON complaints_complaint(status);
CREATE INDEX CONCURRENTLY idx_complaints_created ON complaints_complaint(created_at);
CREATE INDEX CONCURRENTLY idx_complaints_location ON complaints_complaint USING GIST(location);
```

#### **Cache Configuration**
```python
# In settings
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache timeout settings
CACHE_TTL = 60 * 15  # 15 minutes
```

### **✅ Post-Deployment Verification**

1. **API Health Check**: `curl https://yourdomain.com/health/`
2. **Database Connection**: Verify admin panel access
3. **Static Files**: Check CSS/JS loading
4. **WebSocket**: Test real-time features
5. **AI Services**: Verify chatbot functionality
6. **Email/SMS**: Test notification delivery
7. **Analytics**: Check dashboard loading
8. **Performance**: Run load tests

---

## **🎯 Success Metrics**

After successful deployment, monitor these KPIs:

- **Response Time**: < 200ms average API response
- **Uptime**: > 99.9% availability
- **Error Rate**: < 0.1% application errors
- **User Satisfaction**: > 95% positive feedback
- **Processing Speed**: < 2 seconds for AI classification

## **📞 Support & Maintenance**

For production support and maintenance:
- **Documentation**: Comprehensive API documentation
- **Monitoring**: 24/7 system monitoring
- **Updates**: Regular security and feature updates
- **Backup**: Automated daily backups
- **Support**: Professional support team available

**Your SmartGriev enterprise platform is now ready for production use!** 🚀
