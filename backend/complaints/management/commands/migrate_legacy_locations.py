from django.core.management.base import BaseCommand
from complaints.models import Complaint

class Command(BaseCommand):
    help = 'Migrates legacy location data to the new GPS fields.'

    def handle(self, *args, **options):
        complaints_to_migrate = Complaint.objects.filter(
            incident_latitude__isnull=True,
            incident_longitude__isnull=True,
            location_lat__isnull=False,
            location_lon__isnull=False
        )

        for complaint in complaints_to_migrate:
            complaint.incident_latitude = complaint.location_lat
            complaint.incident_longitude = complaint.location_lon
            complaint.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully migrated {complaints_to_migrate.count()} complaints.'))
