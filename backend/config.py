"""
CV-Mindcare Unified Configuration Management (Phase 2).

This module provides centralized configuration management for all components
of the CV-Mindcare system, loading settings from YAML files with validation,
defaults, and environment variable overrides.

Features:
- YAML-based configuration files
- Environment variable overrides
- Type validation and defaults
- Configuration caching
- Hot-reload support (optional)
- Thread-safe access

Configuration Files:
- config/sensors.yaml: Sensor settings and calibration
- config/api.yaml: API server and CORS configuration
- config/database.yaml: Database connection and optimization
- config/analytics.yaml: Analytics and trend detection

Usage:
    from backend.config import config
    
    # Access configuration
    camera_backend = config.get('sensors.camera.backend')
    api_port = config.get('api.server.port', default=8000)
    
    # Get entire section
    sensor_config = config.get_section('sensors')
    
    # Check if key exists
    if config.has('sensors.air_quality'):
        aq_config = config.get('sensors.air_quality')
"""

import os
import yaml
import logging
from typing import Any, Dict, Optional, Union
from pathlib import Path
import threading
from copy import deepcopy

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Configuration error exception."""
    pass


class ConfigManager:
    """
    Unified configuration manager for CV-Mindcare.
    
    Loads and manages configuration from multiple YAML files with
    environment variable overrides and validation.
    
    Thread-safe singleton pattern ensures consistent configuration
    across the application.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize configuration manager."""
        # Only initialize once
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._config: Dict[str, Any] = {}
        self._config_lock = threading.RLock()
        
        # Determine config directory
        self._config_dir = self._find_config_dir()
        
        # Load all configuration files
        self._load_all_configs()
        
        logger.info(f"Configuration loaded from {self._config_dir}")
    
    def _find_config_dir(self) -> Path:
        """
        Find configuration directory.
        
        Searches in order:
        1. CVMINDCARE_CONFIG_DIR environment variable
        2. config/ directory relative to project root
        3. /etc/cv-mindcare/ (system-wide config)
        
        Returns:
            Path: Configuration directory path
        """
        # Check environment variable
        env_config_dir = os.getenv('CVMINDCARE_CONFIG_DIR')
        if env_config_dir and os.path.isdir(env_config_dir):
            return Path(env_config_dir)
        
        # Check relative to project root
        project_root = Path(__file__).parent.parent
        config_dir = project_root / 'config'
        if config_dir.is_dir():
            return config_dir
        
        # Check system-wide config
        system_config = Path('/etc/cv-mindcare')
        if system_config.is_dir():
            return system_config
        
        # Default to project config directory
        return project_root / 'config'
    
    def _load_all_configs(self):
        """Load all configuration files."""
        config_files = {
            'sensors': 'sensors.yaml',
            'api': 'api.yaml',
            'database': 'database.yaml',
            'analytics': 'analytics.yaml'
        }
        
        for section, filename in config_files.items():
            filepath = self._config_dir / filename
            
            if filepath.exists():
                try:
                    config_data = self._load_yaml(filepath)
                    self._config[section] = config_data
                    logger.debug(f"Loaded {filename}")
                except Exception as e:
                    logger.warning(f"Failed to load {filename}: {e}")
                    self._config[section] = {}
            else:
                logger.warning(f"Config file not found: {filepath}")
                self._config[section] = {}
        
        # Apply environment variable overrides
        self._apply_env_overrides()
    
    def _load_yaml(self, filepath: Path) -> Dict[str, Any]:
        """
        Load YAML configuration file.
        
        Args:
            filepath: Path to YAML file
        
        Returns:
            Dict: Parsed configuration
        
        Raises:
            ConfigError: If file cannot be loaded or parsed
        """
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
                return data if data is not None else {}
        except yaml.YAMLError as e:
            raise ConfigError(f"YAML parsing error in {filepath}: {e}")
        except Exception as e:
            raise ConfigError(f"Error loading {filepath}: {e}")
    
    def _apply_env_overrides(self):
        """
        Apply environment variable overrides.
        
        Environment variables in format:
        CVMINDCARE_<SECTION>_<KEY>_<SUBKEY>
        
        Examples:
            CVMINDCARE_API_SERVER_PORT=9000
            CVMINDCARE_SENSORS_CAMERA_MOCK_MODE=true
        """
        prefix = 'CVMINDCARE_'
        
        for env_key, env_value in os.environ.items():
            if not env_key.startswith(prefix):
                continue
            
            # Parse environment variable name
            config_path = env_key[len(prefix):].lower().split('_')
            
            if len(config_path) < 2:
                continue
            
            # Convert string value to appropriate type
            value = self._parse_env_value(env_value)
            
            # Set configuration value
            self._set_nested(self._config, config_path, value)
            logger.debug(f"Applied env override: {env_key}={value}")
    
    def _parse_env_value(self, value: str) -> Union[str, int, float, bool]:
        """
        Parse environment variable value to appropriate type.
        
        Args:
            value: String value from environment
        
        Returns:
            Parsed value (str, int, float, or bool)
        """
        # Boolean values
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        if value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Numeric values
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # String value
        return value
    
    def _set_nested(self, config: Dict, path: list, value: Any):
        """
        Set nested configuration value.
        
        Args:
            config: Configuration dictionary
            path: List of keys representing path
            value: Value to set
        """
        current = config
        
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[path[-1]] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.
        
        Args:
            key: Configuration key in dot notation (e.g., 'sensors.camera.backend')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        
        Examples:
            backend = config.get('sensors.camera.backend')
            port = config.get('api.server.port', default=8000)
        """
        with self._config_lock:
            keys = key.split('.')
            current = self._config
            
            try:
                for k in keys:
                    current = current[k]
                return deepcopy(current)
            except (KeyError, TypeError):
                return default
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.
        
        Args:
            section: Section name ('sensors', 'api', 'database', 'analytics')
        
        Returns:
            Dict: Configuration section
        
        Examples:
            sensor_config = config.get_section('sensors')
            api_config = config.get_section('api')
        """
        with self._config_lock:
            return deepcopy(self._config.get(section, {}))
    
    def has(self, key: str) -> bool:
        """
        Check if configuration key exists.
        
        Args:
            key: Configuration key in dot notation
        
        Returns:
            bool: True if key exists, False otherwise
        """
        with self._config_lock:
            keys = key.split('.')
            current = self._config
            
            try:
                for k in keys:
                    current = current[k]
                return True
            except (KeyError, TypeError):
                return False
    
    def set(self, key: str, value: Any):
        """
        Set configuration value (runtime only, not persisted).
        
        Args:
            key: Configuration key in dot notation
            value: Value to set
        
        Note:
            Changes are not persisted to configuration files.
            Use for runtime configuration changes only.
        """
        with self._config_lock:
            keys = key.split('.')
            self._set_nested(self._config, keys, value)
    
    def reload(self):
        """
        Reload configuration from files.
        
        Useful for hot-reloading configuration changes without
        restarting the application.
        """
        with self._config_lock:
            logger.info("Reloading configuration...")
            self._config.clear()
            self._load_all_configs()
            logger.info("Configuration reloaded")
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get entire configuration.
        
        Returns:
            Dict: Complete configuration
        """
        with self._config_lock:
            return deepcopy(self._config)
    
    def validate(self) -> bool:
        """
        Validate configuration.
        
        Checks for required keys and valid values.
        
        Returns:
            bool: True if configuration is valid
        
        Raises:
            ConfigError: If configuration is invalid
        """
        # Check required sections
        required_sections = ['sensors', 'api', 'database', 'analytics']
        
        for section in required_sections:
            if section not in self._config:
                raise ConfigError(f"Missing required configuration section: {section}")
        
        # Validate sensor configuration
        self._validate_sensors()
        
        # Validate API configuration
        self._validate_api()
        
        # Validate database configuration
        self._validate_database()
        
        return True
    
    def _validate_sensors(self):
        """Validate sensor configuration."""
        sensors_config = self._config.get('sensors', {})
        
        # Check required sensor sections
        required_sensors = ['camera', 'microphone', 'air_quality']
        
        for sensor in required_sensors:
            if sensor not in sensors_config:
                logger.warning(f"Missing sensor configuration: {sensor}")
    
    def _validate_api(self):
        """Validate API configuration."""
        api_config = self._config.get('api', {})
        
        # Check server configuration
        if 'server' in api_config:
            server = api_config['server']
            
            # Validate port
            port = server.get('port')
            if port and (port < 1 or port > 65535):
                raise ConfigError(f"Invalid API port: {port}")
    
    def _validate_database(self):
        """Validate database configuration."""
        db_config = self._config.get('database', {})
        
        # Check connection configuration
        if 'connection' in db_config:
            connection = db_config['connection']
            
            # Validate path
            if 'path' not in connection:
                logger.warning("Database path not specified, using default")


