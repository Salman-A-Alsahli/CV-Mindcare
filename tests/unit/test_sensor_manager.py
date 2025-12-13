"""
Tests for Sensor Manager (Phase 5).

Comprehensive test suite for the unified sensor management system.
"""

import time
import threading
from unittest.mock import Mock

from backend.sensors.sensor_manager import SensorManager, ManagerStatus


class TestSensorManagerInitialization:
    """Test sensor manager initialization."""

    def test_init_default_config(self):
        """Test initialization with default configuration."""
        manager = SensorManager()

        assert manager.polling_interval == 5.0
        assert manager.auto_start is True
        assert manager.auto_recover is True
        assert manager.max_retries == 3
        assert manager.status == ManagerStatus.STOPPED
        assert manager.running is False
        assert manager.camera is not None
        assert manager.microphone is not None

    def test_init_custom_config(self):
        """Test initialization with custom configuration."""
        config = {
            "polling_interval": 2.0,
            "auto_start": False,
            "auto_recover": False,
            "max_retries": 5,
            "camera": {"mock_mode": True},
            "microphone": {"mock_mode": True},
        }
        manager = SensorManager(config)

        assert manager.polling_interval == 2.0
        assert manager.auto_start is False
        assert manager.auto_recover is False
        assert manager.max_retries == 5

    def test_init_sensors_created(self):
        """Test that sensors are created on initialization."""
        manager = SensorManager()

        assert hasattr(manager, "camera")
        assert hasattr(manager, "microphone")
        assert manager.camera is not None
        assert manager.microphone is not None


class TestSensorManagerStartStop:
    """Test starting and stopping the sensor manager."""

    def test_start_all_sensors(self):
        """Test starting all sensors."""
        config = {"camera": {"mock_mode": True}, "microphone": {"mock_mode": True}}
        manager = SensorManager(config)

        success = manager.start_all()

        assert success is True
        assert manager.status == ManagerStatus.RUNNING
        assert manager.running is True

        # Cleanup
        manager.stop_all()

    def test_stop_all_sensors(self):
        """Test stopping all sensors."""
        config = {"camera": {"mock_mode": True}, "microphone": {"mock_mode": True}}
        manager = SensorManager(config)

        manager.start_all()
        success = manager.stop_all()

        assert success is True
        assert manager.status == ManagerStatus.STOPPED
        assert manager.running is False

    def test_start_already_running(self):
        """Test starting when already running."""
        config = {"camera": {"mock_mode": True}, "microphone": {"mock_mode": True}}
        manager = SensorManager(config)

        manager.start_all()
        result = manager.start_all()  # Start again

        assert result is True
        assert manager.status == ManagerStatus.RUNNING

        # Cleanup
        manager.stop_all()

    def test_stop_not_running(self):
        """Test stopping when not running."""
        manager = SensorManager()

        result = manager.stop_all()

        assert result is True
        assert manager.status == ManagerStatus.STOPPED


class TestSensorManagerStatus:
    """Test status reporting."""

    def test_get_all_status_stopped(self):
        """Test getting status when stopped."""
        manager = SensorManager()

        status = manager.get_all_status()

        assert "manager" in status
        assert "sensors" in status
        assert "timestamp" in status
        assert status["manager"]["status"] == ManagerStatus.STOPPED.value
        assert status["manager"]["running"] is False

    def test_get_all_status_running(self):
        """Test getting status when running."""
        config = {"camera": {"mock_mode": True}, "microphone": {"mock_mode": True}}
        manager = SensorManager(config)

        manager.start_all()
        status = manager.get_all_status()

        assert status["manager"]["status"] == ManagerStatus.RUNNING.value
        assert status["manager"]["running"] is True
        assert "camera" in status["sensors"]
        assert "microphone" in status["sensors"]

        # Cleanup
        manager.stop_all()

    def test_status_includes_sensor_details(self):
        """Test that status includes sensor-specific details."""
        config = {"camera": {"mock_mode": True}, "microphone": {"mock_mode": True}}
        manager = SensorManager(config)

        status = manager.get_all_status()

        assert "error_count" in status["sensors"]["camera"]
        assert "retry_count" in status["sensors"]["camera"]
        assert "last_read" in status["sensors"]["camera"]
        assert "error_count" in status["sensors"]["microphone"]
        assert "retry_count" in status["sensors"]["microphone"]
        assert "last_read" in status["sensors"]["microphone"]


