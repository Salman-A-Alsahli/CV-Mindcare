"""
Unit Tests for Camera Sensor (Phase 3)
---------------------------------------
Tests for camera sensor with greenery detection and mock mode support.
"""

import pytest
import numpy as np
from datetime import datetime
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

from backend.sensors.camera_sensor import CameraSensor, get_camera_reading, check_camera_available
from backend.sensors.base import SensorStatus, SensorError


class TestCameraSensorInitialization:
    """Test camera sensor initialization."""
    
    def test_basic_init(self):
        """Test basic sensor initialization."""
        sensor = CameraSensor()
        assert sensor.name == "Camera Sensor"
        assert sensor.sensor_type == "camera"
        assert sensor.camera_index == 0
        assert sensor.backend == 'opencv'
        assert sensor.resolution == (640, 480)
    
    def test_init_with_config(self):
        """Test initialization with custom configuration."""
        config = {
            'camera_index': 1,
            'backend': 'picamera2',
            'resolution': (1280, 720),
            'green_hue_range': (30, 90),
            'mock_mode': True,
        }
        sensor = CameraSensor(config=config)
        
        assert sensor.camera_index == 1
        assert sensor.backend == 'picamera2'
        assert sensor.resolution == (1280, 720)
        assert sensor.green_hue_range == (30, 90)
        assert sensor.mock_mode is True
    
    def test_init_hsv_parameters(self):
        """Test HSV parameters initialization."""
        sensor = CameraSensor()
        assert sensor.green_hue_range == (35, 85)
        assert sensor.saturation_min == 40
        assert sensor.value_min == 40


