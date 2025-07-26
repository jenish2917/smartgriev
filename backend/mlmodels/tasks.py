from celery import shared_task
from .utils import classifier, sentiment_analyzer, entity_extractor, calculate_priority
from .models import MLModel, ModelPrediction
from complaints.models import Complaint
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_complaint(complaint_id: int):
    """Process a new complaint with ML models."""
    try:
        complaint = Complaint.objects.get(id=complaint_id)
        
        # Classify complaint
        categories = classifier.classify(complaint.description)
        main_category = max(categories.items(), key=lambda x: x[1])[0]
        
        # Analyze sentiment
        sentiment = sentiment_analyzer.analyze(complaint.description)
        
        # Extract entities
        entities = entity_extractor.extract_entities(complaint.description)
        
        # Calculate priority
        priority_level, priority_score = calculate_priority(
            sentiment,
            list(categories.keys()),
            complaint.description
        )
        
        # Update complaint
        complaint.category = main_category
        complaint.sentiment = sentiment['compound']
        complaint.priority = priority_level
        complaint.location_extracted = ', '.join(entities['locations'])
        complaint.save()
        
        # Create prediction records
        model = MLModel.objects.get(model_type='classification', is_active=True)
        ModelPrediction.objects.create(
            model=model,
            input_text=complaint.description,
            prediction=main_category,
            confidence=max(categories.values())
        )
        
        # Notify if high priority
        if priority_level == 'HIGH':
            notify_department.delay(complaint_id)
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing complaint {complaint_id}: {str(e)}")
        return False

@shared_task
def notify_department(complaint_id: int):
    """Send notification for high priority complaints."""
    try:
        complaint = Complaint.objects.get(id=complaint_id)
        department = complaint.department
        
        if department and department.officer:
            subject = f"High Priority Complaint: {complaint.title}"
            message = f"""
            Urgent: A high priority complaint has been filed.
            
            Title: {complaint.title}
            Category: {complaint.category}
            Priority: {complaint.priority}
            Location: {complaint.location_extracted or complaint.location}
            
            Description:
            {complaint.description}
            
            Please review and take immediate action.
            """
            
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [department.officer.email],
                fail_silently=False,
            )
            
        return True
        
    except Exception as e:
        logger.error(f"Error notifying about complaint {complaint_id}: {str(e)}")
        return False

@shared_task
def retrain_models():
    """Periodic task to retrain ML models with new data."""
    # TODO: Implement model retraining logic
    pass
