from celery import shared_task
from .models import ModelPrediction
from .utils import load_model

@shared_task
def process_prediction(prediction_id):
    try:
        prediction = ModelPrediction.objects.get(id=prediction_id)
        model = prediction.model
        
        ml_model = load_model(model.model_type)
        
        if not ml_model:
            prediction.prediction = "ML model not available"
            prediction.confidence = 0.0
            prediction.save()
            return False
        
        result = ml_model(prediction.input_text)[0]
        prediction.prediction = result['label']
        prediction.confidence = result['score']
        
        prediction.save()
        return True
    except ModelPrediction.DoesNotExist:
        print(f"Prediction with id {prediction_id} does not exist.")
        return False
    except Exception as e:
        print(f"Error processing prediction {prediction_id}: {str(e)}")
        return False