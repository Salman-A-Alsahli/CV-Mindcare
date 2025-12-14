"""
Unit Tests for Sensor Auto-Detection
-------------------------------------
Tests for auto backend detection in camera and air quality sensors.
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from backend.sensors.camera_sensor import CameraSensor
from backend.sensors.air_quality import AirQualitySensor
from backend.sensors.base import SensorStatus


class TestCameraAutoDetection:
    """Test camera sensor auto backend detection."""

    def test_auto_backend_config(self):
        """Test that auto backend is properly configured."""
        sensor = CameraSensor(config={"backend": "auto"})
        assert sensor.backend == "auto"

    @patch('backend.sensors.camera_sensor.CameraSensor._check_picamera2_available')
    @patch('backend.sensors.camera_sensor.CameraSensor._check_opencv_available')
    def test_check_hardware_auto_picamera2_first(self, mock_opencv, mock_picamera2):
        """Test that auto detection checks picamera2 first."""
        mock_picamera2.return_value = True
        mock_opencv.return_value = True
        
        sensor = CameraSensor(config={"backend": "auto"})
        result = sensor.check_hardware_available()
        
        assert result is True
        mock_picamera2.assert_called_once()
        # OpenCV should not be called if picamera2 is available
        mock_opencv.assert_not_called()

    @patch('backend.sensors.camera_sensor.CameraSensor._check_picamera2_available')
    @patch('backend.sensors.camera_sensor.CameraSensor._check_opencv_available')
    def test_check_hardware_auto_fallback_opencv(self, mock_opencv, mock_picamera2):
        """Test that auto detection falls back to opencv."""
        mock_picamera2.return_value = False
        mock_opencv.return_value = True
        
        sensor = CameraSensor(config={"backend": "auto"})
        result = sensor.check_hardware_available()
        
        assert result is True
        mock_picamera2.assert_called_once()
        mock_opencv.assert_called_once()

    @patch('backend.sensors.camera_sensor.CameraSensor._check_picamera2_available')
    @patch('backend.sensors.camera_sensor.CameraSensor._check_opencv_available')
    def test_check_hardware_auto_none_available(self, mock_opencv, mock_picamera2):
        """Test auto detection when no hardware available."""
        mock_picamera2.return_value = False
        mock_opencv.return_value = False
        
        sensor = CameraSensor(config={"backend": "auto"})
        result = sensor.check_hardware_available()
        
        assert result is False

    @patch('backend.sensors.camera_sensor.CameraSensor._initialize_picamera2')
    @patch('backend.sensors.camera_sensor.CameraSensor._initialize_opencv')
    def test_initialize_auto_selects_picamera2(self, mock_opencv, mock_picamera2):
        """Test that auto initialization selects picamera2 when available."""
        mock_picamera2.return_value = True
        
        sensor = CameraSensor(config={"backend": "auto"})
        result = sensor.initialize()
        
        assert result is True
        assert sensor.backend == "picamera2"
        mock_picamera2.assert_called_once()
        mock_opencv.assert_not_called()

    @patch('backend.sensors.camera_sensor.CameraSensor._initialize_picamera2')
    @patch('backend.sensors.camera_sensor.CameraSensor._initialize_opencv')
    def test_initialize_auto_fallback_opencv(self, mock_opencv, mock_picamera2):
        """Test that auto initialization falls back to opencv."""
        mock_picamera2.side_effect = Exception("Picamera2 not available")
        mock_opencv.return_value = True
        
        sensor = CameraSensor(config={"backend": "auto"})
        result = sensor.initialize()
        
        assert result is True
        assert sensor.backend == "opencv"
        mock_picamera2.assert_called_once()
        mock_opencv.assert_called_once()


class TestAirQualityI2CDetection:
    """Test air quality sensor I2C device detection."""

    def test_i2c_scan_detects_configured_address(self):
        """Test that I2C scan detects device at configured address."""
        # Mock the board and busio modules
        mock_board = MagicMock()
        mock_busio = MagicMock()
        mock_i2c = MagicMock()
        mock_i2c.scan.return_value = [0x4b]
        mock_busio.I2C.return_value = mock_i2c
        
        with patch.dict(sys.modules, {'board': mock_board, 'busio': mock_busio}):
            sensor = AirQualitySensor(config={
                "backend": "i2c",
                "i2c": {"address": 0x4b}
            })
            result = sensor.check_hardware_available()
        
        assert result is True
        mock_i2c.scan.assert_called_once()

    def test_i2c_scan_wrong_address(self):
        """Test that I2C scan fails when device at different address."""
        # Mock the board and busio modules
        mock_board = MagicMock()
        mock_busio = MagicMock()
        mock_i2c = MagicMock()
        mock_i2c.scan.return_value = [0x4b]
        mock_busio.I2C.return_value = mock_i2c
        
        with patch.dict(sys.modules, {'board': mock_board, 'busio': mock_busio}):
            sensor = AirQualitySensor(config={
                "backend": "i2c",
                "i2c": {"address": 0x48}  # Default ADS1115 address
            })
            result = sensor.check_hardware_available()
        
        # Should not detect since address doesn't match
        assert result is False

    def test_i2c_scan_no_devices(self):
        """Test I2C scan when no devices detected."""
        # Mock the board and busio modules
        mock_board = MagicMock()
        mock_busio = MagicMock()
        mock_i2c = MagicMock()
        mock_i2c.scan.return_value = []
        mock_busio.I2C.return_value = mock_i2c
        
        with patch.dict(sys.modules, {'board': mock_board, 'busio': mock_busio}):
            sensor = AirQualitySensor(config={"backend": "i2c"})
            result = sensor.check_hardware_available()
        
        assert result is False
