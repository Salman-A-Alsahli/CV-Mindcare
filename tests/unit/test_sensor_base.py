"""
Unit Tests for Base Sensor Class (Phase 2)
-------------------------------------------
Tests for the abstract base sensor with all status states and mock mode support.
"""

import pytest
import time
from datetime import datetime
from typing import Dict, Any

from backend.sensors.base import (
    BaseSensor,
    SensorStatus,
    SensorError,
    SensorUnavailableError,
    SensorConfigError,
)


class MockSensor(BaseSensor):
    """Concrete implementation of BaseSensor for testing."""

    def __init__(self, name="Test Sensor", sensor_type="test", config=None):
        super().__init__(name, sensor_type, config)
        self.initialize_called = False
        self.capture_called = False
        self.capture_mock_called = False
        self.cleanup_called = False
        self.should_fail_init = False
        self.should_fail_capture = False
        self.hardware_available = True

    def initialize(self) -> bool:
        self.initialize_called = True
        if self.should_fail_init:
            return False
        return True

    def capture(self) -> Dict[str, Any]:
        self.capture_called = True
        if self.should_fail_capture:
            raise SensorError("Capture failed")
        return {
            "timestamp": datetime.now().isoformat(),
            "sensor_type": self.sensor_type,
            "value": 42.0,
            "raw_data": "real data",
        }

    def capture_mock_data(self) -> Dict[str, Any]:
        self.capture_mock_called = True
        return {
            "timestamp": datetime.now().isoformat(),
            "sensor_type": self.sensor_type,
            "value": 99.0,
            "raw_data": "mock data",
        }

    def cleanup(self) -> bool:
        self.cleanup_called = True
        return True

    def check_hardware_available(self) -> bool:
        return self.hardware_available


class TestSensorStatus:
    """Test SensorStatus enum."""

    def test_status_values(self):
        """Test all status values are defined."""
        assert SensorStatus.INACTIVE.value == "inactive"
        assert SensorStatus.AVAILABLE.value == "available"
        assert SensorStatus.ACTIVE.value == "active"
        assert SensorStatus.ERROR.value == "error"
        assert SensorStatus.UNAVAILABLE.value == "unavailable"
        assert SensorStatus.MOCK_MODE.value == "mock_mode"


class TestBaseSensorInitialization:
    """Test sensor initialization."""

    def test_basic_init(self):
        """Test basic sensor initialization."""
        sensor = MockSensor()
        assert sensor.name == "Test Sensor"
        assert sensor.sensor_type == "test"
        assert sensor.status == SensorStatus.INACTIVE
        assert sensor.error_message is None
        assert sensor.mock_mode is False

    def test_init_with_config(self):
        """Test initialization with configuration."""
        config = {"mock_mode": True, "some_option": "value"}
        sensor = MockSensor(config=config)
        assert sensor.config == config
        assert sensor.mock_mode is True

    def test_init_with_name_and_type(self):
        """Test initialization with custom name and type."""
        sensor = MockSensor(name="My Sensor", sensor_type="camera")
        assert sensor.name == "My Sensor"
        assert sensor.sensor_type == "camera"


class TestSensorStartStop:
    """Test sensor start and stop operations."""

    def test_start_success(self):
        """Test successful sensor start with real hardware."""
        sensor = MockSensor()
        result = sensor.start()

        assert result is True
        assert sensor.status == SensorStatus.ACTIVE
        assert sensor.initialize_called is True
        assert sensor.is_active() is True

    def test_start_already_active(self):
        """Test starting an already active sensor."""
        sensor = MockSensor()
        sensor.start()
        result = sensor.start()  # Start again

        assert result is True
        assert sensor.status == SensorStatus.ACTIVE

    def test_start_with_mock_mode_config(self):
        """Test starting sensor with mock_mode in config."""
        sensor = MockSensor(config={"mock_mode": True})
        result = sensor.start()

        assert result is True
        assert sensor.status == SensorStatus.MOCK_MODE
        assert sensor.mock_mode is True
        assert sensor.initialize_called is False  # Real init not called

    def test_start_hardware_unavailable(self):
        """Test sensor falls back to mock mode when hardware unavailable."""
        sensor = MockSensor()
        sensor.hardware_available = False
        result = sensor.start()

        assert result is True
        assert sensor.status == SensorStatus.MOCK_MODE
        assert sensor.mock_mode is True

    def test_start_init_fails_fallback_mock(self):
        """Test sensor falls back to mock mode when init fails."""
        sensor = MockSensor()
        sensor.should_fail_init = True
        result = sensor.start()

        assert result is True
        assert sensor.status == SensorStatus.MOCK_MODE
        assert sensor.mock_mode is True

    def test_stop_success(self):
        """Test successful sensor stop."""
        sensor = MockSensor()
        sensor.start()
        result = sensor.stop()

        assert result is True
        assert sensor.status == SensorStatus.INACTIVE
        assert sensor.cleanup_called is True
        assert sensor.is_active() is False

    def test_stop_already_inactive(self):
        """Test stopping an already inactive sensor."""
        sensor = MockSensor()
        result = sensor.stop()

        assert result is True
        assert sensor.status == SensorStatus.INACTIVE


