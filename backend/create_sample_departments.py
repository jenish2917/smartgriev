# Create sample departments for the SmartGriev system
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgriev.settings')
django.setup()

from complaints.models import Department
from django.contrib.auth.models import User

# Create departments if they don't exist
departments_data = [
    {
        'name': 'Infrastructure and Public Works',
        'description': 'Roads, bridges, buildings, construction issues, public facilities maintenance',
        'contact_email': 'infrastructure@smartgriev.gov',
        'contact_phone': '+1-234-567-8901'
    },
    {
        'name': 'Healthcare Services',
        'description': 'Hospitals, clinics, medical services, health insurance, sanitation',
        'contact_email': 'healthcare@smartgriev.gov',
        'contact_phone': '+1-234-567-8902'
    },
    {
        'name': 'Education Department',
        'description': 'Schools, colleges, educational policies, teacher issues, student facilities',
        'contact_email': 'education@smartgriev.gov',
        'contact_phone': '+1-234-567-8903'
    },
    {
        'name': 'Transportation and Traffic',
        'description': 'Public transport, traffic management, vehicle registration, parking',
        'contact_email': 'transport@smartgriev.gov',
        'contact_phone': '+1-234-567-8904'
    },
    {
        'name': 'Water, Electricity and Utilities',
        'description': 'Water supply, electricity, gas, waste management, sewage',
        'contact_email': 'utilities@smartgriev.gov',
        'contact_phone': '+1-234-567-8905'
    }
]

created_departments = []
for dept_data in departments_data:
    dept, created = Department.objects.get_or_create(
        name=dept_data['name'],
        defaults={
            'description': dept_data['description'],
            'contact_email': dept_data['contact_email'],
            'contact_phone': dept_data['contact_phone']
        }
    )
    created_departments.append((dept, created))
    print(f"Department: {dept.name} - {'Created' if created else 'Already exists'}")

print()
print(f"Total departments in system: {Department.objects.count()}")