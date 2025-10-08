"""
Video Processing Module for SmartGriev Multimodal Complaint Analysis

This module handles video file processing, including:
- Video validation and preprocessing
- Audio extraction
- Frame extraction for visual analysis
- Video metadata extraction
"""

import os
import logging
import tempfile
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import subprocess
import json

logger = logging.getLogger(__name__)

# Try to import video processing libraries
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV (cv2) not available. Video processing will be limited.")

try:
    import moviepy.editor as mp  # type: ignore
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    mp = None  # type: ignore
    logger.warning("MoviePy not available. Audio extraction will be limited.")


class VideoProcessor:
    """
    Handles video file processing for multimodal complaint analysis.
    """
    
    # Supported video formats
    SUPPORTED_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
    
    # Video size limits (in bytes)
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100 MB
    MAX_VIDEO_DURATION = 300  # 5 minutes in seconds
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        logger.info("VideoProcessor initialized")
    
    def validate_video(self, video_path: str) -> Dict[str, Any]:
        """
        Validate video file format, size, and duration.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dict with validation results and metadata
        """
        try:
            # Check if file exists
            if not os.path.exists(video_path):
                return {
                    'valid': False,
                    'error': 'Video file not found'
                }
            
            # Check file extension
            file_ext = Path(video_path).suffix.lower()
            if file_ext not in self.SUPPORTED_FORMATS:
                return {
                    'valid': False,
                    'error': f'Unsupported video format: {file_ext}. Supported: {", ".join(self.SUPPORTED_FORMATS)}'
                }
            
            # Check file size
            file_size = os.path.getsize(video_path)
            if file_size > self.MAX_VIDEO_SIZE:
                return {
                    'valid': False,
                    'error': f'Video file too large: {file_size / (1024*1024):.2f} MB. Max: {self.MAX_VIDEO_SIZE / (1024*1024)} MB'
                }
            
            # Get video metadata using OpenCV
            if CV2_AVAILABLE:
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    return {
                        'valid': False,
                        'error': 'Unable to open video file'
                    }
                
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                duration = frame_count / fps if fps > 0 else 0
                
                cap.release()
                
                # Check duration
                if duration > self.MAX_VIDEO_DURATION:
                    return {
                        'valid': False,
                        'error': f'Video too long: {duration:.2f}s. Max: {self.MAX_VIDEO_DURATION}s'
                    }
                
                return {
                    'valid': True,
                    'metadata': {
                        'duration': duration,
                        'fps': fps,
                        'frame_count': frame_count,
                        'width': width,
                        'height': height,
                        'file_size': file_size,
                        'format': file_ext
                    }
                }
            else:
                # Basic validation without OpenCV
                return {
                    'valid': True,
                    'metadata': {
                        'file_size': file_size,
                        'format': file_ext
                    }
                }
                
        except Exception as e:
            logger.error(f"Video validation error: {str(e)}")
            return {
                'valid': False,
                'error': f'Validation failed: {str(e)}'
            }
    
    def extract_audio(self, video_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract audio from video file.
        
        Args:
            video_path: Path to the video file
            output_path: Optional output path for audio file
            
        Returns:
            Dict with audio file path and metadata
        """
        try:
            if not MOVIEPY_AVAILABLE:
                return {
                    'success': False,
                    'error': 'MoviePy not available for audio extraction'
                }
            
            # Generate output path if not provided
            if output_path is None:
                output_path = os.path.join(
                    self.temp_dir,
                    f"{Path(video_path).stem}_audio.wav"
                )
            
            # Extract audio using MoviePy
            video = mp.VideoFileClip(video_path)
            
            if video.audio is None:
                return {
                    'success': False,
                    'error': 'No audio track found in video'
                }
            
            video.audio.write_audiofile(output_path, logger=None)
            video.close()
            
            return {
                'success': True,
                'audio_path': output_path,
                'duration': video.duration
            }
            
        except Exception as e:
            logger.error(f"Audio extraction error: {str(e)}")
            return {
                'success': False,
                'error': f'Audio extraction failed: {str(e)}'
            }
    
    def extract_key_frames(self, video_path: str, num_frames: int = 5) -> Dict[str, Any]:
        """
        Extract key frames from video for visual analysis.
        
        Args:
            video_path: Path to the video file
            num_frames: Number of frames to extract
            
        Returns:
            Dict with frame paths and metadata
        """
        try:
            if not CV2_AVAILABLE:
                return {
                    'success': False,
                    'error': 'OpenCV not available for frame extraction'
                }
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {
                    'success': False,
                    'error': 'Unable to open video file'
                }
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_interval = max(1, total_frames // num_frames)
            
            frames = []
            frame_paths = []
            
            for i in range(num_frames):
                frame_number = min(i * frame_interval, total_frames - 1)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                
                ret, frame = cap.read()
                if ret:
                    # Save frame to temp file
                    frame_path = os.path.join(
                        self.temp_dir,
                        f"{Path(video_path).stem}_frame_{i}.jpg"
                    )
                    cv2.imwrite(frame_path, frame)
                    
                    frames.append(frame)
                    frame_paths.append(frame_path)
            
            cap.release()
            
            return {
                'success': True,
                'frame_paths': frame_paths,
                'num_frames': len(frame_paths)
            }
            
        except Exception as e:
            logger.error(f"Frame extraction error: {str(e)}")
            return {
                'success': False,
                'error': f'Frame extraction failed: {str(e)}'
            }
    
    def get_video_thumbnail(self, video_path: str, timestamp: float = 1.0) -> Optional[str]:
        """
        Extract a thumbnail from video at specific timestamp.
        
        Args:
            video_path: Path to the video file
            timestamp: Time in seconds to extract thumbnail
            
        Returns:
            Path to thumbnail image or None
        """
        try:
            if not CV2_AVAILABLE:
                return None
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None
            
            # Set position to timestamp
            cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
            
            ret, frame = cap.read()
            if ret:
                thumbnail_path = os.path.join(
                    self.temp_dir,
                    f"{Path(video_path).stem}_thumbnail.jpg"
                )
                cv2.imwrite(thumbnail_path, frame)
                cap.release()
                return thumbnail_path
            
            cap.release()
            return None
            
        except Exception as e:
            logger.error(f"Thumbnail extraction error: {str(e)}")
            return None


# Global instance
_video_processor = None


def get_video_processor() -> VideoProcessor:
    """Get or create global video processor instance."""
    global _video_processor
    if _video_processor is None:
        _video_processor = VideoProcessor()
    return _video_processor