class TestSensorCapture:
    """Test sensor data capture."""

    def test_capture_real_data(self):
        """Test capturing real data from active sensor."""
        sensor = MockSensor()
        sensor.start()
        data = sensor.read()

        assert data is not None
        assert data["mock_mode"] is False
        assert data["value"] == 42.0
        assert data["raw_data"] == "real data"
        assert sensor.capture_called is True

    def test_capture_mock_data(self):
        """Test capturing mock data in mock mode."""
        sensor = MockSensor(config={"mock_mode": True})
        sensor.start()
        data = sensor.read()

        assert data is not None
        assert data["mock_mode"] is True
        assert data["value"] == 99.0
        assert data["raw_data"] == "mock data"
        assert sensor.capture_mock_called is True
        assert sensor.capture_called is False

    def test_capture_when_inactive(self):
        """Test capturing data from inactive sensor raises error."""
        sensor = MockSensor()
        with pytest.raises(SensorError, match="is not active"):
            sensor.read()

    def test_capture_error_handling(self):
        """Test error handling during capture."""
        sensor = MockSensor()
        sensor.should_fail_capture = True
        sensor.start()

        with pytest.raises(SensorError, match="Failed to read"):
            sensor.read()

        assert sensor.status == SensorStatus.ERROR
        assert sensor.error_message is not None


class TestSensorStatusReporting:
    """Test sensor status reporting."""

    def test_get_status_inactive(self):
        """Test status of inactive sensor."""
        sensor = MockSensor()
        status = sensor.get_status()

        assert status["name"] == "Test Sensor"
        assert status["type"] == "test"
        assert status["status"] == "inactive"
        assert status["active"] is False
        assert status["mock_mode"] is False
        assert status["uptime_seconds"] == 0

    def test_get_status_active(self):
        """Test status of active sensor."""
        sensor = MockSensor()
        sensor.start()
        status = sensor.get_status()

        assert status["status"] == "active"
        assert status["active"] is True
        assert status["mock_mode"] is False
        assert status["uptime_seconds"] > 0

    def test_get_status_mock_mode(self):
        """Test status of sensor in mock mode."""
        sensor = MockSensor(config={"mock_mode": True})
        sensor.start()
        status = sensor.get_status()

        assert status["status"] == "mock_mode"
        assert status["active"] is True
        assert status["mock_mode"] is True

    def test_get_status_with_error(self):
        """Test status when sensor has error."""
        sensor = MockSensor()
        sensor.status = SensorStatus.ERROR
        sensor.error_message = "Test error"
        status = sensor.get_status()

        assert status["status"] == "error"
        assert status["active"] is False
        assert status["error_message"] == "Test error"

    def test_is_available(self):
        """Test is_available method."""
        sensor = MockSensor()
        assert sensor.is_available() is True

        sensor.status = SensorStatus.UNAVAILABLE
        assert sensor.is_available() is False

    def test_is_active(self):
        """Test is_active method for different statuses."""
        sensor = MockSensor()
        assert sensor.is_active() is False

        sensor.start()
        assert sensor.is_active() is True

        sensor.stop()
        assert sensor.is_active() is False

        # Test mock mode is also considered active
        sensor = MockSensor(config={"mock_mode": True})
        sensor.start()
        assert sensor.is_active() is True


class TestSensorConfiguration:
    """Test sensor configuration management."""

    def test_update_config(self):
        """Test updating sensor configuration."""
        sensor = MockSensor()
        result = sensor.update_config({"new_option": "value"})

        assert result is True
        assert sensor.config["new_option"] == "value"

    def test_config_persistence(self):
        """Test configuration persists across operations."""
        config = {"option1": "value1", "option2": "value2"}
        sensor = MockSensor(config=config)

        sensor.start()
        sensor.stop()

        assert sensor.config == config


class TestSensorExceptions:
    """Test custom sensor exceptions."""

    def test_sensor_error(self):
        """Test SensorError exception."""
        with pytest.raises(SensorError, match="test error"):
            raise SensorError("test error")

    def test_sensor_unavailable_error(self):
        """Test SensorUnavailableError exception."""
        with pytest.raises(SensorUnavailableError, match="hardware not found"):
            raise SensorUnavailableError("hardware not found")

    def test_sensor_config_error(self):
        """Test SensorConfigError exception."""
        with pytest.raises(SensorConfigError, match="invalid config"):
            raise SensorConfigError("invalid config")


class TestSensorRepr:
    """Test sensor string representation."""

    def test_repr(self):
        """Test __repr__ method."""
        sensor = MockSensor(name="My Sensor")
        repr_str = repr(sensor)

        assert "MockSensor" in repr_str
        assert "My Sensor" in repr_str
        assert "inactive" in repr_str


class TestSensorEdgeCases:
    """Test edge cases and error scenarios."""

    def test_multiple_start_stop_cycles(self):
        """Test multiple start/stop cycles."""
        sensor = MockSensor()

        for _ in range(3):
            assert sensor.start() is True
            assert sensor.is_active() is True
            assert sensor.stop() is True
            assert sensor.is_active() is False

    def test_mock_mode_after_hardware_failure(self):
        """Test sensor switches to mock mode after hardware becomes unavailable."""
        sensor = MockSensor()
        sensor.start()
        assert sensor.status == SensorStatus.ACTIVE

        sensor.stop()
        sensor.hardware_available = False
        sensor.start()
        assert sensor.status == SensorStatus.MOCK_MODE

    def test_uptime_calculation(self):
        """Test uptime is calculated correctly."""
        sensor = MockSensor()
        sensor.start()

        time.sleep(0.1)  # Wait a bit
        status = sensor.get_status()

        assert status["uptime_seconds"] > 0
        assert status["uptime_seconds"] < 1  # Should be less than 1 second
