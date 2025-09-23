from complaints.models import Department
from django.contrib.auth.models import User

# Create sample departments
departments_data = [
    {
        'name': 'Infrastructure and Public Works',
        'description': 'Handles roads, bridges, buildings, construction issues, and public facilities maintenance',
        'contact_email': 'infrastructure@smartgriev.gov',
        'contact_phone': '+1-555-0101'
    },
    {
        'name': 'Healthcare Services',
        'description': 'Manages hospitals, clinics, medical services, health insurance, and sanitation',
        'contact_email': 'healthcare@smartgriev.gov',
        'contact_phone': '+1-555-0102'
    },
    {
        'name': 'Education Department',
        'description': 'Oversees schools, colleges, educational policies, teacher issues, and student facilities',
        'contact_email': 'education@smartgriev.gov',
        'contact_phone': '+1-555-0103'
    },
    {
        'name': 'Transportation and Traffic',
        'description': 'Handles public transport, traffic management, vehicle registration, and parking',
        'contact_email': 'transport@smartgriev.gov',
        'contact_phone': '+1-555-0104'
    },
    {
        'name': 'Water, Electricity and Utilities',
        'description': 'Manages water supply, electricity, gas, waste management, and sewage systems',
        'contact_email': 'utilities@smartgriev.gov',
        'contact_phone': '+1-555-0105'
    }
]

# Create or update departments
for dept_data in departments_data:
    dept, created = Department.objects.get_or_create(
        name=dept_data['name'],
        defaults=dept_data
    )
    if created:
        print(f"Created department: {dept.name}")
    else:
        print(f"Department already exists: {dept.name}")

print(f"\nTotal departments: {Department.objects.count()}")