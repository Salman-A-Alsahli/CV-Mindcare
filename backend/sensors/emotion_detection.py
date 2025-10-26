"""
Face Detection and Emotion Analysis Module
------------------------------------------
Provides real-time emotion detection using DeepFace library with multiple model support.
"""

import numpy as np
import cv2
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import logging
from pathlib import Path

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    logging.warning("DeepFace not available. Install with: pip install deepface")

from .base import BaseSensor, SensorUnavailableError

logger = logging.getLogger(__name__)


class EmotionDetector(BaseSensor):
    """
    Emotion detection sensor using DeepFace.
    
    Supports multiple models and provides real-time emotion classification
    from webcam feed with confidence scoring.
    """
    
    # Available DeepFace models
    AVAILABLE_MODELS = [
        "VGG-Face",
        "Facenet",
        "Facenet512", 
        "OpenFace",
        "DeepFace",
        "DeepID",
        "ArcFace",
        "Dlib",
        "SFace"
    ]
    
    # Emotion categories (DeepFace standard)
    EMOTIONS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
    
    def __init__(
        self,
        camera_index: int = 0,
        model_name: str = "VGG-Face",
        confidence_threshold: float = 0.5,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize emotion detector.
        
        Args:
            camera_index: Camera device index (default 0)
            model_name: DeepFace model to use (default VGG-Face)
            confidence_threshold: Minimum confidence for valid detection (0.0-1.0)
            config: Optional configuration dictionary
        """
        super().__init__(
            name=f"Emotion Detector ({model_name})",
            sensor_type="emotion_detection",
            config=config or {}
        )
        
        self.camera_index = camera_index
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.cap: Optional[cv2.VideoCapture] = None
        
        # Emotion history for smoothing
        self.emotion_history: List[Dict[str, float]] = []
        self.history_size = 10
        
        # Validate model name
        if model_name not in self.AVAILABLE_MODELS:
            logger.warning(
                f"Model '{model_name}' not in available models. "
                f"Using 'VGG-Face' instead."
            )
            self.model_name = "VGG-Face"
    
    def initialize(self) -> bool:
        """
        Initialize the emotion detector and camera.
        
        Returns:
            bool: True if initialization successful
        """
        if not DEEPFACE_AVAILABLE:
            raise SensorUnavailableError(
                "DeepFace library not available. "
                "Install with: pip install deepface tensorflow"
            )
        
        try:
            # Test camera availability
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                raise SensorUnavailableError(
                    f"Camera {self.camera_index} not available"
                )
            
            # Test camera read
            ret, frame = self.cap.read()
            if not ret or frame is None:
                raise SensorUnavailableError(
                    f"Camera {self.camera_index} failed to capture frame"
                )
            
            logger.info(
                f"Emotion detector initialized with {self.model_name} model"
            )
            return True
            
        except SensorUnavailableError:
            raise
        except Exception as e:
            logger.error(f"Error initializing emotion detector: {e}")
            if self.cap:
                self.cap.release()
                self.cap = None
            return False
    
    def capture(self) -> Dict[str, Any]:
        """
        Capture frame and analyze emotions.
        
        Returns:
            Dict containing emotion analysis results
        """
        if not self.is_active():
            return {
                "timestamp": datetime.now().isoformat(),
                "sensor_type": self.sensor_type,
                "available": False,
                "error": "Sensor not active"
            }
        
        try:
            # Capture frame
            ret, frame = self.cap.read()
            if not ret or frame is None:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "sensor_type": self.sensor_type,
                    "available": False,
                    "error": "Failed to capture frame"
                }
            
            # Analyze emotions
            result = self._analyze_frame(frame)
            result["timestamp"] = datetime.now().isoformat()
            result["sensor_type"] = self.sensor_type
            
            return result
            
        except Exception as e:
            logger.error(f"Error during emotion capture: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "sensor_type": self.sensor_type,
                "available": False,
                "error": str(e)
            }
    
    def cleanup(self) -> bool:
        """
        Clean up camera resources.
        
        Returns:
            bool: True if cleanup successful
        """
        try:
            if self.cap:
                self.cap.release()
                self.cap = None
            
            # Clear emotion history
            self.emotion_history.clear()
            
            logger.info("Emotion detector cleaned up successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during emotion detector cleanup: {e}")
            return False
    
    def _analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Analyze a single frame for emotions.
        
        Args:
            frame: OpenCV frame (BGR format)
            
        Returns:
            Dict with emotion analysis results
        """
        try:
            # DeepFace expects RGB, OpenCV uses BGR
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Analyze emotions
            result = DeepFace.analyze(
                img_path=rgb_frame,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv',
                silent=True
            )
            
            # Handle both single face and multiple faces
            if isinstance(result, list):
                if len(result) == 0:
                    return self._no_face_result()
                # Use first detected face
                result = result[0]
            
            # Extract emotion data
            emotions = result.get('emotion', {})
            region = result.get('region', {})
            
            # Find dominant emotion
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])
            
            # Calculate overall confidence
            confidence = dominant_emotion[1] / 100.0  # Convert percentage to 0-1
            
            # Add to history for smoothing
            self._update_history(emotions)
            
            # Get smoothed emotions
            smoothed_emotions = self._get_smoothed_emotions()
            smoothed_dominant = max(smoothed_emotions.items(), key=lambda x: x[1])
            
            return {
                "available": True,
                "face_detected": True,
                "dominant_emotion": dominant_emotion[0],
                "dominant_confidence": round(confidence, 3),
                "emotions": {k: round(v / 100.0, 3) for k, v in emotions.items()},
                "smoothed_dominant_emotion": smoothed_dominant[0],
                "smoothed_emotions": smoothed_emotions,
                "face_coordinates": {
                    "x": region.get('x', 0),
                    "y": region.get('y', 0),
                    "w": region.get('w', 0),
                    "h": region.get('h', 0)
                },
                "model_used": self.model_name,
                "meets_threshold": confidence >= self.confidence_threshold
            }
            
        except ValueError as e:
            # No face detected
            logger.debug(f"No face detected: {e}")
            return self._no_face_result()
            
        except Exception as e:
            logger.error(f"Error analyzing frame: {e}")
            return {
                "available": False,
                "error": str(e)
            }
    
    def _no_face_result(self) -> Dict[str, Any]:
        """Return result structure when no face is detected."""
        return {
            "available": True,
            "face_detected": False,
            "dominant_emotion": "neutral",
            "dominant_confidence": 0.0,
            "emotions": {emotion: 0.0 for emotion in self.EMOTIONS},
            "smoothed_dominant_emotion": "neutral",
            "smoothed_emotions": {emotion: 0.0 for emotion in self.EMOTIONS},
            "face_coordinates": None,
            "model_used": self.model_name,
            "meets_threshold": False
        }
    
    def _update_history(self, emotions: Dict[str, float]) -> None:
        """
        Update emotion history for smoothing.
        
        Args:
            emotions: Current emotion scores
        """
        # Normalize emotions to 0-1 range
        normalized = {k: v / 100.0 for k, v in emotions.items()}
        
        self.emotion_history.append(normalized)
        
        # Keep only recent history
        if len(self.emotion_history) > self.history_size:
            self.emotion_history.pop(0)
    
    def _get_smoothed_emotions(self) -> Dict[str, float]:
        """
        Calculate smoothed emotion scores from history.
        
        Returns:
            Dict of smoothed emotion scores
        """
        if not self.emotion_history:
            return {emotion: 0.0 for emotion in self.EMOTIONS}
        
        # Calculate average for each emotion
        smoothed = {}
        for emotion in self.EMOTIONS:
            scores = [h.get(emotion, 0.0) for h in self.emotion_history]
            smoothed[emotion] = round(np.mean(scores), 3)
        
        return smoothed
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze emotions from an image file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dict with emotion analysis results
        """
        try:
            frame = cv2.imread(image_path)
            if frame is None:
                return {
                    "available": False,
                    "error": f"Failed to load image: {image_path}"
                }
            
            result = self._analyze_frame(frame)
            result["timestamp"] = datetime.now().isoformat()
            result["sensor_type"] = self.sensor_type
            result["source"] = image_path
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {
                "available": False,
                "error": str(e)
            }
    
    def get_emotion_distribution(self) -> Dict[str, Any]:
        """
        Get emotion distribution from recent history.
        
        Returns:
            Dict with emotion statistics
        """
        if not self.emotion_history:
            return {
                "samples": 0,
                "distribution": {emotion: 0.0 for emotion in self.EMOTIONS},
                "most_frequent": None
            }
        
        # Calculate average distribution
        distribution = self._get_smoothed_emotions()
        
        # Find most frequent emotion
        most_frequent = max(distribution.items(), key=lambda x: x[1])
        
        return {
            "samples": len(self.emotion_history),
            "distribution": distribution,
            "most_frequent": most_frequent[0],
            "most_frequent_score": most_frequent[1]
        }


# Convenience functions

def detect_emotion(
    camera_index: int = 0,
    model_name: str = "VGG-Face"
) -> Dict[str, Any]:
    """
    Detect emotion from a single camera frame.
    
    Args:
        camera_index: Camera device index
        model_name: DeepFace model to use
        
    Returns:
        Emotion analysis results
    """
    detector = EmotionDetector(camera_index=camera_index, model_name=model_name)
    
    if not detector.start():
        return {
            "available": False,
            "error": "Failed to start emotion detector"
        }
    
    result = detector.capture()
    detector.stop()
    
    return result


def analyze_image_emotion(
    image_path: str,
    model_name: str = "VGG-Face"
) -> Dict[str, Any]:
    """
    Analyze emotions from an image file.
    
    Args:
        image_path: Path to image file
        model_name: DeepFace model to use
        
    Returns:
        Emotion analysis results
    """
    detector = EmotionDetector(model_name=model_name)
    return detector.analyze_image(image_path)


def get_available_models() -> List[str]:
    """
    Get list of available DeepFace models.
    
    Returns:
        List of model names
    """
    return EmotionDetector.AVAILABLE_MODELS.copy()


def check_deepface_available() -> bool:
    """
    Check if DeepFace is available.
    
    Returns:
        True if DeepFace can be imported
    """
    return DEEPFACE_AVAILABLE
