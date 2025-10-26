"""
Base class for all sensor implementations.

This module provides an abstract base class that defines the common interface
for all sensor types (camera, microphone, etc.). It handles status management,
error handling, and configuration.
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
    ACTIVE = "active"      # Sensor running normally
    ERROR = "error"        # Sensor encountered an error
    UNAVAILABLE = "unavailable"  # Hardware not available


class SensorError(Exception):
    """Base exception for sensor-related errors."""
    pass


class SensorUnavailableError(SensorError):
    """Raised when sensor hardware is not available."""
    pass


class SensorConfigError(SensorError):
    """Raised when sensor configuration is invalid."""
    pass


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
    """
    
    def __init__(self, name: str, sensor_type: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base sensor.
        
        Args:
            name: Human-readable sensor name
            sensor_type: Type identifier (camera, microphone, etc.)
            config: Optional configuration dictionary
        """
        self.name = name
        self.sensor_type = sensor_type
        self.config = config or {}
        self.status = SensorStatus.INACTIVE
        self.error_message: Optional[str] = None
        self._start_time: Optional[datetime] = None
        
        logger.info(f"Initialized {self.name} ({self.sensor_type})")
    
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
        pass
    
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
        pass
    
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
        pass
    
    def start(self) -> bool:
        """
        Start the sensor.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            if self.status == SensorStatus.ACTIVE:
                logger.warning(f"{self.name} is already active")
                return True
            
            logger.info(f"Starting {self.name}...")
            if self.initialize():
                self.status = SensorStatus.ACTIVE
                self._start_time = datetime.now()
                logger.info(f"{self.name} started successfully")
                return True
            else:
                self.status = SensorStatus.ERROR
                self.error_message = "Initialization failed"
                logger.error(f"{self.name} failed to start")
                return False
                
        except SensorUnavailableError as e:
            self.status = SensorStatus.UNAVAILABLE
            self.error_message = str(e)
            logger.error(f"{self.name} hardware unavailable: {e}")
            return False
            
        except Exception as e:
            self.status = SensorStatus.ERROR
            self.error_message = str(e)
            logger.error(f"{self.name} error during start: {e}", exc_info=True)
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
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current sensor status.
        
        Returns:
            Dict containing status information:
                - name: Sensor name
                - type: Sensor type
                - status: Current status
                - active: Whether sensor is active
                - error_message: Error message if status is ERROR
                - uptime_seconds: Seconds since start (if active)
                - config: Current configuration
        """
        result = {
            "name": self.name,
            "type": self.sensor_type,
            "status": self.status.value,
            "active": self.status == SensorStatus.ACTIVE,
            "error_message": self.error_message,
            "config": self.config
        }
        
        if self._start_time and self.status == SensorStatus.ACTIVE:
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
        Check if sensor is currently active.
        
        Returns:
            bool: True if sensor is active and capturing data
        """
        return self.status == SensorStatus.ACTIVE
    
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
