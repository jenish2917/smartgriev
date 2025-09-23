#!/bin/bash
# SmartGriev Backend Deployment Script

set -e

echo "Starting SmartGriev Backend Deployment..."

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | xargs)
fi

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Load initial data
echo "Loading government departments..."
python manage.py loaddata departments

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if doesn't exist
echo "Creating admin user..."
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
echo "Starting background workers..."
celery -A smartgriev worker --detach --loglevel=info
celery -A smartgriev beat --detach --loglevel=info

echo "Backend deployment completed successfully!"
