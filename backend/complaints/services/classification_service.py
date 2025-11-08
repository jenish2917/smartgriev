"""
Complaint Classification Service using Groq API with Qwen3 Model
This service classifies complaints into different departments automatically.
"""
import os
from typing import Dict, List, Optional
from django.conf import settings
import logging

# Try to import Groq, but make it optional
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None
    logging.warning("Groq library not available. AI classification will use fallback methods.")

logger = logging.getLogger(__name__)


class ComplaintClassificationService:
    """Enhanced service for classifying complaints using Groq AI with advanced features"""
    
    DEPARTMENTS = {
        'INFRASTRUCTURE': {
            'name': 'Infrastructure and Public Works',
            'description': 'Roads, bridges, buildings, construction, public facilities',
            'keywords': ['road', 'bridge', 'building', 'construction', 'infrastructure', 'facility', 'repair', 'maintenance'],
            'priority_keywords': ['collapse', 'dangerous', 'urgent repair', 'safety hazard'],
            'icon': '🏗️',
            'color': "#7F65FF"
        },
        'HEALTHCARE': {
            'name': 'Healthcare Services',
            'description': 'Hospitals, clinics, medical services, health insurance, sanitation',
            'keywords': ['hospital', 'doctor', 'medical', 'health', 'clinic', 'medicine', 'treatment', 'emergency'],
            'priority_keywords': ['emergency', 'critical', 'life threatening', 'urgent medical'],
            'icon': '🏥',
            'color': "#5E69BE"
        },
        'EDUCATION': {
            'name': 'Education Department',
            'description': 'Schools, colleges, educational policies, teacher issues, student facilities',
            'keywords': ['school', 'teacher', 'student', 'education', 'college', 'university', 'class', 'exam'],
            'priority_keywords': ['violence', 'safety', 'harassment', 'discrimination'],
            'icon': '🎓',
            'color': '#007BFF'
        },
        'TRANSPORTATION': {
            'name': 'Transportation and Traffic',
            'description': 'Public transport, traffic management, vehicle registration, parking',
            'keywords': ['transport', 'bus', 'train', 'traffic', 'vehicle', 'parking', 'license', 'registration'],
            'priority_keywords': ['accident', 'emergency', 'breakdown', 'blocked road'],
            'icon': '🚌',
            'color': "#1B2962"
        },
        'UTILITIES': {
            'name': 'Water, Electricity and Utilities',
            'description': 'Water supply, electricity, gas, waste management, sewage',
            'keywords': ['water', 'electricity', 'power', 'gas', 'waste', 'sewage', 'garbage', 'utility'],
            'priority_keywords': ['outage', 'leak', 'contamination', 'emergency repair'],
            'icon': '⚡',
            'color': "#070BFF"
        }
    }
    
    def __init__(self):
        """Initialize the enhanced Groq client with caching and monitoring"""
        self.api_key = getattr(settings, 'GROQ_API_KEY', None)
        self.client = None
        self.use_ai = False
        
        if GROQ_AVAILABLE and self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                self.use_ai = True
            except Exception as e:
                logging.warning(f"Failed to initialize Groq client: {e}. Using fallback classification.")
        elif not GROQ_AVAILABLE:
            logging.warning("Groq library not available. Using fallback classification.")
        else:
            logging.warning("GROQ_API_KEY not set. Using fallback classification.")
            
        self.model = "llama-3.1-8b-instant"  # Updated to latest supported Groq model
        self.classification_cache = {}  # Simple in-memory cache
        self.performance_metrics = {
            'total_classifications': 0,
            'successful_classifications': 0,
            'failed_classifications': 0,
            'average_response_time': 0.0,
            'cache_hits': 0
        }
    
    def classify_complaint(self, complaint_text: str, complaint_title: str = "") -> Dict[str, any]:
        """
        Enhanced complaint classification with caching, monitoring, and advanced features
        
        Args:
            complaint_text (str): The main complaint description
            complaint_title (str): Optional complaint title
            
        Returns:
            Dict containing comprehensive classification results
        """
        import time
        import hashlib
        
        start_time = time.time()
        self.performance_metrics['total_classifications'] += 1
        
        try:
            # Generate cache key
            cache_key = hashlib.md5(f"{complaint_title}:{complaint_text}".encode()).hexdigest()
            
            # Check cache first
            if cache_key in self.classification_cache:
                self.performance_metrics['cache_hits'] += 1
                cached_result = self.classification_cache[cache_key]
                cached_result['from_cache'] = True
                return cached_result
            
            # Preprocess and validate input
            processed_data = self._preprocess_complaint(complaint_text, complaint_title)
            
            # Quick keyword-based pre-classification for high-confidence cases
            keyword_result = self._get_quick_classification(processed_data['text'])
            if keyword_result['confidence'] > 0.85:
                result = self._enhance_classification_result(keyword_result, processed_data)
                self.classification_cache[cache_key] = result
                self.performance_metrics['successful_classifications'] += 1
                return result
            
            # Use AI for complex cases if available
            if self.use_ai:
                prompt = self._create_enhanced_classification_prompt(processed_data)
                
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": self._get_system_prompt()
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.2,  # Lower temperature for consistency
                    max_tokens=800,
                    top_p=0.9,
                    stream=False
                )
                
                response_text = completion.choices[0].message.content
                result = self._parse_enhanced_classification_response(response_text, processed_data)
            else:
                # Use intelligent fallback when AI is not available
                result = self._get_intelligent_fallback(complaint_text, complaint_title, "AI service not available")
            
            # Cache successful result
            self.classification_cache[cache_key] = result
            self.performance_metrics['successful_classifications'] += 1
            
            # Update performance metrics
            response_time = time.time() - start_time
            self._update_performance_metrics(response_time)
            
            return result
            
        except Exception as e:
            self.performance_metrics['failed_classifications'] += 1
            logger.error(f"Enhanced classification error: {str(e)}")
            
            # Enhanced fallback with reasoning
            fallback_result = self._get_intelligent_fallback(complaint_text, complaint_title, str(e))
            return fallback_result
    
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


    def _fallback_classification(self, text: str) -> Dict[str, any]:
        """Legacy fallback method - redirects to enhanced fallback"""
        return self._get_intelligent_fallback(text, '', 'Legacy fallback method called')


    def _preprocess_complaint(self, complaint_text: str, complaint_title: str = "") -> Dict[str, any]:
        """Preprocess complaint text for better classification"""
        import re
        
        # Clean and normalize text
        full_text = f"{complaint_title} {complaint_text}".strip()
        cleaned_text = re.sub(r'\s+', ' ', full_text)  # Normalize whitespace
        
        # Extract key information
        urgency_indicators = ['urgent', 'emergency', 'critical', 'immediate', 'asap', 'help']
        location_indicators = re.findall(r'\b(?:near|at|in|on)\s+([A-Za-z\s]+)\b', cleaned_text.lower())
        
        urgency_score = sum(1 for indicator in urgency_indicators if indicator in cleaned_text.lower())
        
        return {
            'text': cleaned_text,
            'word_count': len(cleaned_text.split()),
            'urgency_score': urgency_score,
            'locations': location_indicators[:3],  # Keep top 3 locations
            'has_numbers': bool(re.search(r'\d+', cleaned_text)),
            'has_contact': bool(re.search(r'\b\d{10}\b|\b[\w.-]+@[\w.-]+\.\w+\b', cleaned_text))
        }
    
    def _get_quick_classification(self, text: str) -> Dict[str, any]:
        """Fast keyword-based classification for high-confidence cases"""
        text_lower = text.lower()
        scores = {}
        
        for dept_code, dept_info in self.DEPARTMENTS.items():
            score = 0
            
            # Check regular keywords
            for keyword in dept_info['keywords']:
                if keyword in text_lower:
                    score += 1
            
            # Check priority keywords (higher weight)
            for priority_keyword in dept_info['priority_keywords']:
                if priority_keyword in text_lower:
                    score += 3
            
            scores[dept_code] = score
        
        # Find best match
        best_dept = max(scores, key=scores.get)
        max_score = scores[best_dept]
        
        # Calculate confidence based on score and text length
        confidence = min(0.95, (max_score * 0.2) + 0.3)
        
        return {
            'department': best_dept,
            'department_name': self.DEPARTMENTS[best_dept]['name'],
            'confidence': confidence,
            'reasoning': f'Keyword-based classification (score: {max_score})',
            'method': 'keyword'
        }
    
    def _get_system_prompt(self) -> str:
        """Generate enhanced system prompt with department details"""
        dept_details = "\n".join([
            f"{code}: {info['name']} - {info['description']}"
            for code, info in self.DEPARTMENTS.items()
        ])
        
        return f"""You are an expert AI classifier for Indian government complaints with deep understanding of:
        - Government department structures and responsibilities
        - Citizen complaint patterns and urgency levels
        - Administrative processes and routing efficiency
        
        Available Departments:
        {dept_details}
        
        Your task is to classify complaints accurately and provide reasoning. Consider:
        1. Primary department responsibility
        2. Urgency level (low/medium/high/critical)
        3. Potential secondary departments if applicable
        4. Confidence level based on clarity and keywords
        
        Always respond with valid JSON only."""
    
    def _create_enhanced_classification_prompt(self, processed_data: Dict) -> str:
        """Create enhanced prompt with preprocessed data"""
        return f"""Classify this government complaint:
        
        Text: {processed_data['text']}
        
        Additional Context:
        - Word count: {processed_data['word_count']}
        - Urgency indicators: {processed_data['urgency_score']}
        - Mentioned locations: {', '.join(processed_data['locations']) if processed_data['locations'] else 'None'}
        - Contains numbers: {processed_data['has_numbers']}
        - Has contact info: {processed_data['has_contact']}
        
        Provide classification in this exact JSON format:
        {{
            "department": "DEPARTMENT_CODE",
            "confidence": 0.95,
            "urgency_level": "high",
            "reasoning": "Detailed explanation of classification decision",
            "secondary_departments": ["DEPT1", "DEPT2"],
            "estimated_resolution_days": 7,
            "required_documents": ["ID proof", "Photos"],
            "escalation_needed": false
        }}"""
    
    def _parse_enhanced_classification_response(self, response_text: str, processed_data: Dict) -> Dict[str, any]:
        """Parse enhanced AI response with validation and enrichment"""
        try:
            import json
            
            # Extract JSON from response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start != -1 and end != 0:
                json_str = response_text[start:end]
                result = json.loads(json_str)
                
                # Validate and enrich result
                department = result.get('department', '').upper()
                if department not in self.DEPARTMENTS:
                    department = 'INFRASTRUCTURE'  # Safe fallback
                
                dept_info = self.DEPARTMENTS[department]
                
                return {
                    'department': department,
                    'department_name': dept_info['name'],
                    'department_description': dept_info['description'],
                    'department_icon': dept_info['icon'],
                    'department_color': dept_info['color'],
                    'confidence': min(1.0, float(result.get('confidence', 0.7))),
                    'urgency_level': result.get('urgency_level', 'medium'),
                    'reasoning': result.get('reasoning', 'AI classification completed'),
                    'secondary_departments': result.get('secondary_departments', []),
                    'estimated_resolution_days': result.get('estimated_resolution_days', 7),
                    'required_documents': result.get('required_documents', []),
                    'escalation_needed': result.get('escalation_needed', False),
                    'method': 'ai_enhanced',
                    'processing_info': processed_data,
                    'from_cache': False
                }
            else:
                raise ValueError("No valid JSON found in AI response")
                
        except Exception as e:
            logger.error(f"Error parsing enhanced AI response: {str(e)}")
            return self._get_intelligent_fallback(processed_data['text'], '', str(e))
    
    def _get_intelligent_fallback(self, complaint_text: str, complaint_title: str, error: str) -> Dict[str, any]:
        """Intelligent fallback with enhanced reasoning"""
        # Use quick classification as fallback
        quick_result = self._get_quick_classification(complaint_text)
        dept_info = self.DEPARTMENTS[quick_result['department']]
        
        return {
            'department': quick_result['department'],
            'department_name': dept_info['name'],
            'department_description': dept_info['description'],
            'department_icon': dept_info['icon'],
            'department_color': dept_info['color'],
            'confidence': max(0.4, quick_result['confidence'] - 0.2),
            'urgency_level': 'medium',
            'reasoning': f"Fallback classification due to: {error}. Used keyword matching.",
            'secondary_departments': [],
            'estimated_resolution_days': 10,
            'required_documents': ['ID Proof', 'Address Proof'],
            'escalation_needed': False,
            'method': 'fallback_enhanced',
            'from_cache': False,
            'error': error
        }
    
    def _enhance_classification_result(self, result: Dict, processed_data: Dict) -> Dict[str, any]:
        """Enhance classification result with additional information"""
        dept_info = self.DEPARTMENTS[result['department']]
        
        # Determine urgency based on keywords and score
        urgency = 'low'
        if processed_data['urgency_score'] >= 2:
            urgency = 'critical'
        elif processed_data['urgency_score'] >= 1:
            urgency = 'high'
        elif any(keyword in processed_data['text'].lower() 
                for keyword in dept_info['priority_keywords']):
            urgency = 'high'
        
        result.update({
            'department_description': dept_info['description'],
            'department_icon': dept_info['icon'],
            'department_color': dept_info['color'],
            'urgency_level': urgency,
            'estimated_resolution_days': 3 if urgency == 'critical' else 7 if urgency == 'high' else 10,
            'escalation_needed': urgency in ['critical', 'high'],
            'processing_info': processed_data,
            'from_cache': False
        })
        
        return result
    
    def _update_performance_metrics(self, response_time: float):
        """Update performance tracking metrics"""
        total = self.performance_metrics['total_classifications']
        current_avg = self.performance_metrics['average_response_time']
        
        # Calculate rolling average
        self.performance_metrics['average_response_time'] = (
            (current_avg * (total - 1)) + response_time
        ) / total
    
    def get_performance_metrics(self) -> Dict[str, any]:
        """Get current performance metrics"""
        metrics = self.performance_metrics.copy()
        if metrics['total_classifications'] > 0:
            metrics['success_rate'] = (
                metrics['successful_classifications'] / metrics['total_classifications']
            ) * 100
            metrics['cache_hit_rate'] = (
                metrics['cache_hits'] / metrics['total_classifications']
            ) * 100
        else:
            metrics['success_rate'] = 0
            metrics['cache_hit_rate'] = 0
        
        return metrics
    
    def clear_cache(self):
        """Clear classification cache"""
        self.classification_cache.clear()
        logger.info("Classification cache cleared")
        
    def health_check(self) -> Dict[str, any]:
        """Comprehensive health check for the classification service"""
        try:
            # Test classification with sample data
            test_result = self.classify_complaint(
                "Test complaint about road repair needed urgently",
                "Road Repair Test"
            )
            
            metrics = self.get_performance_metrics()
            
            return {
                'status': 'healthy',
                'ai_model': self.model,
                'departments_available': len(self.DEPARTMENTS),
                'test_classification_successful': 'department' in test_result,
                'performance_metrics': metrics,
                'cache_size': len(self.classification_cache),
                'last_test_result': test_result.get('department', 'unknown')
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'ai_model': self.model,
                'departments_available': len(self.DEPARTMENTS)
            }


# Service instance for dependency injection
complaint_classifier = ComplaintClassificationService()