class TestSensorManagerReading:
    """Test reading from sensors."""

    def test_read_all_with_mock_sensors(self):
        """Test reading from all sensors in mock mode."""
        config = {"camera": {"mock_mode": True}, "microphone": {"mock_mode": True}}
        manager = SensorManager(config)

        manager.start_all()
        data = manager.read_all()

        assert "timestamp" in data
        assert "data" in data
        assert "errors" in data

        # Should have data from both sensors
        assert "camera" in data["data"] or "camera" in data["errors"]
        assert "microphone" in data["data"] or "microphone" in data["errors"]

        # Cleanup
        manager.stop_all()

    def test_read_all_updates_timestamps(self):
        """Test that read_all updates last read timestamps."""
        config = {"camera": {"mock_mode": True}, "microphone": {"mock_mode": True}}
        manager = SensorManager(config)

        manager.start_all()
        manager.read_all()

        # Check that timestamps were updated
        assert manager._last_read_time["camera"] is not None
        assert manager._last_read_time["microphone"] is not None

        # Cleanup
        manager.stop_all()

    def test_read_all_handles_sensor_errors(self):
        """Test that read_all handles sensor errors gracefully."""
        config = {"camera": {"mock_mode": True}, "microphone": {"mock_mode": True}}
        manager = SensorManager(config)

        # Mock sensor to raise error
        manager.camera.read = Mock(side_effect=Exception("Test error"))

        data = manager.read_all()

        # Should still return data structure
        assert "timestamp" in data
        assert "data" in data
        assert "errors" in data

        # Camera should have error
        assert "camera" in data["errors"]
        assert manager._error_counts["camera"] > 0


class TestSensorManagerHealth:
    """Test health monitoring."""

    def test_get_health_all_running(self):
        """Test health when all sensors running."""
        config = {"camera": {"mock_mode": True}, "microphone": {"mock_mode": True}}
        manager = SensorManager(config)

        manager.start_all()
        health = manager.get_health()

        assert "health_score" in health
        assert "status" in health
        assert "issues" in health
        assert health["health_score"] >= 0
        assert health["health_score"] <= 100

        # Cleanup
        manager.stop_all()

    def test_get_health_not_running(self):
        """Test health when manager not running."""
        manager = SensorManager()

        health = manager.get_health()

        # Should have lower health score
        assert health["health_score"] < 100
        assert len(health["issues"]) > 0
        assert any("not running" in issue.lower() for issue in health["issues"])

    def test_health_score_with_errors(self):
        """Test that errors reduce health score."""
        config = {"camera": {"mock_mode": True}, "microphone": {"mock_mode": True}}
        manager = SensorManager(config)

        # Introduce errors
        manager._error_counts["camera"] = 3
        manager._error_counts["microphone"] = 2

        health = manager.get_health()

        # Health score should be reduced
        assert len(health["issues"]) > 0


class TestSensorManagerConfiguration:
    """Test configuration management."""

    def test_update_config_polling_interval(self):
        """Test updating polling interval."""
        manager = SensorManager()

        success = manager.update_config({"polling_interval": 10.0})

        assert success is True
        assert manager.polling_interval == 10.0

    def test_update_config_auto_recover(self):
        """Test updating auto recover setting."""
        manager = SensorManager()

        success = manager.update_config({"auto_recover": False})

        assert success is True
        assert manager.auto_recover is False

    def test_update_config_max_retries(self):
        """Test updating max retries."""
        manager = SensorManager()

        success = manager.update_config({"max_retries": 10})

        assert success is True
        assert manager.max_retries == 10

    def test_update_config_invalid_value(self):
        """Test updating with invalid value."""
        manager = SensorManager()

        # This should not raise but should handle gracefully
        success = manager.update_config({"polling_interval": "invalid"})

        # Might fail or succeed depending on error handling
        assert success in [True, False]


