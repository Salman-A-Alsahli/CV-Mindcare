"""
Camera Sensor Implementation (Phase 3)

Implements camera-based greenery detection using HSV color analysis with
>80% accuracy target. Supports both OpenCV (development) and picamera2 (Raspberry Pi).
Includes automatic mock mode fallback for development without hardware.
"""

import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import random

# Import base sensor
from .base import BaseSensor, SensorUnavailableError

logger = logging.getLogger(__name__)


class CameraSensor(BaseSensor):
    """
    Camera sensor for greenery detection using HSV color analysis.

    Supports two backends:
    - OpenCV (cv2) - for development and general use
    - picamera2 - for Raspberry Pi native camera (10x faster)

    Features:
    - HSV color space analysis for greenery detection
    - Configurable green hue range (default: 35-85°)
    - Automatic mock mode if hardware unavailable
    - Frame capture and analysis
    - >80% accuracy target for greenery detection

    Configuration options:
        - camera_index (int): Camera device index (default: 0)
        - backend (str): 'opencv' or 'picamera2' (default: 'opencv')
        - resolution (tuple): Frame resolution (default: (640, 480))
        - mock_mode (bool): Force mock mode (default: False)
        - green_hue_range (tuple): HSV hue range for green (default: (35, 85))
        - saturation_min (int): Minimum saturation for green detection (default: 40)
        - value_min (int): Minimum value for green detection (default: 40)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize camera sensor."""
        super().__init__(name="Camera Sensor", sensor_type="camera", config=config)

        # Configuration
        self.camera_index = self.config.get("camera_index", 0)
        self.backend = self.config.get("backend", "opencv")
        
        # Handle resolution - can be tuple (width, height) or dict with width/height
        resolution_config = self.config.get("resolution", (640, 480))
        if isinstance(resolution_config, dict):
            self.resolution = (
                resolution_config.get("width", 640),
                resolution_config.get("height", 480)
            )
        else:
            self.resolution = resolution_config

        # HSV parameters for greenery detection
        self.green_hue_range = self.config.get("green_hue_range", (35, 85))
        self.saturation_min = self.config.get("saturation_min", 40)
        self.value_min = self.config.get("value_min", 40)

        # Hardware objects
        self.cap = None
        self.picam = None

        logger.info(f"CameraSensor initialized (backend={self.backend}, index={self.camera_index})")

    def check_hardware_available(self) -> bool:
        """
        Check if camera hardware is available.

        Returns:
            bool: True if camera can be accessed
        """
        if self.backend == "picamera2":
            try:
                from picamera2 import Picamera2

                # Try to instantiate to check availability
                test_cam = Picamera2()
                test_cam.close()
                logger.info("Picamera2 hardware detected")
                return True
            except Exception as e:
                logger.warning(f"Picamera2 not available: {e}")
                return False
        else:
            # OpenCV backend
            try:
                import cv2

                test_cap = cv2.VideoCapture(self.camera_index)
                available = test_cap.isOpened()
                test_cap.release()
                if available:
                    logger.info(f"OpenCV camera {self.camera_index} detected")
                else:
                    logger.warning(f"OpenCV camera {self.camera_index} not available")
                return available
            except Exception as e:
                logger.warning(f"OpenCV camera check failed: {e}")
                return False

    def initialize(self) -> bool:
        """
        Initialize camera hardware.

        Returns:
            bool: True if initialization successful

        Raises:
            SensorUnavailableError: If hardware cannot be initialized
        """
        if self.backend == "picamera2":
            return self._initialize_picamera2()
        else:
            return self._initialize_opencv()

    def _initialize_opencv(self) -> bool:
        """Initialize OpenCV camera backend."""
        try:
            import cv2

            self.cap = cv2.VideoCapture(self.camera_index)

            if not self.cap.isOpened():
                raise SensorUnavailableError(f"Cannot open camera {self.camera_index}")

            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])

            # Test capture
            ret, frame = self.cap.read()
            if not ret or frame is None:
                self.cap.release()
                raise SensorUnavailableError("Cannot capture test frame")

            logger.info(f"OpenCV camera initialized (resolution={frame.shape[1]}x{frame.shape[0]})")
            return True

        except ImportError:
            raise SensorUnavailableError("OpenCV (cv2) not installed")
        except Exception as e:
            if self.cap:
                self.cap.release()
            raise SensorUnavailableError(f"Camera initialization failed: {e}")

    def _initialize_picamera2(self) -> bool:
        """Initialize picamera2 backend (Raspberry Pi)."""
        try:
            from picamera2 import Picamera2

            self.picam = Picamera2()
            config = self.picam.create_preview_configuration(
                main={"size": self.resolution, "format": "RGB888"}
            )
            self.picam.configure(config)
            self.picam.start()

            # Test capture
            frame = self.picam.capture_array()
            if frame is None:
                self.picam.stop()
                raise SensorUnavailableError("Cannot capture test frame")

            logger.info(f"Picamera2 initialized (resolution={frame.shape[1]}x{frame.shape[0]})")
            return True

        except ImportError:
            raise SensorUnavailableError("picamera2 not installed")
        except Exception as e:
            if self.picam:
                try:
                    self.picam.stop()
                except:
                    pass
            raise SensorUnavailableError(f"Picamera2 initialization failed: {e}")

    def capture(self) -> Dict[str, Any]:
        """
        Capture frame and analyze greenery.

        Returns:
            Dict containing:
                - timestamp: ISO 8601 timestamp
                - sensor_type: 'camera'
                - greenery_percentage: Percentage of green pixels (0-100)
                - resolution: Frame resolution (width, height)
                - frame_shape: Actual captured frame shape
                - hsv_params: HSV parameters used for detection

        Raises:
            SensorError: If capture or analysis fails
        """
        from .base import SensorError

        # Capture frame
        if self.backend == "picamera2":
            frame = self._capture_picamera2()
        else:
            frame = self._capture_opencv()

        if frame is None:
            raise SensorError("Failed to capture frame")

        # Analyze greenery
        greenery_pct = self._analyze_greenery(frame)

        return {
            "timestamp": datetime.now().isoformat(),
            "sensor_type": "camera",
            "greenery_percentage": round(greenery_pct, 2),
            "resolution": self.resolution,
            "frame_shape": frame.shape,
            "hsv_params": {
                "hue_range": self.green_hue_range,
                "saturation_min": self.saturation_min,
                "value_min": self.value_min,
            },
        }

    def _capture_opencv(self) -> Optional[np.ndarray]:
        """Capture frame using OpenCV."""
        if self.cap is None or not self.cap.isOpened():
            logger.error("OpenCV camera not initialized")
            return None

        ret, frame = self.cap.read()
        if not ret or frame is None:
            logger.error("Failed to capture frame")
            return None

        return frame

    def _capture_picamera2(self) -> Optional[np.ndarray]:
        """Capture frame using picamera2."""
        if self.picam is None:
            logger.error("Picamera2 not initialized")
            return None

        try:
            frame = self.picam.capture_array()
            return frame
        except Exception as e:
            logger.error(f"Picamera2 capture failed: {e}")
            return None

    def _analyze_greenery(self, frame: np.ndarray) -> float:
        """
        Analyze greenery percentage using HSV color space.

        Algorithm:
        1. Convert frame to HSV color space
        2. Define green color range (hue: 35-85°, saturation: 40-255, value: 40-255)
        3. Create binary mask of green pixels
        4. Calculate percentage of green pixels

        Args:
            frame: BGR or RGB image array

        Returns:
            float: Percentage of green pixels (0-100)
        """
        try:
            import cv2

            # Convert to HSV (handle both BGR and RGB)
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                # Assume BGR from OpenCV or RGB from picamera2
                # picamera2 gives RGB, OpenCV gives BGR
                if self.backend == "picamera2":
                    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
                else:
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            else:
                logger.error(f"Unexpected frame shape: {frame.shape}")
                return 0.0

            # Define HSV range for green
            lower_green = np.array([self.green_hue_range[0], self.saturation_min, self.value_min])
            upper_green = np.array([self.green_hue_range[1], 255, 255])

            # Create mask for green pixels
            mask = cv2.inRange(hsv, lower_green, upper_green)

            # Calculate percentage
            total_pixels = mask.size
            green_pixels = np.count_nonzero(mask)
            percentage = (green_pixels / total_pixels) * 100.0

            logger.debug(f"Greenery analysis: {green_pixels}/{total_pixels} = {percentage:.2f}%")
            return percentage

        except Exception as e:
            logger.error(f"Greenery analysis failed: {e}")
            return 0.0

    def capture_mock_data(self) -> Dict[str, Any]:
        """
        Generate realistic mock camera data.

        Simulates various workspace scenarios with different greenery levels.

        Returns:
            Dict with same structure as capture()
        """
        # Generate realistic greenery percentage based on common scenarios
        scenarios = [
            (0, 5, "indoor_no_plants"),  # Indoor with no plants
            (5, 15, "indoor_few_plants"),  # Indoor with few small plants
            (15, 30, "indoor_many_plants"),  # Indoor with several plants
            (30, 50, "near_window"),  # Near window with view
            (50, 80, "outdoor_partial"),  # Outdoor with partial greenery
            (80, 100, "outdoor_full"),  # Full outdoor/garden view
        ]

        # Weighted random selection (favor indoor scenarios)
        weights = [0.25, 0.35, 0.20, 0.10, 0.07, 0.03]
        scenario = random.choices(scenarios, weights=weights)[0]
        greenery_pct = random.uniform(scenario[0], scenario[1])

        return {
            "timestamp": datetime.now().isoformat(),
            "sensor_type": "camera",
            "greenery_percentage": round(greenery_pct, 2),
            "resolution": self.resolution,
            "frame_shape": (self.resolution[1], self.resolution[0], 3),  # Height, Width, Channels
            "hsv_params": {
                "hue_range": self.green_hue_range,
                "saturation_min": self.saturation_min,
                "value_min": self.value_min,
            },
            "mock_scenario": scenario[2],
        }

    def cleanup(self) -> bool:
        """
        Clean up camera resources.

        Returns:
            bool: True if cleanup successful
        """
        try:
            if self.cap is not None:
                self.cap.release()
                self.cap = None
                logger.info("OpenCV camera released")

            if self.picam is not None:
                self.picam.stop()
                self.picam = None
                logger.info("Picamera2 stopped")

            return True

        except Exception as e:
            logger.error(f"Camera cleanup error: {e}")
            return False


# Convenience functions for backward compatibility


def get_camera_reading(camera_index: int = 0, backend: str = "opencv") -> Dict[str, Any]:
    """
    Get a single camera reading with greenery detection.

    Args:
        camera_index: Camera device index
        backend: 'opencv' or 'picamera2'

    Returns:
        Camera reading dictionary
    """
    sensor = CameraSensor(config={"camera_index": camera_index, "backend": backend})
    sensor.start()

    try:
        data = sensor.read()
        sensor.stop()
        return data
    except Exception as e:
        sensor.stop()
        return {
            "timestamp": datetime.now().isoformat(),
            "sensor_type": "camera",
            "greenery_percentage": 0.0,
            "error": str(e),
            "mock_mode": True,
        }


def check_camera_available(camera_index: int = 0, backend: str = "opencv") -> bool:
    """
    Check if camera is available.

    Args:
        camera_index: Camera device index
        backend: 'opencv' or 'picamera2'

    Returns:
        True if camera is available
    """
    sensor = CameraSensor(config={"camera_index": camera_index, "backend": backend})
    return sensor.check_hardware_available()
