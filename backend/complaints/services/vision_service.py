"""
Gemini Vision Service for SmartGriev
Handles image and video analysis using Gemini 1.5 Pro Vision API
"""

import os
import logging
import google.generativeai as genai
from typing import Dict, Any, List, Optional
from pathlib import Path
from PIL import Image
import mimetypes

logger = logging.getLogger(__name__)


class GeminiVisionService:
    """
    Vision AI service using Gemini 1.5 Pro Vision for image/video analysis
    """
    
    # Supported image formats
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif'}
    
    # Supported video formats
    SUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
    
    # Maximum file sizes (in MB)
    MAX_IMAGE_SIZE_MB = 20
    MAX_VIDEO_SIZE_MB = 100
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini Vision Service
        
        Args:
            api_key: Google AI API key (defaults to environment variable or Django settings)
        """
        from django.conf import settings
        
        self.api_key = (
            api_key or 
            os.getenv('GOOGLE_AI_API_KEY') or 
            getattr(settings, 'GOOGLE_AI_API_KEY', None) or
            getattr(settings, 'GEMINI_API_KEY', None)
        )
        if not self.api_key:
            raise ValueError("GOOGLE_AI_API_KEY not found in environment variables or Django settings")
        
        genai.configure(api_key=self.api_key)
        
        # Use Gemini 1.5 Pro for vision tasks (supports multimodal input)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        logger.info("GeminiVisionService initialized with Gemini 1.5 Pro")
    
    def analyze_image(
        self,
        image_path: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze an image for civic complaints
        
        Args:
            image_path: Path to the image file
            context: Optional context about the complaint
            
        Returns:
            Analysis results with issue detection, severity, description
        """
        try:
            # Validate image file
            validation = self._validate_image(image_path)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': validation['error']
                }
            
            # Load image
            image = Image.open(image_path)
            
            # Prepare analysis prompt
            prompt = self._create_image_analysis_prompt(context)
            
            # Generate analysis
            response = self.model.generate_content([prompt, image])
            
            # Parse response
            result = self._parse_vision_response(response.text)
            
            return {
                'success': True,
                'issue_type': result.get('issue_type', 'Unknown'),
                'severity': result.get('severity', 'Medium'),
                'description': result.get('description', ''),
                'detected_objects': result.get('detected_objects', []),
                'location_context': result.get('location_context', ''),
                'suggested_department': result.get('suggested_department', 'Other'),
                'urgency': result.get('urgency', 'medium'),
                'raw_analysis': response.text,
                'metadata': validation['metadata']
            }
            
        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            return {
                'success': False,
                'error': f'Image analysis failed: {str(e)}'
            }
    
    def analyze_video(
        self,
        video_path: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a video for civic complaints (extracts key frames)
        
        Args:
            video_path: Path to the video file
            context: Optional context about the complaint
            
        Returns:
            Analysis results aggregated from video frames
        """
        try:
            # Validate video file
            validation = self._validate_video(video_path)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': validation['error']
                }
            
            # Upload video to Gemini
            logger.info(f"Uploading video: {video_path}")
            video_file = genai.upload_file(video_path)
            
            # Wait for processing
            import time
            while video_file.state.name == "PROCESSING":
                time.sleep(2)
                video_file = genai.get_file(video_file.name)
            
            if video_file.state.name == "FAILED":
                return {
                    'success': False,
                    'error': 'Video processing failed'
                }
            
            # Prepare analysis prompt
            prompt = self._create_video_analysis_prompt(context)
            
            # Generate analysis
            response = self.model.generate_content([video_file, prompt])
            
            # Parse response
            result = self._parse_vision_response(response.text)
            
            # Clean up uploaded file
            genai.delete_file(video_file.name)
            
            return {
                'success': True,
                'issue_type': result.get('issue_type', 'Unknown'),
                'severity': result.get('severity', 'Medium'),
                'description': result.get('description', ''),
                'detected_objects': result.get('detected_objects', []),
                'location_context': result.get('location_context', ''),
                'suggested_department': result.get('suggested_department', 'Other'),
                'urgency': result.get('urgency', 'medium'),
                'key_observations': result.get('key_observations', []),
                'raw_analysis': response.text,
                'metadata': validation['metadata']
            }
            
        except Exception as e:
            logger.error(f"Video analysis failed: {str(e)}")
            return {
                'success': False,
                'error': f'Video analysis failed: {str(e)}'
            }
    
    def analyze_multiple_images(
        self,
        image_paths: List[str],
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze multiple images together for comprehensive complaint analysis
        
        Args:
            image_paths: List of image file paths
            context: Optional context about the complaint
            
        Returns:
            Aggregated analysis results
        """
        try:
            if not image_paths:
                return {
                    'success': False,
                    'error': 'No images provided'
                }
            
            # Load all images
            images = []
            for path in image_paths:
                validation = self._validate_image(path)
                if validation['valid']:
                    images.append(Image.open(path))
            
            if not images:
                return {
                    'success': False,
                    'error': 'No valid images found'
                }
            
            # Prepare prompt for multiple images
            prompt = self._create_multi_image_analysis_prompt(context, len(images))
            
            # Generate analysis with all images
            content = [prompt] + images
            response = self.model.generate_content(content)
            
            # Parse response
            result = self._parse_vision_response(response.text)
            
            return {
                'success': True,
                'issue_type': result.get('issue_type', 'Unknown'),
                'severity': result.get('severity', 'Medium'),
                'description': result.get('description', ''),
                'detected_objects': result.get('detected_objects', []),
                'location_context': result.get('location_context', ''),
                'suggested_department': result.get('suggested_department', 'Other'),
                'urgency': result.get('urgency', 'medium'),
                'key_observations': result.get('key_observations', []),
                'images_analyzed': len(images),
                'raw_analysis': response.text
            }
            
        except Exception as e:
            logger.error(f"Multiple image analysis failed: {str(e)}")
            return {
                'success': False,
                'error': f'Multiple image analysis failed: {str(e)}'
            }
    
    def _validate_image(self, image_path: str) -> Dict[str, Any]:
        """Validate image file format and size"""
        try:
            if not os.path.exists(image_path):
                return {'valid': False, 'error': 'Image file not found'}
            
            # Check file extension
            file_ext = Path(image_path).suffix.lower()
            if file_ext not in self.SUPPORTED_IMAGE_FORMATS:
                return {
                    'valid': False,
                    'error': f'Unsupported image format: {file_ext}'
                }
            
            # Check file size
            file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
            if file_size_mb > self.MAX_IMAGE_SIZE_MB:
                return {
                    'valid': False,
                    'error': f'Image too large: {file_size_mb:.2f}MB (max: {self.MAX_IMAGE_SIZE_MB}MB)'
                }
            
            # Get image metadata
            with Image.open(image_path) as img:
                metadata = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height,
                    'file_size_mb': file_size_mb
                }
            
            return {
                'valid': True,
                'metadata': metadata
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Image validation failed: {str(e)}'
            }
    
    def _validate_video(self, video_path: str) -> Dict[str, Any]:
        """Validate video file format and size"""
        try:
            if not os.path.exists(video_path):
                return {'valid': False, 'error': 'Video file not found'}
            
            # Check file extension
            file_ext = Path(video_path).suffix.lower()
            if file_ext not in self.SUPPORTED_VIDEO_FORMATS:
                return {
                    'valid': False,
                    'error': f'Unsupported video format: {file_ext}'
                }
            
            # Check file size
            file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            if file_size_mb > self.MAX_VIDEO_SIZE_MB:
                return {
                    'valid': False,
                    'error': f'Video too large: {file_size_mb:.2f}MB (max: {self.MAX_VIDEO_SIZE_MB}MB)'
                }
            
            metadata = {
                'format': file_ext,
                'file_size_mb': file_size_mb
            }
            
            return {
                'valid': True,
                'metadata': metadata
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Video validation failed: {str(e)}'
            }
    
    def _create_image_analysis_prompt(self, context: Optional[str] = None) -> str:
        """Create detailed prompt for image analysis"""
        base_prompt = """Analyze this image for a civic complaint in India. Provide a detailed analysis in JSON format:

{
    "issue_type": "Brief name of the issue (e.g., 'Pothole', 'Garbage Accumulation', 'Street Light Broken')",
    "severity": "Low | Medium | High | Critical",
    "description": "Detailed description of the issue visible in the image",
    "detected_objects": ["list", "of", "visible", "objects", "related", "to", "complaint"],
    "location_context": "Description of location type (e.g., 'residential area', 'main road', 'park')",
    "suggested_department": "Water Supply | Electricity | Roads | Sanitation | Streetlights | Waste Management | Parks & Gardens | Building Permits | Fire Safety | Other",
    "urgency": "low | medium | high | critical",
    "key_observations": ["observation1", "observation2", "..."]
}

IMPORTANT:
- Focus on civic infrastructure issues (roads, water, electricity, sanitation, etc.)
- Assess severity based on safety risk and impact on daily life
- Be specific in descriptions
- Identify all visible damage, defects, or hazards
"""
        
        if context:
            base_prompt += f"\n\nAdditional context provided by user:\n{context}"
        
        return base_prompt
    
    def _create_video_analysis_prompt(self, context: Optional[str] = None) -> str:
        """Create detailed prompt for video analysis"""
        base_prompt = """Analyze this video for a civic complaint in India. Watch the entire video and provide a comprehensive analysis in JSON format:

{
    "issue_type": "Brief name of the issue",
    "severity": "Low | Medium | High | Critical",
    "description": "Detailed description of the issue shown in the video",
    "detected_objects": ["list", "of", "visible", "objects"],
    "location_context": "Description of location type",
    "suggested_department": "Water Supply | Electricity | Roads | Sanitation | Streetlights | Waste Management | Parks & Gardens | Building Permits | Fire Safety | Other",
    "urgency": "low | medium | high | critical",
    "key_observations": ["timeline", "of", "important", "events", "in", "video"]
}

IMPORTANT:
- Analyze the video timeline chronologically
- Note any changes or progression of the issue
- Identify safety hazards
- Look for context clues about location and time
"""
        
        if context:
            base_prompt += f"\n\nAdditional context provided by user:\n{context}"
        
        return base_prompt
    
    def _create_multi_image_analysis_prompt(
        self,
        context: Optional[str] = None,
        num_images: int = 0
    ) -> str:
        """Create prompt for analyzing multiple images together"""
        base_prompt = f"""Analyze these {num_images} images together for a civic complaint in India. These images show different angles or aspects of the same issue. Provide a comprehensive analysis in JSON format:

{{
    "issue_type": "Brief name of the issue",
    "severity": "Low | Medium | High | Critical",
    "description": "Comprehensive description combining insights from all images",
    "detected_objects": ["list", "of", "all", "visible", "objects"],
    "location_context": "Description of location type",
    "suggested_department": "Water Supply | Electricity | Roads | Sanitation | Streetlights | Waste Management | Parks & Gardens | Building Permits | Fire Safety | Other",
    "urgency": "low | medium | high | critical",
    "key_observations": ["observation1", "observation2", "..."]
}}

IMPORTANT:
- Combine information from all images for complete understanding
- Note any progression or different perspectives shown
- Provide a unified severity assessment
"""
        
        if context:
            base_prompt += f"\n\nAdditional context provided by user:\n{context}"
        
        return base_prompt
    
    def _parse_vision_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini vision response into structured data"""
        try:
            # Try to extract JSON from response
            import json
            import re
            
            # Find JSON block in response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                return result
            
            # Fallback: Return raw text if JSON parsing fails
            return {
                'issue_type': 'Unknown',
                'severity': 'Medium',
                'description': response_text,
                'detected_objects': [],
                'location_context': '',
                'suggested_department': 'Other',
                'urgency': 'medium',
                'key_observations': []
            }
            
        except Exception as e:
            logger.warning(f"Failed to parse vision response: {str(e)}")
            return {
                'issue_type': 'Unknown',
                'severity': 'Medium',
                'description': response_text,
                'detected_objects': [],
                'location_context': '',
                'suggested_department': 'Other',
                'urgency': 'medium',
                'key_observations': []
            }


# Global instance
_vision_service = None

def get_vision_service(api_key: Optional[str] = None) -> GeminiVisionService:
    """Get or create global GeminiVisionService instance"""
    global _vision_service
    if _vision_service is None:
        _vision_service = GeminiVisionService(api_key)
    return _vision_service