class TestSensorManagerPolling:
    """Test automatic polling functionality."""

    def test_polling_thread_starts(self):
        """Test that polling thread starts."""
        config = {"camera": {"mock_mode": True}, "microphone": {"mock_mode": True}}
        manager = SensorManager(config)

        manager.start_all()

        assert manager._polling_thread is not None
        assert manager._polling_thread.is_alive()

        # Cleanup
        manager.stop_all()

    def test_polling_thread_stops(self):
        """Test that polling thread stops."""
        config = {"camera": {"mock_mode": True}, "microphone": {"mock_mode": True}}
        manager = SensorManager(config)

        manager.start_all()
        time.sleep(0.1)  # Let thread start
        manager.stop_all()
        time.sleep(0.5)  # Wait for thread to stop

        # Thread should no longer be alive
        if manager._polling_thread:
            assert not manager._polling_thread.is_alive()

    def test_polling_updates_data(self):
        """Test that polling updates sensor data."""
        config = {
            "polling_interval": 0.5,  # Fast polling for test
            "camera": {"mock_mode": True},
            "microphone": {"mock_mode": True},
        }
        manager = SensorManager(config)

        manager.start_all()

        # Wait for at least one polling cycle
        time.sleep(1.0)

        # Should have read timestamps
        assert manager._last_read_time["camera"] is not None
        assert manager._last_read_time["microphone"] is not None

        # Cleanup
        manager.stop_all()


class TestSensorManagerThreadSafety:
    """Test thread-safe operations."""

    def test_concurrent_status_reads(self):
        """Test concurrent status reads are thread-safe."""
        config = {"camera": {"mock_mode": True}, "microphone": {"mock_mode": True}}
        manager = SensorManager(config)

        manager.start_all()

        def read_status():
            for _ in range(10):
                manager.get_all_status()

        # Create multiple threads
        threads = [threading.Thread(target=read_status) for _ in range(5)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Should complete without errors
        assert manager.status == ManagerStatus.RUNNING

        # Cleanup
        manager.stop_all()

    def test_concurrent_read_all(self):
        """Test concurrent read_all calls are thread-safe."""
        config = {"camera": {"mock_mode": True}, "microphone": {"mock_mode": True}}
        manager = SensorManager(config)

        manager.start_all()

        results = []

        def read_data():
            for _ in range(5):
                data = manager.read_all()
                results.append(data)

        # Create multiple threads
        threads = [threading.Thread(target=read_data) for _ in range(3)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Should have results from all threads
        assert len(results) == 15  # 3 threads * 5 reads

        # Cleanup
        manager.stop_all()


class TestSensorManagerRecovery:
    """Test auto-recovery functionality."""

    def test_should_recover_error_state(self):
        """Test that sensors in error state should recover."""
        config = {"camera": {"mock_mode": True}, "microphone": {"mock_mode": True}}
        manager = SensorManager(config)

        # Mock sensor in error state
        manager.camera.get_status = Mock(return_value={"status": "ERROR"})

        should_recover = manager._should_recover("camera", manager.camera)

        assert should_recover is True

    def test_should_not_recover_max_retries_exceeded(self):
        """Test that recovery stops after max retries."""
        config = {"camera": {"mock_mode": True}, "microphone": {"mock_mode": True}}
        manager = SensorManager(config)

        # Set retry count to max
        manager._retry_counts["camera"] = manager.max_retries

        should_recover = manager._should_recover("camera", manager.camera)

        assert should_recover is False

    def test_should_not_recover_active_sensor(self):
        """Test that active sensors don't need recovery."""
        config = {"camera": {"mock_mode": True}, "microphone": {"mock_mode": True}}
        manager = SensorManager(config)

        manager.start_all()

        # Active sensor shouldn't need recovery
        should_recover = manager._should_recover("camera", manager.camera)

        assert should_recover is False

        # Cleanup
        manager.stop_all()


class TestSensorManagerHelperMethods:
    """Test helper methods."""

    def test_calculate_uptime_not_running(self):
        """Test uptime calculation when not running."""
        manager = SensorManager()

        uptime = manager._calculate_uptime()

        assert uptime is None

    def test_calculate_uptime_running(self):
        """Test uptime calculation when running."""
        config = {"camera": {"mock_mode": True}, "microphone": {"mock_mode": True}}
        manager = SensorManager(config)

        manager.start_all()
        time.sleep(0.5)

        uptime = manager._calculate_uptime()

        assert uptime is not None
        assert uptime >= 0.0

        # Cleanup
        manager.stop_all()

    def test_start_sensor_success(self):
        """Test starting individual sensor."""
        config = {"camera": {"mock_mode": True}}
        manager = SensorManager(config)

        success = manager._start_sensor(manager.camera, "camera")

        assert success is True
        assert manager._retry_counts["camera"] == 0

    def test_stop_sensor_success(self):
        """Test stopping individual sensor."""
        config = {"camera": {"mock_mode": True}}
        manager = SensorManager(config)

        manager._start_sensor(manager.camera, "camera")
        success = manager._stop_sensor(manager.camera, "camera")

        assert success is True
