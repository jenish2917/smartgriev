"""
Multimodal Analysis Orchestrator for SmartGriev

This module coordinates the complete multimodal complaint analysis pipeline:
1. Video processing
2. Audio analysis
3. Visual analysis  
4. Multimodal fusion
5. Response generation
"""

import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import time

logger = logging.getLogger(__name__)

# Import analysis modules
try:
    from .video_processor import get_video_processor
    from .audio_analyzer import get_audio_analyzer
    from .visual_analyzer import get_visual_analyzer
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    logger.error(f"Failed to import analysis modules: {str(e)}")

# Import AI for response generation
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class MultimodalAnalyzer:
    """
    Orchestrates complete multimodal complaint analysis.
    """
    
    # Department mapping based on complaint content
    DEPARTMENT_MAPPING = {
        'pothole': 'Public Works Department',
        'road': 'Public Works Department',
        'crack': 'Public Works Department',
        'garbage': 'Sanitation Department',
        'trash': 'Sanitation Department',
        'waste': 'Sanitation Department',
        'water': 'Water Supply Department',
        'leak': 'Water Supply Department',
        'pipe': 'Water Supply Department',
        'electrical': 'Electrical Department',
        'streetlight': 'Electrical Department',
        'power': 'Electrical Department',
        'traffic': 'Traffic Department',
        'signal': 'Traffic Department',
        'construction': 'Urban Development Department',
        'building': 'Urban Development Department',
        'noise': 'Environmental Department',
        'pollution': 'Environmental Department'
    }
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """
        Initialize Multimodal Analyzer.
        
        Args:
            groq_api_key: Groq API key for AI response generation
        """
        self.video_processor = get_video_processor() if MODULES_AVAILABLE else None
        self.audio_analyzer = get_audio_analyzer() if MODULES_AVAILABLE else None
        self.visual_analyzer = get_visual_analyzer() if MODULES_AVAILABLE else None
        
        self.groq_client = None
        if GROQ_AVAILABLE and groq_api_key:
            try:
                self.groq_client = Groq(api_key=groq_api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {str(e)}")
        
        logger.info("MultimodalAnalyzer initialized")
    
    def analyze_video_complaint(self, video_path: str) -> Dict[str, Any]:
        """
        Perform complete multimodal analysis of video complaint.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Complete analysis results with AI response
        """
        start_time = time.time()
        
        try:
            # Validate video
            logger.info(f"Validating video: {video_path}")
            validation = self.video_processor.validate_video(video_path)
            
            if not validation.get('valid'):
                return {
                    'success': False,
                    'error': validation.get('error', 'Video validation failed')
                }
            
            # Extract audio
            logger.info("Extracting audio from video")
            audio_result = self.video_processor.extract_audio(video_path)
            
            audio_analysis = None
            if audio_result.get('success'):
                # Analyze audio
                logger.info("Analyzing audio")
                audio_analysis = self.audio_analyzer.analyze_audio(
                    audio_result['audio_path']
                )
            
            # Extract key frames
            logger.info("Extracting key frames")
            frames_result = self.video_processor.extract_key_frames(video_path, num_frames=5)
            
            visual_analysis = None
            if frames_result.get('success'):
                # Analyze frames
                logger.info("Analyzing visual content")
                visual_analysis = self.visual_analyzer.analyze_frames(
                    frames_result['frame_paths']
                )
            
            # Fuse multimodal information
            logger.info("Fusing multimodal data")
            fused_analysis = self._fuse_multimodal_data(
                audio_analysis,
                visual_analysis,
                validation['metadata']
            )
            
            # Generate AI response
            logger.info("Generating AI response")
            ai_response = self._generate_response(fused_analysis)
            
            # Combine all results
            processing_time = time.time() - start_time
            
            result = {
                'success': True,
                'analysis_summary': fused_analysis.get('summary', ''),
                'emotion_detected': fused_analysis.get('emotion', 'unknown'),
                'urgency_level': fused_analysis.get('urgency', 'medium'),
                'identified_objects': fused_analysis.get('objects', []),
                'scene_context': fused_analysis.get('scene', 'unknown'),
                'extracted_text': fused_analysis.get('text', ''),
                'transcribed_audio': fused_analysis.get('transcription', ''),
                'ai_reply': ai_response.get('reply', ''),
                'suggested_department': ai_response.get('department', 'General Administration'),
                'suggested_priority': ai_response.get('priority', 'Medium'),
                'processing_time': processing_time,
                'video_metadata': validation['metadata']
            }
            
            logger.info(f"Analysis completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Video analysis error: {str(e)}")
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }
    
    def _fuse_multimodal_data(
        self,
        audio_analysis: Optional[Dict[str, Any]],
        visual_analysis: Optional[Dict[str, Any]],
        video_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fuse audio and visual analysis results.
        
        Args:
            audio_analysis: Audio analysis results
            visual_analysis: Visual analysis results
            video_metadata: Video metadata
            
        Returns:
            Fused analysis results
        """
        try:
            fused = {
                'summary': '',
                'emotion': 'unknown',
                'urgency': 'medium',
                'objects': [],
                'scene': 'unknown',
                'text': '',
                'transcription': ''
            }
            
            # Extract audio information
            if audio_analysis and audio_analysis.get('success'):
                transcription = audio_analysis.get('transcription', {})
                emotion = audio_analysis.get('emotion', {})
                urgency = audio_analysis.get('urgency', {})
                
                fused['transcription'] = transcription.get('text', '')
                fused['emotion'] = emotion.get('primary_emotion', 'unknown')
                fused['urgency'] = urgency.get('level', 'medium')
            
            # Extract visual information
            if visual_analysis and visual_analysis.get('success'):
                objects = visual_analysis.get('aggregated_objects', [])
                fused['objects'] = [obj['object'] for obj in objects]
                fused['scene'] = visual_analysis.get('dominant_scene', 'unknown')
                fused['text'] = visual_analysis.get('combined_text', '')
            
            # Create summary
            summary_parts = []
            
            if fused['transcription']:
                summary_parts.append(f"User complaint: {fused['transcription'][:200]}")
            
            if fused['objects']:
                obj_str = ', '.join(fused['objects'][:5])
                summary_parts.append(f"Visual evidence shows: {obj_str}")
            
            if fused['scene'] != 'unknown':
                summary_parts.append(f"Location context: {fused['scene']}")
            
            if fused['emotion'] != 'unknown':
                summary_parts.append(f"User is expressing {fused['emotion']}")
            
            fused['summary'] = '. '.join(summary_parts) + '.'
            
            return fused
            
        except Exception as e:
            logger.error(f"Multimodal fusion error: {str(e)}")
            return {
                'summary': 'Error processing complaint data',
                'emotion': 'unknown',
                'urgency': 'medium',
                'objects': [],
                'scene': 'unknown',
                'text': '',
                'transcription': ''
            }
    
    def _generate_response(self, fused_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate empathetic AI response based on analysis.
        
        Args:
            fused_analysis: Fused analysis results
            
        Returns:
            AI-generated response with department and priority
        """
        try:
            # Determine department
            department = self._determine_department(fused_analysis)
            
            # Determine priority
            priority = self._determine_priority(fused_analysis)
            
            # Generate empathetic reply
            if self.groq_client:
                reply = self._generate_ai_reply_groq(fused_analysis, department, priority)
            else:
                reply = self._generate_template_reply(fused_analysis, department, priority)
            
            return {
                'reply': reply,
                'department': department,
                'priority': priority
            }
            
        except Exception as e:
            logger.error(f"Response generation error: {str(e)}")
            return {
                'reply': "Thank you for submitting your complaint. We will review it and take appropriate action.",
                'department': 'General Administration',
                'priority': 'Medium'
            }
    
    def _determine_department(self, fused_analysis: Dict[str, Any]) -> str:
        """Determine appropriate department based on analysis."""
        # Check objects
        for obj in fused_analysis.get('objects', []):
            obj_lower = obj.lower()
            for keyword, dept in self.DEPARTMENT_MAPPING.items():
                if keyword in obj_lower:
                    return dept
        
        # Check transcription
        transcription = fused_analysis.get('transcription', '').lower()
        for keyword, dept in self.DEPARTMENT_MAPPING.items():
            if keyword in transcription:
                return dept
        
        return 'General Administration'
    
    def _determine_priority(self, fused_analysis: Dict[str, Any]) -> str:
        """Determine priority level based on urgency and emotion."""
        urgency = fused_analysis.get('urgency', 'medium')
        emotion = fused_analysis.get('emotion', 'neutral')
        
        if urgency == 'high' or emotion in ['anger', 'anxiety']:
            return 'High'
        elif urgency == 'medium' or emotion == 'frustration':
            return 'Medium'
        else:
            return 'Low'
    
    def _generate_ai_reply_groq(
        self,
        fused_analysis: Dict[str, Any],
        department: str,
        priority: str
    ) -> str:
        """Generate AI reply using Groq."""
        try:
            prompt = f"""You are an empathetic government complaint response assistant for SmartGriev system.

Generate a brief, empathetic response to a citizen's complaint based on this analysis:

Summary: {fused_analysis.get('summary', 'Complaint received')}
Emotion: {fused_analysis.get('emotion', 'unknown')}
Urgency: {fused_analysis.get('urgency', 'medium')}
Department: {department}
Priority: {priority}

Requirements:
1. Be empathetic and acknowledge the citizen's concern
2. Briefly mention what was understood from their complaint
3. Confirm it will be forwarded to {department}
4. Mention priority level: {priority}
5. Keep response under 100 words
6. Be professional yet warm

Generate only the response text, nothing else."""

            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Groq AI generation error: {str(e)}")
            return self._generate_template_reply(fused_analysis, department, priority)
    
    def _generate_template_reply(
        self,
        fused_analysis: Dict[str, Any],
        department: str,
        priority: str
    ) -> str:
        """Generate template-based reply as fallback."""
        emotion = fused_analysis.get('emotion', 'neutral')
        
        # Empathetic opening
        if emotion == 'anger':
            opening = "I understand your frustration, and I apologize for the inconvenience you're experiencing."
        elif emotion == 'anxiety':
            opening = "I understand your concern and want to assure you that we're here to help."
        elif emotion == 'frustration':
            opening = "I appreciate you taking the time to report this issue."
        else:
            opening = "Thank you for bringing this matter to our attention."
        
        # Main response
        objects_str = ', '.join(fused_analysis.get('objects', [])[:3]) if fused_analysis.get('objects') else 'the issue'
        main = f"Based on your complaint regarding {objects_str}, this has been registered as a {priority.lower()} priority case."
        
        # Action statement
        action = f"It will be immediately forwarded to the {department} for prompt resolution."
        
        # Closing
        closing = "We will keep you updated on the progress. Thank you for your patience."
        
        return f"{opening} {main} {action} {closing}"


# Global instance
_multimodal_analyzer = None


def get_multimodal_analyzer(groq_api_key: Optional[str] = None) -> MultimodalAnalyzer:
    """Get or create global multimodal analyzer instance."""
    global _multimodal_analyzer
    if _multimodal_analyzer is None:
        _multimodal_analyzer = MultimodalAnalyzer(groq_api_key)
    return _multimodal_analyzer
