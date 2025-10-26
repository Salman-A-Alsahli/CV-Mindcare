"""
Sensors Package
--------------
Contains all sensor modules for CV-Mindcare data collection.
"""

from .base import BaseSensor, SensorStatus, SensorError, SensorUnavailableError
from .camera import CameraSensor, get_camera_reading, check_camera_available
from .microphone import MicrophoneSensor, get_sound_reading, check_microphone_available
from .system_monitor import SystemMonitor, get_system_reading, get_detailed_system_info
from .emotion_detection import (
    EmotionDetector,
    detect_emotion,
    analyze_image_emotion,
    get_available_models,
    check_deepface_available
)
from .sound_analysis import (
    SoundAnalyzer,
    analyze_sound,
    get_audio_devices,
    check_scipy_available
)

__all__ = [
    # Base classes
    'BaseSensor',
    'SensorStatus',
    'SensorError',
    'SensorUnavailableError',
    # Sensors
    'CameraSensor',
    'MicrophoneSensor',
    'SystemMonitor',
    'EmotionDetector',
    'SoundAnalyzer',
    # Convenience functions
    'get_camera_reading',
    'get_sound_reading',
    'get_system_reading',
    'get_detailed_system_info',
    'check_camera_available',
    'check_microphone_available',
    'detect_emotion',
    'analyze_image_emotion',
    'get_available_models',
    'check_deepface_available',
    'analyze_sound',
    'get_audio_devices',
    'check_scipy_available',
]