class TestCameraMockMode:
    """Test camera mock mode functionality."""
    
    def test_start_in_mock_mode(self):
        """Test starting sensor in mock mode."""
        sensor = CameraSensor(config={'mock_mode': True})
        result = sensor.start()
        
        assert result is True
        assert sensor.status == SensorStatus.MOCK_MODE
        assert sensor.is_active() is True
    
    def test_mock_data_generation(self):
        """Test mock data generation."""
        sensor = CameraSensor(config={'mock_mode': True})
        sensor.start()
        
        data = sensor.read()
        
        assert data is not None
        assert 'timestamp' in data
        assert 'sensor_type' in data
        assert data['sensor_type'] == 'camera'
        assert 'greenery_percentage' in data
        assert 0 <= data['greenery_percentage'] <= 100
        assert 'resolution' in data
        assert 'hsv_params' in data
        assert data['mock_mode'] is True
    
    def test_mock_data_scenarios(self):
        """Test that mock data generates varied scenarios."""
        sensor = CameraSensor(config={'mock_mode': True})
        sensor.start()
        
        # Generate multiple samples to check variety
        samples = [sensor.read()['greenery_percentage'] for _ in range(10)]
        
        # Should have some variation
        assert len(set(samples)) > 1  # Not all the same
        assert all(0 <= s <= 100 for s in samples)  # All within valid range
    
    def test_mock_data_structure(self):
        """Test mock data has correct structure."""
        sensor = CameraSensor(config={'mock_mode': True})
        sensor.start()
        
        data = sensor.read()
        
        # Check all required fields
        required_fields = [
            'timestamp', 'sensor_type', 'greenery_percentage',
            'resolution', 'frame_shape', 'hsv_params'
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Check HSV params structure
        assert 'hue_range' in data['hsv_params']
        assert 'saturation_min' in data['hsv_params']
        assert 'value_min' in data['hsv_params']


@patch('cv2.VideoCapture')
class TestCameraOpenCVBackend:
    """Test OpenCV backend functionality."""
    
    def test_hardware_check_available(self, mock_videocapture):
        """Test hardware availability check when camera is available."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_videocapture.return_value = mock_cap
        
        sensor = CameraSensor()
        available = sensor.check_hardware_available()
        
        assert available is True
        mock_cap.release.assert_called_once()
    
    def test_hardware_check_unavailable(self, mock_videocapture):
        """Test hardware availability check when camera is unavailable."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_videocapture.return_value = mock_cap
        
        sensor = CameraSensor()
        available = sensor.check_hardware_available()
        
        assert available is False
    
    def test_hardware_check_exception(self, mock_videocapture):
        """Test hardware check handles exceptions."""
        mock_videocapture.side_effect = Exception("Camera error")
        
        sensor = CameraSensor()
        available = sensor.check_hardware_available()
        
        assert available is False
    
    @patch('cv2.cvtColor')
    @patch('cv2.inRange')
    def test_initialize_opencv(self, mock_inrange, mock_cvtcolor, mock_videocapture):
        """Test OpenCV initialization."""
        # Mock successful camera opening
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_videocapture.return_value = mock_cap
        
        sensor = CameraSensor()
        result = sensor.initialize()
        
        assert result is True
        assert sensor.cap is not None
    
    @patch('cv2.cvtColor')
    @patch('cv2.inRange')
    def test_capture_real_frame(self, mock_inrange, mock_cvtcolor, mock_videocapture):
        """Test capturing and analyzing real frame."""
        # Mock camera and frame
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cap.read.return_value = (True, mock_frame)
        mock_videocapture.return_value = mock_cap
        
        # Mock HSV conversion and mask
        mock_cvtcolor.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_mask = np.zeros((480, 640), dtype=np.uint8)
        mock_mask[0:100, 0:100] = 255  # 10000 green pixels out of 307200 total
        mock_inrange.return_value = mock_mask
        
        sensor = CameraSensor()
        sensor.start()
        
        data = sensor.read()
        
        assert data is not None
        assert 'greenery_percentage' in data
        assert data['greenery_percentage'] > 0
        assert data['mock_mode'] is False
    
    def test_cleanup_opencv(self, mock_videocapture):
        """Test OpenCV cleanup."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_videocapture.return_value = mock_cap
        
        sensor = CameraSensor()
        sensor.initialize()
        result = sensor.cleanup()
        
        assert result is True
        mock_cap.release.assert_called()


class TestGreeneryDetectionAlgorithm:
    """Test greenery detection algorithm."""
    
    @patch('cv2.VideoCapture')
    @patch('cv2.cvtColor')
    @patch('cv2.inRange')
    def test_greenery_percentage_calculation(self, mock_inrange, mock_cvtcolor, mock_videocapture):
        """Test greenery percentage calculation."""
        # Setup mocks
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_cap.read.return_value = (True, mock_frame)
        mock_videocapture.return_value = mock_cap
        
        mock_cvtcolor.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Create mask with 25% green pixels
        mock_mask = np.zeros((100, 100), dtype=np.uint8)
        mock_mask[0:50, 0:50] = 255  # 2500 out of 10000 pixels = 25%
        mock_inrange.return_value = mock_mask
        
        sensor = CameraSensor()
        sensor.start()
        
        data = sensor.read()
        
        # Should be approximately 25%
        assert 24 <= data['greenery_percentage'] <= 26
    
    @patch('cv2.VideoCapture')
    @patch('cv2.cvtColor')
    @patch('cv2.inRange')
    def test_no_greenery_detection(self, mock_inrange, mock_cvtcolor, mock_videocapture):
        """Test when no greenery is detected."""
        # Setup mocks
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_cap.read.return_value = (True, mock_frame)
        mock_videocapture.return_value = mock_cap
        
        mock_cvtcolor.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Create mask with no green pixels
        mock_mask = np.zeros((100, 100), dtype=np.uint8)
        mock_inrange.return_value = mock_mask
        
        sensor = CameraSensor()
        sensor.start()
        
        data = sensor.read()
        
        assert data['greenery_percentage'] == 0.0
    
    @patch('cv2.VideoCapture')
    @patch('cv2.cvtColor')
    @patch('cv2.inRange')
    def test_full_greenery_detection(self, mock_inrange, mock_cvtcolor, mock_videocapture):
        """Test when full greenery is detected."""
        # Setup mocks
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_cap.read.return_value = (True, mock_frame)
        mock_videocapture.return_value = mock_cap
        
        mock_cvtcolor.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Create mask with all green pixels
        mock_mask = np.ones((100, 100), dtype=np.uint8) * 255
        mock_inrange.return_value = mock_mask
        
        sensor = CameraSensor()
        sensor.start()
        
        data = sensor.read()
        
        assert data['greenery_percentage'] == 100.0


class TestCameraFallbackMechanism:
    """Test automatic fallback to mock mode."""
    
    @patch('cv2.VideoCapture')
    def test_fallback_when_hardware_unavailable(self, mock_videocapture):
        """Test sensor falls back to mock mode when hardware unavailable."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_videocapture.return_value = mock_cap
        
        sensor = CameraSensor()
        result = sensor.start()
        
        assert result is True
        assert sensor.status == SensorStatus.MOCK_MODE
        assert sensor.mock_mode is True
    
    @patch('cv2.VideoCapture')
    def test_data_capture_in_fallback_mode(self, mock_videocapture):
        """Test data capture works in fallback mode."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_videocapture.return_value = mock_cap
        
        sensor = CameraSensor()
        sensor.start()
        
        data = sensor.read()
        
        assert data is not None
        assert 'greenery_percentage' in data
        assert data['mock_mode'] is True


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @patch('backend.sensors.camera_sensor.CameraSensor')
    def test_get_camera_reading(self, mock_sensor_class):
        """Test get_camera_reading convenience function."""
        mock_sensor = MagicMock()
        mock_sensor.read.return_value = {
            'timestamp': datetime.now().isoformat(),
            'greenery_percentage': 25.0,
            'mock_mode': True,
        }
        mock_sensor_class.return_value = mock_sensor
        
        result = get_camera_reading(camera_index=0)
        
        assert result is not None
        assert 'greenery_percentage' in result
        mock_sensor.start.assert_called_once()
        mock_sensor.stop.assert_called_once()
    
    @patch('backend.sensors.camera_sensor.CameraSensor')
    def test_check_camera_available(self, mock_sensor_class):
        """Test check_camera_available convenience function."""
        mock_sensor = MagicMock()
        mock_sensor.check_hardware_available.return_value = True
        mock_sensor_class.return_value = mock_sensor
        
        result = check_camera_available(camera_index=0)
        
        assert result is True
        mock_sensor.check_hardware_available.assert_called_once()


class TestCameraConfiguration:
    """Test camera configuration options."""
    
    def test_custom_hsv_parameters(self):
        """Test custom HSV parameters."""
        config = {
            'green_hue_range': (30, 90),
            'saturation_min': 50,
            'value_min': 60,
            'mock_mode': True,
        }
        sensor = CameraSensor(config=config)
        
        assert sensor.green_hue_range == (30, 90)
        assert sensor.saturation_min == 50
        assert sensor.value_min == 60
    
    def test_custom_resolution(self):
        """Test custom resolution setting."""
        config = {
            'resolution': (1280, 720),
            'mock_mode': True,
        }
        sensor = CameraSensor(config=config)
        sensor.start()
        
        data = sensor.read()
        
        assert data['resolution'] == (1280, 720)
    
    def test_backend_selection(self):
        """Test backend selection."""
        config_opencv = {'backend': 'opencv'}
        config_picam = {'backend': 'picamera2'}
        
        sensor_opencv = CameraSensor(config=config_opencv)
        sensor_picam = CameraSensor(config=config_picam)
        
        assert sensor_opencv.backend == 'opencv'
        assert sensor_picam.backend == 'picamera2'


class TestCameraSensorStatus:
    """Test sensor status reporting."""
    
    def test_status_after_init(self):
        """Test status after initialization."""
        sensor = CameraSensor()
        status = sensor.get_status()
        
        assert status['name'] == "Camera Sensor"
        assert status['type'] == 'camera'
        assert status['status'] == 'inactive'
        assert status['active'] is False
    
    def test_status_in_mock_mode(self):
        """Test status when running in mock mode."""
        sensor = CameraSensor(config={'mock_mode': True})
        sensor.start()
        status = sensor.get_status()
        
        assert status['status'] == 'mock_mode'
        assert status['active'] is True
        assert status['mock_mode'] is True
    
    @patch('cv2.VideoCapture')
    def test_status_after_cleanup(self, mock_videocapture):
        """Test status after cleanup."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_videocapture.return_value = mock_cap
        
        sensor = CameraSensor()
        sensor.start()  # Will go to mock mode
        sensor.stop()
        status = sensor.get_status()
        
        assert status['status'] == 'inactive'
        assert status['active'] is False
