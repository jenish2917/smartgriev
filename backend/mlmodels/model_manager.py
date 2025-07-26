import os
import time
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    MBartForConditionalGeneration,
    pipeline
)
import fasttext
from django.conf import settings
from .models import MLModel, ModelPrediction

class ModelManager:
    _instance = None
    _models = {}
    _tokenizers = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._load_all_models()
        return cls._instance

    def _load_all_models(self):
        """Load all active models into memory"""
        active_models = MLModel.objects.filter(is_active=True)
        for model_info in active_models:
            self._load_model(model_info)

    def _load_model(self, model_info):
        """Load a specific model into memory"""
        model_path = os.path.join(settings.MODELS_ROOT, model_info.model_path)
        
        if model_info.framework == MLModel.ModelFramework.TRANSFORMERS:
            if model_info.model_type == MLModel.ModelType.COMPLAINT:
                model = AutoModelForSequenceClassification.from_pretrained(model_path)
                tokenizer = AutoTokenizer.from_pretrained(model_path)
            elif model_info.model_type == MLModel.ModelType.SENTIMENT:
                model = AutoModelForSequenceClassification.from_pretrained(model_path)
                tokenizer = AutoTokenizer.from_pretrained(model_path)
            elif model_info.model_type == MLModel.ModelType.NER:
                model = AutoModelForTokenClassification.from_pretrained(model_path)
                tokenizer = AutoTokenizer.from_pretrained(model_path)
            elif model_info.model_type == MLModel.ModelType.TRANSLATOR:
                model = MBartForConditionalGeneration.from_pretrained(model_path)
                tokenizer = AutoTokenizer.from_pretrained(model_path)
            
            if torch.cuda.is_available():
                model = model.to('cuda')
            
            self._models[model_info.id] = model
            self._tokenizers[model_info.id] = tokenizer
        
        elif model_info.framework == MLModel.ModelFramework.FASTTEXT:
            model = fasttext.load_model(model_path)
            self._models[model_info.id] = model

    def predict(self, model_id, text, source_lang=None, target_lang=None):
        """Make prediction using specified model"""
        start_time = time.time()
        model_info = MLModel.objects.get(id=model_id)
        model = self._models.get(model_id)
        tokenizer = self._tokenizers.get(model_id)

        if model is None:
            self._load_model(model_info)
            model = self._models[model_id]
            tokenizer = self._tokenizers.get(model_id)

        try:
            if model_info.model_type == MLModel.ModelType.COMPLAINT:
                prediction = self._predict_complaint(model, tokenizer, text)
            elif model_info.model_type == MLModel.ModelType.SENTIMENT:
                prediction = self._predict_sentiment(model, tokenizer, text)
            elif model_info.model_type == MLModel.ModelType.NER:
                prediction = self._predict_ner(model, tokenizer, text)
            elif model_info.model_type == MLModel.ModelType.LANG:
                prediction = self._predict_language(model, text)
            elif model_info.model_type == MLModel.ModelType.TRANSLATOR:
                prediction = self._translate_text(model, tokenizer, text, source_lang, target_lang)

            processing_time = time.time() - start_time

            # Store prediction
            ModelPrediction.objects.create(
                model=model_info,
                input_text=text,
                input_language=source_lang,
                output_language=target_lang,
                prediction=prediction['result'],
                confidence=prediction['confidence'],
                processing_time=processing_time,
                metadata=prediction.get('metadata', {})
            )

            return prediction

        except Exception as e:
            return {'error': str(e)}

    def _predict_complaint(self, model, tokenizer, text):
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        if torch.cuda.is_available():
            inputs = {k: v.to('cuda') for k, v in inputs.items()}
        
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        prediction = torch.argmax(probs, dim=-1)
        confidence = float(probs[0][prediction])
        
        return {
            'result': {
                'category': model.config.id2label[prediction.item()],
                'probabilities': {
                    label: float(prob)
                    for label, prob in zip(model.config.id2label.values(), probs[0])
                }
            },
            'confidence': confidence
        }

    def _predict_sentiment(self, model, tokenizer, text):
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        if torch.cuda.is_available():
            inputs = {k: v.to('cuda') for k, v in inputs.items()}
        
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        prediction = torch.argmax(probs, dim=-1)
        confidence = float(probs[0][prediction])
        
        return {
            'result': {
                'sentiment': model.config.id2label[prediction.item()],
                'probabilities': {
                    label: float(prob)
                    for label, prob in zip(model.config.id2label.values(), probs[0])
                }
            },
            'confidence': confidence
        }

    def _predict_ner(self, model, tokenizer, text):
        ner = pipeline('ner', model=model, tokenizer=tokenizer)
        entities = ner(text)
        
        # Group by entity type
        grouped_entities = {}
        for entity in entities:
            entity_type = entity['entity']
            if entity_type not in grouped_entities:
                grouped_entities[entity_type] = []
            grouped_entities[entity_type].append({
                'text': entity['word'],
                'score': float(entity['score']),
                'start': entity['start'],
                'end': entity['end']
            })
        
        return {
            'result': grouped_entities,
            'confidence': sum(e['score'] for e in entities) / len(entities) if entities else 0
        }

    def _predict_language(self, model, text):
        prediction = model.predict(text)
        return {
            'result': {
                'language': prediction[0][0].replace('__label__', ''),
                'probabilities': {
                    lang.replace('__label__', ''): float(prob)
                    for lang, prob in zip(prediction[0], prediction[1])
                }
            },
            'confidence': float(prediction[1][0])
        }

    def _translate_text(self, model, tokenizer, text, source_lang, target_lang):
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        if torch.cuda.is_available():
            inputs = {k: v.to('cuda') for k, v in inputs.items()}
        
        tokenizer.src_lang = source_lang
        generated_tokens = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.lang_code_to_id[target_lang],
            num_beams=5,
            length_penalty=1.0,
            max_length=512
        )
        
        translation = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        
        return {
            'result': {
                'translated_text': translation,
                'source_language': source_lang,
                'target_language': target_lang
            },
            'confidence': 0.85  # Fixed confidence for translation
        }

    def get_supported_languages(self, model_id):
        """Get supported languages for a model"""
        model_info = MLModel.objects.get(id=model_id)
        return model_info.supported_languages
