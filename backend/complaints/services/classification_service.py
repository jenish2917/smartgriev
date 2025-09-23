"""
Complaint Classification Service using Groq API with Qwen3 Model
This service classifies complaints into different departments automatically.
"""
import os
from typing import Dict, List, Optional
from groq import Groq
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ComplaintClassificationService:
    """Service for classifying complaints using Groq AI"""
    
    DEPARTMENTS = {
        'INFRASTRUCTURE': 'Infrastructure and Public Works',
        'HEALTHCARE': 'Healthcare Services',
        'EDUCATION': 'Education Department',
        'TRANSPORTATION': 'Transportation and Traffic',
        'UTILITIES': 'Water, Electricity and Utilities'
    }
    
    def __init__(self):
        """Initialize the Groq client with API key"""
        self.api_key = getattr(settings, 'GROQ_API_KEY', None)
        if not self.api_key:
            raise ValueError("GROQ_API_KEY must be set in environment variables")
        self.client = Groq(api_key=self.api_key)
        self.model = "llama3-8b-8192"  # Using available Groq model
    
    def classify_complaint(self, complaint_text: str, complaint_title: str = "") -> Dict[str, any]:
        """
        Classify a complaint into one of the five departments
        
        Args:
            complaint_text (str): The main complaint description
            complaint_title (str): Optional complaint title
            
        Returns:
            Dict containing classification results
        """
        try:
            # Prepare the classification prompt
            prompt = self._create_classification_prompt(complaint_text, complaint_title)
            
            # Call Groq API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert complaint classifier for government departments. Analyze complaints and classify them accurately into the appropriate department."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent classification
                max_tokens=500,
                top_p=0.9,
                stream=False
            )
            
            # Parse the response
            response_text = completion.choices[0].message.content
            return self._parse_classification_response(response_text)
            
        except Exception as e:
            logger.error(f"Error in complaint classification: {str(e)}")
            return {
                'department': 'INFRASTRUCTURE',  # Default fallback
                'confidence': 0.5,
                'reasoning': 'Classification failed, assigned to default department',
                'error': str(e)
            }
    
    def _create_classification_prompt(self, complaint_text: str, complaint_title: str = "") -> str:
        """Create a structured prompt for complaint classification"""
        
        departments_info = """
        Available Departments:
        1. INFRASTRUCTURE - Roads, bridges, buildings, construction issues, public facilities maintenance
        2. HEALTHCARE - Hospitals, clinics, medical services, health insurance, sanitation
        3. EDUCATION - Schools, colleges, educational policies, teacher issues, student facilities
        4. TRANSPORTATION - Public transport, traffic management, vehicle registration, parking
        5. UTILITIES - Water supply, electricity, gas, waste management, sewage
        """
        
        full_complaint = f"Title: {complaint_title}\nDescription: {complaint_text}" if complaint_title else complaint_text
        
        prompt = f"""
        {departments_info}
        
        Please classify the following complaint into ONE of the five departments above.
        
        Complaint to classify:
        {full_complaint}
        
        Respond in the following JSON format:
        {{
            "department": "DEPARTMENT_CODE",
            "confidence": 0.95,
            "reasoning": "Brief explanation of why this complaint belongs to this department"
        }}
        
        Consider keywords, context, and the nature of the issue to make an accurate classification.
        """
        
        return prompt
    
    def _parse_classification_response(self, response_text: str) -> Dict[str, any]:
        """Parse the AI response and extract classification data"""
        try:
            import json
            
            # Try to extract JSON from the response
            response_text = response_text.strip()
            
            # Find JSON content between braces
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start != -1 and end != 0:
                json_str = response_text[start:end]
                result = json.loads(json_str)
                
                # Validate department code
                department = result.get('department', '').upper()
                if department not in self.DEPARTMENTS:
                    department = 'INFRASTRUCTURE'  # Default fallback
                
                return {
                    'department': department,
                    'department_name': self.DEPARTMENTS[department],
                    'confidence': float(result.get('confidence', 0.7)),
                    'reasoning': result.get('reasoning', 'AI classification completed')
                }
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            logger.error(f"Error parsing classification response: {str(e)}")
            
            # Fallback: Simple keyword-based classification
            return self._fallback_classification(response_text)
    
    def _fallback_classification(self, text: str) -> Dict[str, any]:
        """Fallback classification using keyword matching"""
        text_lower = text.lower()
        
        keywords = {
            'INFRASTRUCTURE': ['road', 'bridge', 'building', 'construction', 'facility', 'infrastructure'],
            'HEALTHCARE': ['hospital', 'doctor', 'medical', 'health', 'clinic', 'medicine', 'treatment'],
            'EDUCATION': ['school', 'teacher', 'student', 'education', 'college', 'university', 'class'],
            'TRANSPORTATION': ['bus', 'train', 'traffic', 'transport', 'vehicle', 'parking', 'metro'],
            'UTILITIES': ['water', 'electricity', 'power', 'gas', 'waste', 'sewage', 'utility']
        }
        
        max_score = 0
        best_department = 'INFRASTRUCTURE'
        
        for dept, words in keywords.items():
            score = sum(1 for word in words if word in text_lower)
            if score > max_score:
                max_score = score
                best_department = dept
        
        return {
            'department': best_department,
            'department_name': self.DEPARTMENTS[best_department],
            'confidence': min(0.8, max_score / 10),
            'reasoning': f'Keyword-based fallback classification (matched {max_score} keywords)'
        }
    
    def classify_multiple_complaints(self, complaints: List[Dict[str, str]]) -> List[Dict[str, any]]:
        """Classify multiple complaints in batch"""
        results = []
        for complaint in complaints:
            result = self.classify_complaint(
                complaint.get('text', ''),
                complaint.get('title', '')
            )
            result['complaint_id'] = complaint.get('id')
            results.append(result)
        return results


# Service instance for dependency injection
complaint_classifier = ComplaintClassificationService()