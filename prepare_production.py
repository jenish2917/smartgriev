#!/usr/bin/env python3
"""
SmartGriev Production Deployment Script
======================================

This script prepares the SmartGriev system for production deployment
by configuring environment variables, optimizing settings, and setting up
monitoring capabilities.
"""

import os
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

class ProductionDeployment:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_root = self.project_root / "backend"
        self.frontend_root = self.project_root / "frontend"
        
    def create_production_env(self):
        """Create production environment configuration"""
        print("🔧 Creating production environment configuration...")
        
        # Backend production settings
        backend_env = """# SmartGriev Production Environment Configuration
# Generated on {timestamp}

# Django Settings
DJANGO_SETTINGS_MODULE=smartgriev.settings.production
SECRET_KEY=your-super-secure-secret-key-here-change-in-production
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database Configuration (Production)
# DATABASE_URL=postgresql://user:password@localhost:5432/smartgriev_prod

# AI/ML Services
GROQ_API_KEY=your-groq-api-key-here
OPENAI_API_KEY=your-openai-api-key-here

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# SMS Configuration
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# Redis Configuration (for caching and Celery)
REDIS_URL=redis://localhost:6379/0

# File Storage
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=smartgriev-media
AWS_S3_REGION_NAME=us-east-1

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Performance
ENABLE_CACHING=True
CACHE_TIMEOUT=3600
""".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        with open(self.backend_root / ".env.production", "w") as f:
            f.write(backend_env)
        
        # Frontend production environment
        frontend_env = """# SmartGriev Frontend Production Environment
# Generated on {timestamp}

VITE_API_BASE_URL=https://api.your-domain.com/api
VITE_ENVIRONMENT=production
VITE_APP_NAME=SmartGriev
VITE_APP_VERSION=1.0.0
VITE_ENABLE_ANALYTICS=true
VITE_SENTRY_DSN=https://your-frontend-sentry-dsn@sentry.io/project-id
VITE_GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX
VITE_USE_INTEGRATED_APP=true

# Feature Flags
VITE_ENABLE_VOICE_COMPLAINTS=true
VITE_ENABLE_IMAGE_UPLOADS=true
VITE_ENABLE_REAL_TIME_UPDATES=true
VITE_ENABLE_PWA=true

# Performance
VITE_ENABLE_SERVICE_WORKER=true
VITE_BUNDLE_ANALYZER=false
""".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        with open(self.frontend_root / ".env.production", "w") as f:
            f.write(frontend_env)
        
        print("✅ Production environment files created")
        
    def create_docker_configuration(self):
        """Create Docker configuration for containerized deployment"""
        print("🐳 Creating Docker configuration...")
        
        # Backend Dockerfile
        backend_dockerfile = """# SmartGriev Backend Dockerfile
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=smartgriev.settings.production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \\
    && apt-get install -y --no-install-recommends \\
        postgresql-client \\
        build-essential \\
        libpq-dev \\
        ffmpeg \\
        libsm6 \\
        libxext6 \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/production.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/api/complaints/api/health/ || exit 1

# Run server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "smartgriev.wsgi:application"]
"""
        
        with open(self.backend_root / "Dockerfile", "w") as f:
            f.write(backend_dockerfile)
        
        # Frontend Dockerfile
        frontend_dockerfile = """# SmartGriev Frontend Dockerfile
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig*.json ./
COPY vite.config.ts ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY src/ ./src/
COPY public/ ./public/
COPY index.html ./

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
"""
        
        with open(self.frontend_root / "Dockerfile", "w") as f:
            f.write(frontend_dockerfile)
        
        # Docker Compose for full stack
        docker_compose = """version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: smartgriev
      POSTGRES_USER: smartgriev
      POSTGRES_PASSWORD: secure_password_here
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U smartgriev"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Redis for caching and Celery
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Django Backend
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://smartgriev:secure_password_here@db:5432/smartgriev
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - media_files:/app/media
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/complaints/api/health/"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Celery Worker for background tasks
  celery:
    build: ./backend
    command: celery -A smartgriev worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://smartgriev:secure_password_here@db:5432/smartgriev
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - media_files:/app/media

  # Celery Beat for scheduled tasks
  celery-beat:
    build: ./backend
    command: celery -A smartgriev beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://smartgriev:secure_password_here@db:5432/smartgriev
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app

  # React Frontend
  frontend:
    build: ./frontend
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      backend:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 5

volumes:
  postgres_data:
  media_files:
"""
        
        with open(self.project_root / "docker-compose.yml", "w") as f:
            f.write(docker_compose)
        
        print("✅ Docker configuration created")
    
    def create_nginx_config(self):
        """Create Nginx configuration for frontend"""
        print("🌐 Creating Nginx configuration...")
        
        nginx_config = """events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;
    
    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
    
    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        
        # Cache static assets
        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # Handle React Router
        location / {
            try_files $uri $uri/ /index.html;
        }
        
        # Health check
        location /health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }
        
        # Proxy API calls to backend
        location /api/ {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
"""
        
        with open(self.frontend_root / "nginx.conf", "w") as f:
            f.write(nginx_config)
        
        print("✅ Nginx configuration created")
    
    def create_monitoring_setup(self):
        """Create monitoring and logging configuration"""
        print("📊 Creating monitoring setup...")
        
        # Prometheus configuration for metrics
        prometheus_config = """global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "django_rules.yml"

scrape_configs:
  - job_name: 'smartgriev-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'smartgriev-frontend'
    static_configs:
      - targets: ['frontend:80']
    metrics_path: '/health'
    scrape_interval: 15s

  - job_name: 'postgres'
    static_configs:
      - targets: ['db:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
"""
        
        monitoring_dir = self.project_root / "monitoring"
        monitoring_dir.mkdir(exist_ok=True)
        
        with open(monitoring_dir / "prometheus.yml", "w") as f:
            f.write(prometheus_config)
        
        # Grafana dashboard configuration
        grafana_dashboard = {
            "dashboard": {
                "id": None,
                "title": "SmartGriev System Dashboard",
                "tags": ["smartgriev", "government", "grievance"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "API Response Times",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "django_http_requests_latency_seconds_by_view_method",
                                "legendFormat": "{{view}} - {{method}}"
                            }
                        ]
                    },
                    {
                        "id": 2,
                        "title": "Complaint Submissions",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "increase(django_model_inserts_total{model='complaint'}[1h])",
                                "legendFormat": "Complaints per hour"
                            }
                        ]
                    }
                ],
                "time": {
                    "from": "now-6h",
                    "to": "now"
                },
                "refresh": "30s"
            }
        }
        
        with open(monitoring_dir / "grafana_dashboard.json", "w") as f:
            json.dump(grafana_dashboard, f, indent=2)
        
        print("✅ Monitoring configuration created")
    
    def create_deployment_scripts(self):
        """Create deployment automation scripts"""
        print("🚀 Creating deployment scripts...")
        
        # Backend deployment script
        backend_deploy = """#!/bin/bash
# SmartGriev Backend Deployment Script

set -e

echo "🚀 Starting SmartGriev Backend Deployment..."

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | xargs)
fi

# Run database migrations
echo "📊 Running database migrations..."
python manage.py migrate --noinput

# Load initial data
echo "📂 Loading government departments..."
python manage.py loaddata departments

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if doesn't exist
echo "👤 Creating admin user..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@smartgriev.gov.in', 'secure_admin_password')
    print('Admin user created')
else:
    print('Admin user already exists')
"

# Start Celery workers
echo "🔄 Starting background workers..."
celery -A smartgriev worker --detach --loglevel=info
celery -A smartgriev beat --detach --loglevel=info

echo "✅ Backend deployment completed!"
"""
        
        scripts_dir = self.project_root / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        with open(scripts_dir / "deploy_backend.sh", "w") as f:
            f.write(backend_deploy)
        
        # Frontend deployment script
        frontend_deploy = """#!/bin/bash
# SmartGriev Frontend Deployment Script

set -e

echo "🚀 Starting SmartGriev Frontend Deployment..."

# Install dependencies
echo "📦 Installing dependencies..."
npm ci --only=production

# Run tests
echo "🧪 Running tests..."
npm run test:ci

# Build for production
echo "🏗️ Building production bundle..."
npm run build

# Analyze bundle size
echo "📊 Analyzing bundle size..."
npm run analyze

# Generate service worker
echo "⚙️ Generating service worker..."
npm run build:sw

echo "✅ Frontend deployment completed!"
echo "📁 Built files are in: ./dist"
"""
        
        with open(scripts_dir / "deploy_frontend.sh", "w") as f:
            f.write(frontend_deploy)
        
        # Make scripts executable (on Unix systems)
        import stat
        for script in scripts_dir.glob("*.sh"):
            script.chmod(script.stat().st_mode | stat.S_IEXEC)
        
        print("✅ Deployment scripts created")
    
    def create_production_requirements(self):
        """Create production-specific requirements"""
        print("📋 Creating production requirements...")
        
        production_requirements = """# SmartGriev Production Requirements
# Generated on {timestamp}

# Base requirements
-r base.txt

# Production-specific packages
gunicorn==21.2.0
psycopg2-binary==2.9.7
redis==4.6.0
celery==5.3.1
django-redis==5.3.0
django-storages==1.13.2
boto3==1.28.25
whitenoise==6.5.0

# Monitoring and logging
sentry-sdk[django]==1.29.2
django-prometheus==2.3.1
structlog==23.1.0

# Security
django-security==0.16.0
django-csp==3.7
django-ratelimit==4.1.0

# Performance
django-cachalot==2.5.1
django-compressor==4.4
""".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        requirements_dir = self.backend_root / "requirements"
        requirements_dir.mkdir(exist_ok=True)
        
        with open(requirements_dir / "production.txt", "w") as f:
            f.write(production_requirements)
        
        print("✅ Production requirements created")
    
    def run_deployment_preparation(self):
        """Run complete deployment preparation"""
        print("🎯 SmartGriev Production Deployment Preparation")
        print("=" * 50)
        
        try:
            self.create_production_env()
            self.create_docker_configuration()
            self.create_nginx_config()
            self.create_monitoring_setup()
            self.create_deployment_scripts()
            self.create_production_requirements()
            
            print("\n🎉 Production deployment preparation completed!")
            print("\nNext steps:")
            print("1. Review and update .env.production files with actual credentials")
            print("2. Build Docker images: docker-compose build")
            print("3. Start services: docker-compose up -d")
            print("4. Monitor with: docker-compose logs -f")
            print("5. Access application at: http://localhost")
            
        except Exception as e:
            print(f"❌ Error during deployment preparation: {str(e)}")
            return False
        
        return True

if __name__ == "__main__":
    deployment = ProductionDeployment()
    success = deployment.run_deployment_preparation()
    exit(0 if success else 1)