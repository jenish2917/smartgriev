from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import spacy

def load_model(model_type):
    try:
        if model_type == 'SENTIMENT':
            return pipeline('sentiment-analysis')
        elif model_type == 'COMPLAINT':
            tokenizer = AutoTokenizer.from_pretrained('./saved_model')
            model = AutoModelForSequenceClassification.from_pretrained('./saved_model')
            return pipeline('text-classification', model=model, tokenizer=tokenizer)
        elif model_type == 'NER':
            return spacy.load('en_core_web_sm')
        else:
            return None
    except (ImportError, OSError):
        return None