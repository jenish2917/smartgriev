# Advanced Department Classification System
# Classifies complaints into appropriate government departments

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

from groq import Groq
from django.conf import settings
from django.core.cache import cache

from .models import Department, Complaint

logger = logging.getLogger(__name__)

@dataclass
class ClassificationResult:
    """Result of department classification"""
    primary_department: str
    secondary_departments: List[str]
    confidence: float
    reasoning: str
    urgency_level: str
    estimated_resolution_time: str
    required_documents: List[str]
    escalation_path: List[str]

class GovernmentDepartmentClassifier:
    """
    Advanced classifier for routing complaints to appropriate government departments
    Uses AI to understand context and classify based on Indian government structure
    """
    
    def __init__(self):
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        self.department_mapping = self.load_department_mapping()
        
    def load_department_mapping(self) -> Dict:
        """Load comprehensive government department mapping"""
        return {
            # Infrastructure & Urban Development
            "road_infrastructure": {
                "keywords": ["road", "highway", "bridge", "flyover", "underpass", "traffic", "signal", "pothole", "street light"],
                "department": "Ministry of Road Transport and Highways",
                "local_dept": "Municipal Corporation - Roads Division",
                "urgency_mapping": {
                    "critical": "24 hours",
                    "high": "3-5 days", 
                    "medium": "1-2 weeks",
                    "low": "2-4 weeks"
                }
            },
            
            # Utilities
            "electricity": {
                "keywords": ["electricity", "power", "outage", "transformer", "cable", "meter", "bill", "connection"],
                "department": "Ministry of Power",
                "local_dept": "State Electricity Board",
                "urgency_mapping": {
                    "critical": "4-6 hours",
                    "high": "24 hours",
                    "medium": "3-5 days", 
                    "low": "1 week"
                }
            },
            
            "water_supply": {
                "keywords": ["water", "supply", "pipe", "leakage", "sewage", "drainage", "toilet", "sanitation"],
                "department": "Ministry of Jal Shakti",
                "local_dept": "Water Supply Department",
                "urgency_mapping": {
                    "critical": "2-4 hours",
                    "high": "12 hours",
                    "medium": "2-3 days",
                    "low": "1 week"
                }
            },
            
            "waste_management": {
                "keywords": ["garbage", "waste", "trash", "collection", "bin", "dump", "cleanliness", "sweeping"],
                "department": "Ministry of Housing and Urban Affairs",
                "local_dept": "Municipal Corporation - Sanitation Department",
                "urgency_mapping": {
                    "critical": "24 hours",
                    "high": "2-3 days",
                    "medium": "1 week",
                    "low": "2 weeks"
                }
            },
            
            # Healthcare
            "healthcare_services": {
                "keywords": ["hospital", "doctor", "medicine", "health", "medical", "emergency", "ambulance", "clinic"],
                "department": "Ministry of Health and Family Welfare", 
                "local_dept": "District Health Department",
                "urgency_mapping": {
                    "critical": "Immediate",
                    "high": "2-4 hours",
                    "medium": "24 hours",
                    "low": "3-5 days"
                }
            },
            
            # Education
            "education_services": {
                "keywords": ["school", "college", "education", "teacher", "student", "books", "scholarship", "admission"],
                "department": "Ministry of Education",
                "local_dept": "District Education Office",
                "urgency_mapping": {
                    "critical": "24 hours",
                    "high": "3-5 days",
                    "medium": "1-2 weeks",
                    "low": "3-4 weeks"
                }
            },
            
            # Social Services
            "social_welfare": {
                "keywords": ["pension", "welfare", "disability", "senior citizen", "widow", "benefits", "ration", "pds"],
                "department": "Ministry of Social Justice and Empowerment",
                "local_dept": "District Social Welfare Office",
                "urgency_mapping": {
                    "critical": "3-5 days",
                    "high": "1 week",
                    "medium": "2-3 weeks",
                    "low": "1 month"
                }
            },
            
            # Law & Order
            "police_security": {
                "keywords": ["police", "crime", "theft", "assault", "harassment", "security", "safety", "violence"],
                "department": "Ministry of Home Affairs",
                "local_dept": "Local Police Station",
                "urgency_mapping": {
                    "critical": "Immediate",
                    "high": "1-2 hours",
                    "medium": "24 hours",
                    "low": "3-5 days"
                }
            },
            
            # Revenue & Documentation
            "revenue_documents": {
                "keywords": ["property", "land", "registration", "certificate", "license", "permit", "tax", "revenue"],
                "department": "Ministry of Revenue",
                "local_dept": "Tehsil/Revenue Office",
                "urgency_mapping": {
                    "critical": "1 week",
                    "high": "2 weeks",
                    "medium": "3-4 weeks",
                    "low": "1-2 months"
                }
            },
            
            # Employment
            "employment_services": {
                "keywords": ["job", "employment", "unemployment", "skill", "training", "livelihood", "work"],
                "department": "Ministry of Skill Development and Entrepreneurship",
                "local_dept": "District Employment Office",
                "urgency_mapping": {
                    "critical": "1 week",
                    "high": "2-3 weeks",
                    "medium": "1 month",
                    "low": "6-8 weeks"
                }
            },
            
            # Agriculture
            "agriculture_services": {
                "keywords": ["farming", "crop", "agriculture", "irrigation", "fertilizer", "seeds", "farmer", "subsidy"],
                "department": "Ministry of Agriculture and Farmers Welfare",
                "local_dept": "District Agriculture Office",
                "urgency_mapping": {
                    "critical": "24-48 hours",
                    "high": "3-5 days",
                    "medium": "1-2 weeks",
                    "low": "3-4 weeks"
                }
            }
        }
    
    async def classify_complaint(self, complaint_text: str, location: str = None) -> Dict[str, Any]:
        """Classify complaint into appropriate department with detailed analysis"""
        try:
            # Get AI-powered classification
            classification = await self.get_ai_classification(processing_result)
            
            # Determine urgency level
            urgency = await self.determine_urgency(processing_result)
            
            # Get department details
            dept_info = self.get_department_info(classification["primary_department"])
            
            # Estimate resolution time
            resolution_time = self.estimate_resolution_time(
                classification["primary_department"], 
                urgency
            )
            
            # Determine required documents
            required_docs = await self.get_required_documents(processing_result, classification)
            
            # Create escalation path
            escalation_path = self.create_escalation_path(classification["primary_department"])
            
            return ClassificationResult(
                primary_department=classification["primary_department"],
                secondary_departments=classification["secondary_departments"],
                confidence=classification["confidence"],
                reasoning=classification["reasoning"],
                urgency_level=urgency,
                estimated_resolution_time=resolution_time,
                required_documents=required_docs,
                escalation_path=escalation_path
            )
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return self.get_fallback_classification()
    
    async def get_ai_classification(self, processing_result: ProcessingResult) -> Dict:
        """Use AI to classify the complaint"""
        try:
            # Prepare department options
            dept_options = "\n".join([
                f"- {key}: {info['department']} ({info['local_dept']})"
                for key, info in self.department_mapping.items()
            ])
            
            response = await self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are an expert in Indian government department classification.
                        Classify the complaint into the most appropriate department.
                        
                        Available departments:
                        {dept_options}
                        
                        Return JSON with:
                        - primary_department: main department key
                        - secondary_departments: list of related department keys
                        - confidence: confidence score (0-1)
                        - reasoning: why this classification was chosen
                        
                        Consider the complaint text, entities, and context.
                        """
                    },
                    {
                        "role": "user",
                        "content": f"""
                        Complaint Text: {processing_result.text}
                        Processing Type: {processing_result.processing_type}
                        Extracted Entities: {processing_result.extracted_entities}
                        Confidence: {processing_result.confidence}
                        
                        Classify this complaint.
                        """
                    }
                ],
                temperature=0.2
            )
            
            import json
            classification = json.loads(response.choices[0].message.content)
            return classification
            
        except Exception as e:
            logger.error(f"AI classification failed: {e}")
            return self.get_keyword_based_classification(processing_result)
    
    def get_keyword_based_classification(self, processing_result: ProcessingResult) -> Dict:
        """Fallback keyword-based classification"""
        text = processing_result.text.lower()
        scores = {}
        
        for dept_key, dept_info in self.department_mapping.items():
            score = 0
            for keyword in dept_info["keywords"]:
                if keyword in text:
                    score += 1
            scores[dept_key] = score / len(dept_info["keywords"])
        
        # Get best match
        primary_dept = max(scores, key=scores.get) if scores else "road_infrastructure"
        confidence = scores.get(primary_dept, 0.1)
        
        # Get secondary departments (score > 0.2)
        secondary_depts = [
            dept for dept, score in scores.items() 
            if score > 0.2 and dept != primary_dept
        ]
        
        return {
            "primary_department": primary_dept,
            "secondary_departments": secondary_depts[:2],  # Max 2 secondary
            "confidence": confidence,
            "reasoning": f"Keyword-based classification with {confidence:.2f} confidence"
        }
    
    async def determine_urgency(self, processing_result: ProcessingResult) -> str:
        """Determine urgency level of the complaint"""
        try:
            response = await self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": """Determine the urgency level of this complaint.
                        
                        Urgency levels:
                        - critical: Life-threatening, emergency situations, major infrastructure failure
                        - high: Significant impact on daily life, safety concerns, multiple people affected
                        - medium: Moderate inconvenience, localized issues, standard service requests
                        - low: Minor issues, routine maintenance, non-urgent improvements
                        
                        Return only the urgency level: critical, high, medium, or low
                        """
                    },
                    {
                        "role": "user",
                        "content": f"Complaint: {processing_result.text}\nEntities: {processing_result.extracted_entities}"
                    }
                ],
                temperature=0.1
            )
            
            urgency = response.choices[0].message.content.strip().lower()
            return urgency if urgency in ["critical", "high", "medium", "low"] else "medium"
            
        except Exception as e:
            logger.error(f"Urgency determination failed: {e}")
            return "medium"
    
    def get_department_info(self, dept_key: str) -> Dict:
        """Get department information"""
        return self.department_mapping.get(dept_key, self.department_mapping["road_infrastructure"])
    
    def estimate_resolution_time(self, dept_key: str, urgency: str) -> str:
        """Estimate resolution time based on department and urgency"""
        dept_info = self.get_department_info(dept_key)
        return dept_info["urgency_mapping"].get(urgency, "2-4 weeks")
    
    async def get_required_documents(self, processing_result: ProcessingResult, classification: Dict) -> List[str]:
        """Determine required documents for the complaint"""
        try:
            response = await self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": """Based on the complaint and department classification, list the documents 
                        that might be required for processing this complaint in Indian government context.
                        
                        Return a JSON list of document names like:
                        ["Identity Proof (Aadhaar/Voter ID)", "Address Proof", "Photograph of Issue", "Property Documents"]
                        
                        Keep it realistic and relevant to the complaint type.
                        """
                    },
                    {
                        "role": "user",
                        "content": f"Complaint: {processing_result.text}\nDepartment: {classification['primary_department']}"
                    }
                ],
                temperature=0.3
            )
            
            import json
            documents = json.loads(response.choices[0].message.content)
            return documents if isinstance(documents, list) else []
            
        except Exception as e:
            logger.error(f"Document determination failed: {e}")
            return ["Identity Proof", "Address Proof", "Supporting Documents"]
    
    def create_escalation_path(self, dept_key: str) -> List[str]:
        """Create escalation path for the complaint"""
        dept_info = self.get_department_info(dept_key)
        
        escalation = [
            f"Level 1: {dept_info['local_dept']}",
            f"Level 2: District Officer",
            f"Level 3: {dept_info['department']}",
            "Level 4: Chief Minister's Office",
            "Level 5: Prime Minister's Office"
        ]
        
        return escalation
    
    def get_fallback_classification(self) -> ClassificationResult:
        """Fallback classification when all else fails"""
        return ClassificationResult(
            primary_department="road_infrastructure",
            secondary_departments=[],
            confidence=0.3,
            reasoning="Fallback classification - manual review required",
            urgency_level="medium",
            estimated_resolution_time="2-3 weeks",
            required_documents=["Identity Proof", "Address Proof"],
            escalation_path=[
                "Level 1: Municipal Corporation",
                "Level 2: District Collector", 
                "Level 3: State Government",
                "Level 4: Central Government"
            ]
        )

# Initialize global classifier
department_classifier = GovernmentDepartmentClassifier()