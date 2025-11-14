"""
Management command to populate civic service departments
Usage: python manage.py populate_departments
"""
from django.core.management.base import BaseCommand
from complaints.models import Department
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Populates the database with common civic service departments'

    def handle(self, *args, **options):
        # Get admin user as default officer (or create a system user)
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.first()
        except:
            admin_user = None

        departments_data = [
            # Infrastructure & Roads
            {
                'name': 'Road & Transportation',
                'zone': 'City Wide',
                'description': 'Roads, highways, potholes, traffic signals, street lighting',
                'email': 'roads@smartgriev.gov.in',
                'phone': '+91-79-ROADS',
            },
            {
                'name': 'Public Works Department (PWD)',
                'zone': 'City Wide',
                'description': 'Public infrastructure, construction, maintenance',
                'email': 'pwd@smartgriev.gov.in',
                'phone': '+91-79-PWD',
            },
            
            # Water & Sanitation
            {
                'name': 'Water Supply & Sewerage',
                'zone': 'City Wide',
                'description': 'Water supply, sewage, drainage, water quality',
                'email': 'water@smartgriev.gov.in',
                'phone': '+91-79-WATER',
            },
            {
                'name': 'Sanitation & Cleanliness',
                'zone': 'City Wide',
                'description': 'Waste collection, street cleaning, public toilets',
                'email': 'sanitation@smartgriev.gov.in',
                'phone': '+91-79-CLEAN',
            },
            
            # Electricity & Power
            {
                'name': 'Electricity Board',
                'zone': 'City Wide',
                'description': 'Power supply, electricity billing, outages, streetlights',
                'email': 'electricity@smartgriev.gov.in',
                'phone': '+91-79-POWER',
            },
            
            # Health & Safety
            {
                'name': 'Health & Medical Services',
                'zone': 'City Wide',
                'description': 'Public hospitals, health centers, sanitation, disease control',
                'email': 'health@smartgriev.gov.in',
                'phone': '+91-79-HEALTH',
            },
            {
                'name': 'Fire & Emergency Services',
                'zone': 'City Wide',
                'description': 'Fire safety, emergency response, disaster management',
                'email': 'fire@smartgriev.gov.in',
                'phone': '101',
            },
            {
                'name': 'Police & Law Enforcement',
                'zone': 'City Wide',
                'description': 'Public safety, law and order, crime prevention',
                'email': 'police@smartgriev.gov.in',
                'phone': '100',
            },
            
            # Municipal Services
            {
                'name': 'Municipal Corporation',
                'zone': 'City Wide',
                'description': 'Property tax, building permits, civic amenities',
                'email': 'municipal@smartgriev.gov.in',
                'phone': '+91-79-CIVIC',
            },
            {
                'name': 'Town Planning & Development',
                'zone': 'City Wide',
                'description': 'Urban planning, building approvals, zoning',
                'email': 'planning@smartgriev.gov.in',
                'phone': '+91-79-PLAN',
            },
            
            # Environment & Parks
            {
                'name': 'Environment & Pollution Control',
                'zone': 'City Wide',
                'description': 'Air quality, noise pollution, environmental violations',
                'email': 'environment@smartgriev.gov.in',
                'phone': '+91-79-GREEN',
            },
            {
                'name': 'Parks & Gardens',
                'zone': 'City Wide',
                'description': 'Public parks, gardens, playgrounds, green spaces',
                'email': 'parks@smartgriev.gov.in',
                'phone': '+91-79-PARKS',
            },
            
            # Education & Social Welfare
            {
                'name': 'Education Department',
                'zone': 'City Wide',
                'description': 'Schools, educational facilities, student welfare',
                'email': 'education@smartgriev.gov.in',
                'phone': '+91-79-EDU',
            },
            {
                'name': 'Social Welfare',
                'zone': 'City Wide',
                'description': 'Welfare schemes, pensions, subsidies, social programs',
                'email': 'welfare@smartgriev.gov.in',
                'phone': '+91-79-WELFARE',
            },
            
            # Food & Consumer Affairs
            {
                'name': 'Food Safety & Standards',
                'zone': 'City Wide',
                'description': 'Food quality, restaurant hygiene, adulteration',
                'email': 'foodsafety@smartgriev.gov.in',
                'phone': '+91-79-FOOD',
            },
            {
                'name': 'Consumer Affairs',
                'zone': 'City Wide',
                'description': 'Consumer rights, product quality, fair trade practices',
                'email': 'consumer@smartgriev.gov.in',
                'phone': '+91-79-CONSUMER',
            },
            
            # Transport & Traffic
            {
                'name': 'Traffic Police',
                'zone': 'City Wide',
                'description': 'Traffic management, violations, parking',
                'email': 'traffic@smartgriev.gov.in',
                'phone': '+91-79-TRAFFIC',
            },
            {
                'name': 'Public Transport (BRTS/Bus)',
                'zone': 'City Wide',
                'description': 'Bus services, routes, schedules, bus stops',
                'email': 'transport@smartgriev.gov.in',
                'phone': '+91-79-BUS',
            },
            
            # Other Services
            {
                'name': 'Animal Control & Welfare',
                'zone': 'City Wide',
                'description': 'Stray animals, animal welfare, veterinary services',
                'email': 'animal@smartgriev.gov.in',
                'phone': '+91-79-ANIMAL',
            },
            {
                'name': 'Revenue Department',
                'zone': 'City Wide',
                'description': 'Land records, property documents, revenue collection',
                'email': 'revenue@smartgriev.gov.in',
                'phone': '+91-79-REVENUE',
            },
            {
                'name': 'General Administration',
                'zone': 'City Wide',
                'description': 'Other civic issues, general complaints',
                'email': 'admin@smartgriev.gov.in',
                'phone': '+91-79-ADMIN',
            },
        ]

        created_count = 0
        updated_count = 0

        for dept_data in departments_data:
            department, created = Department.objects.update_or_create(
                name=dept_data['name'],
                defaults={
                    'zone': dept_data['zone'],
                    'description': dept_data.get('description', ''),
                    'email': dept_data.get('email', ''),
                    'phone': dept_data.get('phone', ''),
                    'officer': admin_user,
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {department.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'→ Updated: {department.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully populated {created_count} new departments'
            )
        )
        if updated_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'→ Updated {updated_count} existing departments'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nTotal departments in system: {Department.objects.count()}'
            )
        )
