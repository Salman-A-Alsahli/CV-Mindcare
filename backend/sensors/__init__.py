"""
Sensors Package
--------------
Contains all sensor modules for CV-Mindcare data collection.
"""

from .camera import CameraSensor, get_camera_reading, check_camera_available
from .microphone import MicrophoneSensor, get_sound_reading, check_microphone_available
from .system_monitor import SystemMonitor, get_system_reading, get_detailed_system_info

__all__ = [
    'CameraSensor',
    'MicrophoneSensor',
    'SystemMonitor',
    'get_camera_reading',
    'get_sound_reading',
    'get_system_reading',
    'get_detailed_system_info',
    'check_camera_available',
    'check_microphone_available',
]
