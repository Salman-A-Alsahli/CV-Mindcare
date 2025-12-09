"""
Sensor Manager & Orchestration (Phase 5)

Unified management system for all sensors with automatic polling, health monitoring,
and graceful degradation. Coordinates camera and microphone sensors with thread-safe
concurrent access.

Features:
- Centralized control for all sensors
- Automatic background polling (1-10 Hz configurable)
- Health monitoring and auto-recovery
- Thread-safe operations
- Graceful shutdown
- Status aggregation
"""

import threading
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from .camera_sensor import CameraSensor
from .microphone_sensor import MicrophoneSensor
from .base import SensorStatus

logger = logging.getLogger(__name__)


class ManagerStatus(Enum):
    """Status of the sensor manager."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class SensorManager:
    """
    Unified sensor management system.
    
    Manages all sensors (camera, microphone, future sensors) with automatic
    polling, health monitoring, and graceful error handling.
    
    Configuration options:
        - polling_interval (float): Seconds between sensor reads (default: 5.0)
        - camera (dict): Camera sensor configuration
        - microphone (dict): Microphone sensor configuration
        - auto_start (bool): Auto-start sensors on manager start (default: True)
        - auto_recover (bool): Auto-recover failed sensors (default: True)
        - max_retries (int): Max sensor restart attempts (default: 3)
    
    Usage:
        manager = SensorManager(config={
            'polling_interval': 5.0,
            'camera': {'backend': 'opencv'},
            'microphone': {'backend': 'sounddevice'}
        })
        manager.start_all()
        data = manager.read_all()
        manager.stop_all()
    """
    
    # Class constants
    THREAD_STOP_TIMEOUT = 5.0  # Seconds to wait for polling thread shutdown
    HEALTH_ERROR_PENALTY = 10  # Health score penalty per error
    HEALTH_ERROR_MAX_PENALTY = 30  # Maximum penalty from errors
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize sensor manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Configuration
        self.polling_interval = self.config.get('polling_interval', 5.0)
        self.auto_start = self.config.get('auto_start', True)
        self.auto_recover = self.config.get('auto_recover', True)
        self.max_retries = self.config.get('max_retries', 3)
        
        # Initialize sensors
        self.camera = CameraSensor(self.config.get('camera', {}))
        self.microphone = MicrophoneSensor(self.config.get('microphone', {}))
        
        # State management
        self.status = ManagerStatus.STOPPED
        self.running = False
        self._lock = threading.Lock()
        self._polling_thread: Optional[threading.Thread] = None
        self._start_time: Optional[datetime] = None
        
        # Health tracking
        self._retry_counts: Dict[str, int] = {
            'camera': 0,
            'microphone': 0
        }
        self._last_read_time: Dict[str, Optional[datetime]] = {
            'camera': None,
            'microphone': None
        }
        self._error_counts: Dict[str, int] = {
            'camera': 0,
            'microphone': 0
        }
        
        logger.info(f"SensorManager initialized (polling={self.polling_interval}s)")
    
    def start_all(self) -> bool:
        """
        Start all sensors and begin automatic polling.
        
        Returns:
            bool: True if at least one sensor started successfully
        """
        with self._lock:
            if self.running:
                logger.warning("SensorManager already running")
                return True
            
            self.status = ManagerStatus.STARTING
            logger.info("Starting all sensors...")
            
            # Start individual sensors
            camera_ok = self._start_sensor(self.camera, 'camera')
            microphone_ok = self._start_sensor(self.microphone, 'microphone')
            
            if not camera_ok and not microphone_ok:
                logger.error("Failed to start any sensors")
                self.status = ManagerStatus.ERROR
                return False
            
            # Start polling thread
            self.running = True
            self._polling_thread = threading.Thread(
                target=self._polling_loop,
                daemon=True,
                name="SensorManagerPolling"
            )
            self._polling_thread.start()
            
            self.status = ManagerStatus.RUNNING
            self._start_time = datetime.now()  # Set start time when running
            logger.info(f"SensorManager started (camera={camera_ok}, microphone={microphone_ok})")
            return True
    
    def stop_all(self) -> bool:
        """
        Stop all sensors and polling gracefully.
        
        Returns:
            bool: True if stopped successfully
        """
        with self._lock:
            if not self.running:
                logger.warning("SensorManager not running")
                return True
            
            self.status = ManagerStatus.STOPPING
            logger.info("Stopping all sensors...")
            
            # Calculate final uptime before clearing
            final_uptime = self._calculate_uptime()
            
            # Stop polling thread
            self.running = False
            if self._polling_thread and self._polling_thread.is_alive():
                self._polling_thread.join(timeout=self.THREAD_STOP_TIMEOUT)
            
            # Stop individual sensors
            camera_ok = self._stop_sensor(self.camera, 'camera')
            microphone_ok = self._stop_sensor(self.microphone, 'microphone')
            
            self.status = ManagerStatus.STOPPED
            self._start_time = None  # Clear start time after calculating uptime
            logger.info(f"SensorManager stopped (camera={camera_ok}, microphone={microphone_ok}, uptime={final_uptime}s)")
            return True
    
    def get_all_status(self) -> Dict[str, Any]:
        """
        Get status of all sensors and manager.
        
        Returns:
            dict: Status information for manager and all sensors
        """
        with self._lock:
            camera_status = self.camera.get_status()
            microphone_status = self.microphone.get_status()
            
            return {
                'manager': {
                    'status': self.status.value,
                    'running': self.running,
                    'polling_interval': self.polling_interval,
                    'uptime': self._calculate_uptime()
                },
                'sensors': {
                    'camera': {
                        **camera_status,
                        'error_count': self._error_counts['camera'],
                        'retry_count': self._retry_counts['camera'],
                        'last_read': self._last_read_time['camera'].isoformat() if self._last_read_time['camera'] else None
                    },
                    'microphone': {
                        **microphone_status,
                        'error_count': self._error_counts['microphone'],
                        'retry_count': self._retry_counts['microphone'],
                        'last_read': self._last_read_time['microphone'].isoformat() if self._last_read_time['microphone'] else None
                    }
                },
                'timestamp': datetime.now().isoformat()
            }
    
    def read_all(self) -> Dict[str, Any]:
        """
        Read data from all active sensors.
        
        Returns:
            dict: Data from all sensors that successfully read
        """
        with self._lock:
            result = {
                'timestamp': datetime.now().isoformat(),
                'data': {},
                'errors': {}
            }
            
            # Read camera
            try:
                camera_data = self.camera.read()
                result['data']['camera'] = camera_data
                self._last_read_time['camera'] = datetime.now()
                self._error_counts['camera'] = 0  # Reset on success
            except Exception as e:
                logger.error(f"Error reading camera: {e}")
                result['errors']['camera'] = str(e)
                self._error_counts['camera'] += 1
            
            # Read microphone
            try:
                microphone_data = self.microphone.read()
                result['data']['microphone'] = microphone_data
                self._last_read_time['microphone'] = datetime.now()
                self._error_counts['microphone'] = 0  # Reset on success
            except Exception as e:
                logger.error(f"Error reading microphone: {e}")
                result['errors']['microphone'] = str(e)
                self._error_counts['microphone'] += 1
            
            return result
    
    def get_health(self) -> Dict[str, Any]:
        """
        Get detailed health information.
        
        Returns:
            dict: Health metrics for manager and all sensors
        """
        status = self.get_all_status()
        
        # Calculate health score (0-100)
        health_score = 100
        issues = []
        
        # Check manager status
        if self.status != ManagerStatus.RUNNING:
            health_score -= 50
            issues.append(f"Manager not running: {self.status.value}")
        
        # Check sensor health
        for sensor_name, sensor_info in status['sensors'].items():
            sensor_status = sensor_info.get('status', 'unknown')
            error_count = sensor_info.get('error_count', 0)
            
            # Penalize for non-active sensors
            if sensor_status not in ['ACTIVE', 'MOCK_MODE']:
                health_score -= 20
                issues.append(f"{sensor_name} not active: {sensor_status}")
            
            # Penalize for errors
            if error_count > 0:
                penalty = min(self.HEALTH_ERROR_PENALTY * error_count, self.HEALTH_ERROR_MAX_PENALTY)
                health_score -= penalty
                issues.append(f"{sensor_name} has {error_count} errors")
        
        health_score = max(0, health_score)
        
        return {
            'health_score': health_score,
            'status': 'healthy' if health_score >= 80 else 'degraded' if health_score >= 50 else 'unhealthy',
            'issues': issues,
            'timestamp': datetime.now().isoformat(),
            **status
        }
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Update manager configuration (requires restart to take effect).
        
        Args:
            new_config: New configuration dictionary
        
        Returns:
            bool: True if configuration updated successfully
        """
        with self._lock:
            try:
                # Update polling interval
                if 'polling_interval' in new_config:
                    self.polling_interval = float(new_config['polling_interval'])
                    logger.info(f"Updated polling_interval to {self.polling_interval}s")
                
                # Update other config
                if 'auto_recover' in new_config:
                    self.auto_recover = bool(new_config['auto_recover'])
                
                if 'max_retries' in new_config:
                    self.max_retries = int(new_config['max_retries'])
                
                # Store new config
                self.config.update(new_config)
                
                return True
            except Exception as e:
                logger.error(f"Error updating config: {e}")
                return False
    
    def _start_sensor(self, sensor, name: str) -> bool:
        """
        Start an individual sensor with retry logic.
        
        Args:
            sensor: Sensor instance to start
            name: Sensor name for logging
        
        Returns:
            bool: True if sensor started successfully
        """
        try:
            success = sensor.start()
            if success:
                self._retry_counts[name] = 0
                logger.info(f"{name} sensor started successfully")
                return True
            else:
                logger.warning(f"{name} sensor failed to start")
                return False
        except Exception as e:
            logger.error(f"Error starting {name} sensor: {e}")
            return False
    
    def _stop_sensor(self, sensor, name: str) -> bool:
        """
        Stop an individual sensor gracefully.
        
        Args:
            sensor: Sensor instance to stop
            name: Sensor name for logging
        
        Returns:
            bool: True if sensor stopped successfully
        """
        try:
            success = sensor.stop()
            if success:
                logger.info(f"{name} sensor stopped successfully")
                return True
            else:
                logger.warning(f"{name} sensor failed to stop cleanly")
                return False
        except Exception as e:
            logger.error(f"Error stopping {name} sensor: {e}")
            return False
    
    def _polling_loop(self) -> None:
        """
        Background polling loop (runs in separate thread).
        
        Continuously reads from all sensors at the configured interval.
        Handles errors and auto-recovery if configured.
        """
        logger.info("Polling loop started")
        
        while self.running:
            try:
                # Read from all sensors
                data = self.read_all()
                
                # Auto-recover failed sensors if enabled
                if self.auto_recover:
                    self._check_and_recover()
                
                # Sleep for polling interval
                time.sleep(self.polling_interval)
                
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time.sleep(1.0)  # Brief pause before retrying
        
        logger.info("Polling loop stopped")
    
    def _check_and_recover(self) -> None:
        """
        Check sensor health and attempt recovery if needed.
        
        Restarts sensors that have failed if they haven't exceeded max retries.
        """
        # Check camera
        if self._should_recover('camera', self.camera):
            logger.info(f"Attempting to recover camera sensor (retry {self._retry_counts['camera'] + 1}/{self.max_retries})")
            if self._start_sensor(self.camera, 'camera'):
                logger.info("Camera sensor recovered successfully")
            else:
                self._retry_counts['camera'] += 1
        
        # Check microphone
        if self._should_recover('microphone', self.microphone):
            logger.info(f"Attempting to recover microphone sensor (retry {self._retry_counts['microphone'] + 1}/{self.max_retries})")
            if self._start_sensor(self.microphone, 'microphone'):
                logger.info("Microphone sensor recovered successfully")
            else:
                self._retry_counts['microphone'] += 1
    
    def _should_recover(self, name: str, sensor) -> bool:
        """
        Determine if a sensor should be recovered.
        
        Args:
            name: Sensor name
            sensor: Sensor instance
        
        Returns:
            bool: True if sensor should be recovered
        """
        # Don't recover if max retries exceeded
        if self._retry_counts[name] >= self.max_retries:
            return False
        
        # Check if sensor is in error state
        status = sensor.get_status()
        current_status = status.get('status', '')
        
        return current_status in ['ERROR', 'UNAVAILABLE']
    
    def _calculate_uptime(self) -> Optional[float]:
        """
        Calculate manager uptime in seconds.
        
        Returns:
            float: Uptime in seconds, or None if not running
        """
        if self._start_time:
            return (datetime.now() - self._start_time).total_seconds()
        return None