# Global configuration instance
config = ConfigManager()


# Convenience functions for common configuration access

def get_sensor_config(sensor_type: str) -> Dict[str, Any]:
    """
    Get configuration for specific sensor.
    
    Args:
        sensor_type: Sensor type ('camera', 'microphone', 'air_quality')
    
    Returns:
        Dict: Sensor configuration
    
    Raises:
        ValueError: If sensor_type is not supported
    """
    valid_sensors = ['camera', 'microphone', 'air_quality']
    if sensor_type not in valid_sensors:
        raise ValueError(f"Invalid sensor type: {sensor_type}. Must be one of {valid_sensors}")
    
    return config.get(f'sensors.{sensor_type}', default={})


def get_api_config() -> Dict[str, Any]:
    """Get API configuration."""
    return config.get_section('api')


def get_database_config() -> Dict[str, Any]:
    """Get database configuration."""
    return config.get_section('database')


def get_analytics_config() -> Dict[str, Any]:
    """Get analytics configuration."""
    return config.get_section('analytics')


def is_mock_mode(sensor_type: str) -> bool:
    """
    Check if sensor is configured for mock mode.
    
    Args:
        sensor_type: Sensor type ('camera', 'microphone', 'air_quality')
    
    Returns:
        bool: True if mock mode enabled
    
    Raises:
        ValueError: If sensor_type is not supported
    """
    valid_sensors = ['camera', 'microphone', 'air_quality']
    if sensor_type not in valid_sensors:
        raise ValueError(f"Invalid sensor type: {sensor_type}. Must be one of {valid_sensors}")
    
    return config.get(f'sensors.{sensor_type}.mock_mode', default=False)
