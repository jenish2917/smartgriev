"""
Government Department Classification System for SmartGriev
Simplified AI-powered routing for Indian government departments
"""

import asyncio
import logging
import json
import os
from typing import Dict, Any, Optional, List

# Try to import Groq, but make it optional
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    
logger = logging.getLogger(__name__)
if not GROQ_AVAILABLE:
    logger.warning("Groq library not available. Department classification will use fallback methods.")


class GovernmentDepartmentClassifier:
    """
    Classify complaints into appropriate Indian government departments
    """
    
    def __init__(self):
        """Initialize the department classifier"""
        try:
            # Initialize Groq client if available
            if GROQ_AVAILABLE and os.getenv('GROQ_API_KEY'):
                self.groq_client = Groq(
                    api_key=os.getenv('GROQ_API_KEY', 'gsk_...your_api_key_here...')
                )
                self.use_ai = True
            else:
                self.groq_client = None
                self.use_ai = False
            
            # Government department mapping
            self.departments = {
                "electricity": {
                    "name": "Electricity Board",
                    "keywords": ["बिजली", "electricity", "power", "voltage", "outage", "transformer", "meter"],
                    "sub_departments": ["Distribution", "Generation", "Transmission"],
                    "avg_resolution_days": 7,
                    "escalation": ["Junior Engineer", "Assistant Engineer", "Executive Engineer"]
                },
                "water": {
                    "name": "Water and Sanitation Department", 
                    "keywords": ["पानी", "water", "supply", "drainage", "sewage", "pipeline", "tap"],
                    "sub_departments": ["Supply", "Treatment", "Sewerage"],
                    "avg_resolution_days": 5,
                    "escalation": ["Junior Engineer", "Executive Engineer", "Chief Engineer"]
                },
                "roads": {
                    "name": "Public Works Department (Roads)",
                    "keywords": ["सड़क", "road", "highway", "street", "pothole", "construction", "traffic"],
                    "sub_departments": ["Construction", "Maintenance", "Traffic"],
                    "avg_resolution_days": 14,
                    "escalation": ["Site Engineer", "Assistant Engineer", "Superintending Engineer"]
                },
                "health": {
                    "name": "Health Department",
                    "keywords": ["स्वास्थ्य", "health", "hospital", "medical", "doctor", "medicine", "vaccine"],
                    "sub_departments": ["Primary Health", "Public Health", "Hospitals"],
                    "avg_resolution_days": 3,
                    "escalation": ["Medical Officer", "Chief Medical Officer", "Director Health"]
                },
                "education": {
                    "name": "Education Department",
                    "keywords": ["शिक्षा", "education", "school", "teacher", "student", "classroom", "books"],
                    "sub_departments": ["Primary Education", "Secondary Education", "Higher Education"],
                    "avg_resolution_days": 10,
                    "escalation": ["Headmaster", "Block Education Officer", "District Education Officer"]
                },
                "police": {
                    "name": "Police Department",
                    "keywords": ["पुलिस", "police", "crime", "theft", "security", "law", "order"],
                    "sub_departments": ["Local Police", "Traffic Police", "Crime Branch"],
                    "avg_resolution_days": 1,
                    "escalation": ["Constable", "Inspector", "Superintendent of Police"]
                },
                "municipal": {
                    "name": "Municipal Corporation",
                    "keywords": ["नगर", "garbage", "waste", "cleaning", "sanitation", "park", "street light"],
                    "sub_departments": ["Sanitation", "Parks", "Street Lighting"],
                    "avg_resolution_days": 5,
                    "escalation": ["Sanitary Inspector", "Health Officer", "Municipal Commissioner"]
                },
                "transport": {
                    "name": "Transport Department",
                    "keywords": ["परिवहन", "transport", "bus", "auto", "license", "vehicle", "registration"],
                    "sub_departments": ["Public Transport", "Vehicle Registration", "Traffic Management"],
                    "avg_resolution_days": 7,
                    "escalation": ["Motor Vehicle Inspector", "Regional Transport Officer", "Commissioner Transport"]
                },
                "land_revenue": {
                    "name": "Land and Revenue Department",
                    "keywords": ["भूमि", "land", "property", "revenue", "record", "mutation", "registry"],
                    "sub_departments": ["Land Records", "Revenue Collection", "Survey"],
                    "avg_resolution_days": 21,
                    "escalation": ["Patwari", "Tehsildar", "Collector"]
                },
                "consumer_affairs": {
                    "name": "Consumer Affairs Department",
                    "keywords": ["उपभोक्ता", "consumer", "market", "price", "quality", "fraud", "complaint"],
                    "sub_departments": ["Market Inspection", "Consumer Protection", "Fair Price Shops"],
                    "avg_resolution_days": 14,
                    "escalation": ["Inspector", "Assistant Commissioner", "Commissioner"]
                }
            }
            
            logger.info("GovernmentDepartmentClassifier initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize GovernmentDepartmentClassifier: {e}")
            raise
    
    async def classify_complaint(self, complaint_text: str, location: str = None) -> Dict[str, Any]:
        """
        Classify complaint into appropriate government department
        """
        try:
            if not complaint_text or not complaint_text.strip():
                return {
                    "success": False,
                    "error": "Empty complaint text provided"
                }
            
            # Try AI classification first
            ai_result = await self._get_ai_classification(complaint_text, location)
            
            if ai_result["success"]:
                return ai_result
            
            # Fallback to keyword-based classification
            keyword_result = self._get_keyword_classification(complaint_text)
            
            if keyword_result["success"]:
                return keyword_result
            
            # Default classification
            return {
                "success": True,
                "department": "municipal",
                "department_name": "Municipal Corporation",
                "sub_department": "General",
                "urgency_level": "medium",
                "confidence": 0.3,
                "estimated_resolution_days": 7,
                "escalation_path": ["Local Officer", "District Officer", "Commissioner"],
                "reasoning": "Default classification - no specific department identified",
                "classification_method": "default"
            }
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return {
                "success": False,
                "error": f"Classification failed: {str(e)}"
            }
    
    async def _get_ai_classification(self, complaint_text: str, location: str = None) -> Dict[str, Any]:
        """
        Use AI to classify the complaint
        """
        try:
            # Prepare classification prompt
            system_prompt = """You are an expert in Indian government administration. 
Classify this citizen complaint into the most appropriate government department.

Available departments:
1. electricity - Power supply, electrical issues
2. water - Water supply, sewerage, drainage
3. roads - Road maintenance, traffic, construction
4. health - Medical facilities, public health
5. education - Schools, teachers, educational facilities
6. police - Law and order, crime, security
7. municipal - Garbage, sanitation, street lighting
8. transport - Public transport, vehicle registration
9. land_revenue - Land records, property, revenue
10. consumer_affairs - Market regulation, consumer protection

Determine urgency level: low, medium, high, critical

Return JSON with:
- department: department code
- urgency_level: urgency level
- confidence: 0.0-1.0
- reasoning: brief explanation

Return valid JSON only."""
            
            # Build user prompt
            user_prompt = f"Classify this complaint: {complaint_text}"
            if location:
                user_prompt += f"\nLocation: {location}"
            
            # Call Groq API if available
            if not self.use_ai or not self.groq_client:
                logger.warning("AI not available, using keyword-based classification")
                return self._get_keyword_classification(complaint_text)
            
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse AI response
            try:
                ai_data = json.loads(result)
                
                # Validate department exists
                dept_code = ai_data.get("department", "municipal")
                if dept_code not in self.departments:
                    dept_code = "municipal"
                
                dept_info = self.departments[dept_code]
                
                return {
                    "success": True,
                    "department": dept_code,
                    "department_name": dept_info["name"],
                    "sub_department": dept_info["sub_departments"][0],
                    "urgency_level": ai_data.get("urgency_level", "medium"),
                    "confidence": ai_data.get("confidence", 0.8),
                    "estimated_resolution_days": dept_info["avg_resolution_days"],
                    "escalation_path": dept_info["escalation"],
                    "reasoning": ai_data.get("reasoning", "AI-based classification"),
                    "classification_method": "ai"
                }
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse AI classification JSON")
                return {"success": False, "error": "Invalid AI response format"}
                
        except Exception as e:
            logger.error(f"AI classification failed: {e}")
            return {"success": False, "error": f"AI classification failed: {str(e)}"}
    
    def _get_keyword_classification(self, complaint_text: str) -> Dict[str, Any]:
        """
        Classify based on keyword matching
        """
        try:
            text_lower = complaint_text.lower()
            best_match = None
            best_score = 0
            
            # Check each department's keywords
            for dept_code, dept_info in self.departments.items():
                score = 0
                matched_keywords = []
                
                for keyword in dept_info["keywords"]:
                    if keyword.lower() in text_lower:
                        score += 1
                        matched_keywords.append(keyword)
                
                if score > best_score:
                    best_score = score
                    best_match = (dept_code, dept_info, matched_keywords)
            
            if best_match and best_score > 0:
                dept_code, dept_info, matched_keywords = best_match
                
                # Determine urgency based on keywords
                urgency = "medium"
                urgency_keywords = ["urgent", "emergency", "critical", "तुरंत", "जल्दी"]
                if any(word in text_lower for word in urgency_keywords):
                    urgency = "high"
                
                return {
                    "success": True,
                    "department": dept_code,
                    "department_name": dept_info["name"],
                    "sub_department": dept_info["sub_departments"][0],
                    "urgency_level": urgency,
                    "confidence": min(0.9, best_score * 0.3),
                    "estimated_resolution_days": dept_info["avg_resolution_days"],
                    "escalation_path": dept_info["escalation"],
                    "reasoning": f"Matched keywords: {', '.join(matched_keywords)}",
                    "classification_method": "keyword"
                }
            
            return {"success": False, "error": "No keywords matched"}
            
        except Exception as e:
            logger.error(f"Keyword classification failed: {e}")
            return {"success": False, "error": f"Keyword classification failed: {str(e)}"}
    
    def get_all_departments(self) -> List[Dict[str, Any]]:
        """
        Get list of all available government departments
        """
        departments_list = []
        
        for dept_code, dept_info in self.departments.items():
            departments_list.append({
                "code": dept_code,
                "name": dept_info["name"],
                "sub_departments": dept_info["sub_departments"],
                "avg_resolution_days": dept_info["avg_resolution_days"],
                "escalation_levels": len(dept_info["escalation"])
            })
        
        return departments_list
    
    def get_department_info(self, dept_code: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific department
        """
        return self.departments.get(dept_code)
    
    async def estimate_resolution_time(
        self, 
        dept_code: str, 
        urgency_level: str,
        complaint_text: str = ""
    ) -> int:
        """
        Estimate resolution time based on department and urgency
        """
        base_days = self.departments.get(dept_code, {}).get("avg_resolution_days", 7)
        
        # Adjust based on urgency
        urgency_multipliers = {
            "critical": 0.3,
            "high": 0.5,
            "medium": 1.0,
            "low": 1.5
        }
        
        multiplier = urgency_multipliers.get(urgency_level, 1.0)
        estimated_days = max(1, int(base_days * multiplier))
        
        return estimated_days
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check if the classifier is working correctly
        """
        try:
            # Test classification
            test_result = await self.classify_complaint(
                "Test complaint for health check",
                location="Test Location"
            )
            
            return {
                "status": "healthy" if test_result["success"] else "degraded",
                "departments_available": len(self.departments),
                "ai_classification": "available" if test_result.get("classification_method") == "ai" else "unavailable",
                "test_result": test_result["success"]
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }