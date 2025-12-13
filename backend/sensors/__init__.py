"""
Sensors Package (Phase 2: Sensor Infrastructure)

Contains all sensor modules for CV-Mindcare data collection with robust
error handling and automatic mock mode fallback.

Basic imports (always available):
    from backend.sensors import BaseSensor, SensorStatus, SensorError

Specific sensors (require additional dependencies):
    from backend.sensors.camera import CameraSensor  # requires opencv
    from backend.sensors.microphone import MicrophoneSensor  # requires sounddevice
"""

# Always available (no heavy dependencies)
from .base import (
    BaseSensor,
    SensorStatus,
    SensorError,
    SensorUnavailableError,
    SensorConfigError,
)

__all__ = [
    # Base classes (always available)
    "BaseSensor",
    "SensorStatus",
    "SensorError",
    "SensorUnavailableError",
    "SensorConfigError",
]

# Note: Specific sensor implementations should be imported explicitly
# to avoid dependency issues during testing and development.
#
# Example:
#   from backend.sensors.camera import CameraSensor
#   from backend.sensors.microphone import MicrophoneSensor
