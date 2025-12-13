"""
Base class for all sensor implementations (Phase 2: Sensor Infrastructure).

This module provides a robust abstract base class that defines the common interface
for all sensor types (camera, microphone, etc.) with comprehensive status management,
error handling, and automatic mock mode fallback for development without hardware.

Key Features:
- Status management: INACTIVE, AVAILABLE, ACTIVE, ERROR, UNAVAILABLE, MOCK_MODE
- Automatic fallback to mock mode when hardware unavailable
- Standardized error handling and logging
- Configuration management
- Hardware detection
- Graceful degradation

Usage:
    class MyCameraSensor(BaseSensor):
        def __init__(self, config=None):
            super().__init__("My Camera", "camera", config)

        def initialize(self) -> bool:
            # Initialize real hardware
            return True

        def capture(self) -> Dict[str, Any]:
            # Capture real data
            return {"timestamp": datetime.now().isoformat(), ...}

        def capture_mock_data(self) -> Dict[str, Any]:
            # Generate mock data
            return {"timestamp": datetime.now().isoformat(), ...}

        def cleanup(self) -> bool:
            # Clean up resources
            return True

        def check_hardware_available(self) -> bool:
            # Check if camera exists
            return os.path.exists("/dev/video0")

Optimized for Raspberry Pi 5 deployment with graceful hardware detection.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SensorStatus(Enum):
    """Sensor status enumeration."""

    INACTIVE = "inactive"  # Sensor not started
    AVAILABLE = "available"  # Hardware available but not started
    ACTIVE = "active"  # Sensor running normally
    ERROR = "error"  # Sensor encountered an error
    UNAVAILABLE = "unavailable"  # Hardware not available
    MOCK_MODE = "mock_mode"  # Running in mock/simulation mode


class SensorError(Exception):
    """Base exception for sensor-related errors."""



class SensorUnavailableError(SensorError):
    """Raised when sensor hardware is not available."""



class SensorConfigError(SensorError):
    """Raised when sensor configuration is invalid."""



class BaseSensor(ABC):
    """
    Abstract base class for all sensors.

    All sensor implementations must inherit from this class and implement
    the required abstract methods.

    Attributes:
        name: Human-readable sensor name
        sensor_type: Type identifier (camera, microphone, etc.)
        status: Current sensor status
        config: Sensor configuration dictionary
        error_message: Last error message if status is ERROR
        mock_mode: Whether sensor is running in mock/simulation mode
    """

    def __init__(self, name: str, sensor_type: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base sensor.

        Args:
            name: Human-readable sensor name
            sensor_type: Type identifier (camera, microphone, etc.)
            config: Optional configuration dictionary
                - 'mock_mode' (bool): Enable mock/simulation mode (default: False)
                - Other sensor-specific configuration options
        """
        self.name = name
        self.sensor_type = sensor_type
        self.config = config or {}
        self.status = SensorStatus.INACTIVE
        self.error_message: Optional[str] = None
        self.mock_mode = self.config.get("mock_mode", False)
        self._start_time: Optional[datetime] = None

        logger.info(f"Initialized {self.name} ({self.sensor_type}, mock_mode={self.mock_mode})")

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the sensor hardware and resources.

        This method should:
        1. Check hardware availability
        2. Initialize hardware connections
        3. Validate configuration
        4. Set status to ACTIVE or ERROR

        Returns:
            bool: True if initialization successful, False otherwise
        """

    @abstractmethod
    def capture(self) -> Dict[str, Any]:
        """
        Capture data from the sensor.

        This method should:
        1. Capture raw data from hardware
        2. Process/analyze the data
        3. Return structured result dictionary

        Returns:
            Dict containing:
                - timestamp: ISO 8601 timestamp
                - sensor_type: Type of sensor
                - raw_data: Raw sensor reading
                - processed_data: Processed/analyzed data
                - metadata: Additional information

        Raises:
            SensorError: If capture fails
        """

    @abstractmethod
    def cleanup(self) -> bool:
        """
        Clean up sensor resources and close connections.

        This method should:
        1. Release hardware resources
        2. Close connections
        3. Save state if needed
        4. Set status to INACTIVE

        Returns:
            bool: True if cleanup successful, False otherwise
        """

    @abstractmethod
    def capture_mock_data(self) -> Dict[str, Any]:
        """
        Generate mock/simulated sensor data.

        This method must be implemented to provide realistic fake data
        when hardware is unavailable or when mock_mode is enabled.
        Essential for development and testing without physical hardware.

        Returns:
            Dict containing mock sensor data in same format as capture()
        """

    def check_hardware_available(self) -> bool:
        """
        Check if sensor hardware is physically available.

        Override this method to implement hardware detection logic.
        Default implementation returns True (assumes hardware present).

        Returns:
            bool: True if hardware is detected and accessible
        """
        return True

    def start(self) -> bool:
        """
        Start the sensor.

        Automatically falls back to mock mode if hardware is unavailable.

        Returns:
            bool: True if started successfully (real or mock mode), False otherwise
        """
        try:
            if self.status == SensorStatus.ACTIVE or self.status == SensorStatus.MOCK_MODE:
                logger.warning(f"{self.name} is already active")
                return True

            # Check if mock mode is explicitly requested
            if self.mock_mode:
                logger.info(f"Starting {self.name} in MOCK_MODE (explicitly requested)")
                self.status = SensorStatus.MOCK_MODE
                self._start_time = datetime.now()
                logger.info(f"{self.name} started successfully in mock mode")
                return True

            # Check hardware availability
            if not self.check_hardware_available():
                logger.warning(f"{self.name} hardware not available, falling back to MOCK_MODE")
                self.status = SensorStatus.MOCK_MODE
                self.mock_mode = True
                self._start_time = datetime.now()
                return True

            # Try to initialize real hardware
            logger.info(f"Starting {self.name} with real hardware...")
            if self.initialize():
                self.status = SensorStatus.ACTIVE
                self._start_time = datetime.now()
                logger.info(f"{self.name} started successfully")
                return True
            else:
                # Initialization failed, fall back to mock mode
                logger.warning(f"{self.name} initialization failed, falling back to MOCK_MODE")
                self.status = SensorStatus.MOCK_MODE
                self.mock_mode = True
                self._start_time = datetime.now()
                return True

        except SensorUnavailableError as e:
            # Hardware explicitly unavailable, use mock mode
            logger.warning(f"{self.name} hardware unavailable: {e}, using MOCK_MODE")
            self.status = SensorStatus.MOCK_MODE
            self.mock_mode = True
            self.error_message = None  # Clear error since we're in mock mode
            self._start_time = datetime.now()
            return True

        except Exception as e:
            # Unexpected error, try mock mode as last resort
            logger.error(
                f"{self.name} error during start: {e}, attempting MOCK_MODE", exc_info=True
            )
            try:
                self.status = SensorStatus.MOCK_MODE
                self.mock_mode = True
                self.error_message = f"Hardware error (using mock mode): {str(e)}"
                self._start_time = datetime.now()
                return True
            except Exception as fallback_error:
                self.status = SensorStatus.ERROR
                self.error_message = str(e)
                logger.error(f"{self.name} failed to start even in mock mode: {fallback_error}")
                return False

    def stop(self) -> bool:
        """
        Stop the sensor.

        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            if self.status == SensorStatus.INACTIVE:
                logger.warning(f"{self.name} is already inactive")
                return True

            logger.info(f"Stopping {self.name}...")
            if self.cleanup():
                self.status = SensorStatus.INACTIVE
                self._start_time = None
                logger.info(f"{self.name} stopped successfully")
                return True
            else:
                logger.error(f"{self.name} cleanup failed")
                return False

        except Exception as e:
            self.status = SensorStatus.ERROR
            self.error_message = str(e)
            logger.error(f"{self.name} error during stop: {e}", exc_info=True)
            return False

    def read(self) -> Dict[str, Any]:
        """
        Read data from the sensor (real or mock).

        Automatically uses capture() for real hardware or capture_mock_data()
        for mock mode. This is the main method to call for getting sensor data.

        Returns:
            Dict containing sensor data

        Raises:
            SensorError: If sensor is not active
        """
        if self.status == SensorStatus.INACTIVE:
            raise SensorError(f"{self.name} is not active. Call start() first.")

        if self.status == SensorStatus.ERROR:
            raise SensorError(f"{self.name} is in error state: {self.error_message}")

        if self.status == SensorStatus.UNAVAILABLE:
            raise SensorError(f"{self.name} hardware is unavailable")

        try:
            if self.status == SensorStatus.MOCK_MODE or self.mock_mode:
                # Use mock data
                data = self.capture_mock_data()
                data["mock_mode"] = True
                return data
            else:
                # Use real hardware
                data = self.capture()
                data["mock_mode"] = False
                return data
        except Exception as e:
            self.status = SensorStatus.ERROR
            self.error_message = str(e)
            logger.error(f"{self.name} capture error: {e}", exc_info=True)
            raise SensorError(f"Failed to read from {self.name}: {e}")

    def get_status(self) -> Dict[str, Any]:
        """
        Get current sensor status.

        Returns:
            Dict containing status information:
                - name: Sensor name
                - type: Sensor type
                - status: Current status
                - active: Whether sensor is active
                - mock_mode: Whether running in mock mode
                - error_message: Error message if status is ERROR
                - uptime_seconds: Seconds since start (if active)
                - config: Current configuration
        """
        result = {
            "name": self.name,
            "type": self.sensor_type,
            "status": self.status.value,
            "active": self.status in [SensorStatus.ACTIVE, SensorStatus.MOCK_MODE],
            "mock_mode": self.mock_mode or self.status == SensorStatus.MOCK_MODE,
            "error_message": self.error_message,
            "config": self.config,
        }

        if self._start_time and self.status in [SensorStatus.ACTIVE, SensorStatus.MOCK_MODE]:
            uptime = (datetime.now() - self._start_time).total_seconds()
            result["uptime_seconds"] = uptime
        else:
            result["uptime_seconds"] = 0

        return result

    def is_available(self) -> bool:
        """
        Check if sensor hardware is available.

        Returns:
            bool: True if hardware is available and sensor can be used
        """
        return self.status != SensorStatus.UNAVAILABLE

    def is_active(self) -> bool:
        """
        Check if sensor is currently active (real or mock mode).

        Returns:
            bool: True if sensor is active and capturing data
        """
        return self.status in [SensorStatus.ACTIVE, SensorStatus.MOCK_MODE]

    def update_config(self, config: Dict[str, Any]) -> bool:
        """
        Update sensor configuration.

        Args:
            config: New configuration dictionary

        Returns:
            bool: True if configuration updated successfully

        Note:
            If sensor is active, it may need to be restarted for
            configuration changes to take effect.
        """
        try:
            self.config.update(config)
            logger.info(f"{self.name} configuration updated")
            return True
        except Exception as e:
            logger.error(f"{self.name} configuration update failed: {e}")
            return False

    def __repr__(self) -> str:
        """String representation of the sensor."""
        return f"{self.__class__.__name__}(name='{self.name}', status='{self.status.value}')"
