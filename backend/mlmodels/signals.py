from django.db.models.signals import post_save
from django.dispatch import receiver
from complaints.models import Complaint
from .tasks import process_complaint

@receiver(post_save, sender=Complaint)
def process_new_complaint(sender, instance, created, **kwargs):
    """Process a new complaint with ML models when created."""
    if created:
        process_complaint.delay(instance.id)
