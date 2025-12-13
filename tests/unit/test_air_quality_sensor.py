"""
Unit Tests for MQ-135 Air Quality Sensor
-----------------------------------------
Tests for backend/sensors/air_quality.py module.
"""

import pytest
from datetime import datetime
from backend.sensors.air_quality import (
    AirQualitySensor,
    AirQualityLevel,
    get_air_quality_reading,
    check_air_quality_available
)
from backend.sensors.base import SensorStatus, SensorError


class TestAirQualitySensorInitialization:
    """Tests for sensor initialization."""
    
    def test_basic_init(self):
        """Test basic sensor initialization."""
        sensor = AirQualitySensor()
        
        assert sensor.name == "MQ-135 Air Quality Sensor"
        assert sensor.sensor_type == "air_quality"
        assert sensor.status == SensorStatus.INACTIVE
        assert sensor.calibration_factor == 1.0
        assert sensor.sample_count == 10
    
    def test_init_with_config(self):
        """Test initialization with custom configuration."""
        config = {
            'mock_mode': True,
            'calibration_factor': 1.5,
            'sample_count': 5,
            'serial_port': '/dev/ttyUSB1'
        }
        sensor = AirQualitySensor(config)
        
        assert sensor.mock_mode is True
        assert sensor.calibration_factor == 1.5
        assert sensor.sample_count == 5
        assert sensor.serial_port == '/dev/ttyUSB1'
    
    def test_init_default_parameters(self):
        """Test that default parameters are set correctly."""
        sensor = AirQualitySensor()
        
        assert sensor.serial_port == '/dev/ttyUSB0'
        assert sensor.gpio_pin is None
        assert sensor.backend == 'auto'
        assert sensor._serial_connection is None
        assert sensor._adc is None
        assert sensor._last_reading is None


class TestAirQualityMockMode:
    """Tests for mock mode functionality."""
    
    def test_start_in_mock_mode(self):
        """Test starting sensor in mock mode."""
        sensor = AirQualitySensor({'mock_mode': True})
        success = sensor.start()
        
        assert success is True
        assert sensor.status == SensorStatus.MOCK_MODE
        assert sensor.is_active()
        
        sensor.stop()
    
    def test_mock_data_generation(self):
        """Test mock data generation structure and values."""
        sensor = AirQualitySensor({'mock_mode': True})
        sensor.start()
        
        data = sensor.read()
        
        assert 'timestamp' in data
        assert 'sensor_type' in data
        assert 'ppm' in data
        assert 'air_quality_level' in data
        assert 'raw_value' in data
        assert 'calibration_factor' in data
        assert 'sample_count' in data
        assert 'backend' in data
        assert data['mock_mode'] is True
        
        assert data['sensor_type'] == 'air_quality'
        assert data['ppm'] >= 0
        assert data['air_quality_level'] in [
            AirQualityLevel.EXCELLENT,
            AirQualityLevel.GOOD,
            AirQualityLevel.MODERATE,
            AirQualityLevel.POOR,
            AirQualityLevel.HAZARDOUS
        ]
        
        sensor.stop()
    
    def test_mock_data_scenarios(self):
        """Test that mock data covers different air quality scenarios."""
        sensor = AirQualitySensor({'mock_mode': True})
        sensor.start()
        
        # Generate multiple readings to test variety
        levels = set()
        for _ in range(20):
            data = sensor.read()
            levels.add(data['air_quality_level'])
        
        # Should have at least some variety in mock data
        assert len(levels) >= 2
        
        sensor.stop()
    
    def test_mock_data_structure(self):
        """Test mock data structure consistency."""
        sensor = AirQualitySensor({'mock_mode': True})
        sensor.start()
        
        data = sensor.capture_mock_data()
        
        # Verify timestamp format
        timestamp = datetime.fromisoformat(data['timestamp'])
        assert isinstance(timestamp, datetime)
        
        # Verify numeric ranges
        assert 0 <= data['ppm'] <= 300
        assert 0 <= data['raw_value'] <= 1023
        
        sensor.stop()
    
    def test_mock_air_quality_classifications(self):
        """Test that mock data classifications are consistent."""
        sensor = AirQualitySensor({'mock_mode': True})
        sensor.start()
        
        for _ in range(10):
            data = sensor.read()
            ppm = data['ppm']
            level = data['air_quality_level']
            
            # Verify classification matches PPM value
            if ppm <= 50:
                assert level == AirQualityLevel.EXCELLENT
            elif ppm <= 100:
                assert level == AirQualityLevel.GOOD
            elif ppm <= 150:
                assert level == AirQualityLevel.MODERATE
            elif ppm <= 200:
                assert level == AirQualityLevel.POOR
            else:
                assert level == AirQualityLevel.HAZARDOUS
        
        sensor.stop()


class TestAirQualityClassification:
    """Tests for air quality level classification."""
    
    def test_excellent_classification(self):
        """Test excellent air quality classification (0-50 PPM)."""
        sensor = AirQualitySensor()
        
        assert sensor._classify_air_quality(0) == AirQualityLevel.EXCELLENT
        assert sensor._classify_air_quality(25) == AirQualityLevel.EXCELLENT
        assert sensor._classify_air_quality(50) == AirQualityLevel.EXCELLENT
    
    def test_good_classification(self):
        """Test good air quality classification (51-100 PPM)."""
        sensor = AirQualitySensor()
        
        assert sensor._classify_air_quality(51) == AirQualityLevel.GOOD
        assert sensor._classify_air_quality(75) == AirQualityLevel.GOOD
        assert sensor._classify_air_quality(100) == AirQualityLevel.GOOD
    
    def test_moderate_classification(self):
        """Test moderate air quality classification (101-150 PPM)."""
        sensor = AirQualitySensor()
        
        assert sensor._classify_air_quality(101) == AirQualityLevel.MODERATE
        assert sensor._classify_air_quality(125) == AirQualityLevel.MODERATE
        assert sensor._classify_air_quality(150) == AirQualityLevel.MODERATE
    
    def test_poor_classification(self):
        """Test poor air quality classification (151-200 PPM)."""
        sensor = AirQualitySensor()
        
        assert sensor._classify_air_quality(151) == AirQualityLevel.POOR
        assert sensor._classify_air_quality(175) == AirQualityLevel.POOR
        assert sensor._classify_air_quality(200) == AirQualityLevel.POOR
    
    def test_hazardous_classification(self):
        """Test hazardous air quality classification (200+ PPM)."""
        sensor = AirQualitySensor()
        
        assert sensor._classify_air_quality(201) == AirQualityLevel.HAZARDOUS
        assert sensor._classify_air_quality(250) == AirQualityLevel.HAZARDOUS
        assert sensor._classify_air_quality(500) == AirQualityLevel.HAZARDOUS


class TestPPMConversion:
    """Tests for PPM conversion calculations."""
    
    def test_ppm_conversion_zero(self):
        """Test PPM conversion for zero raw value."""
        sensor = AirQualitySensor()
        ppm = sensor._convert_to_ppm(0)
        
        assert ppm == 0.0
    
    def test_ppm_conversion_max(self):
        """Test PPM conversion for maximum raw value."""
        sensor = AirQualitySensor()
        ppm = sensor._convert_to_ppm(1023)
        
        assert ppm == 300.0
    
    def test_ppm_conversion_mid(self):
        """Test PPM conversion for mid-range raw value."""
        sensor = AirQualitySensor()
        ppm = sensor._convert_to_ppm(511.5)  # Half of 1023
        
        assert abs(ppm - 150.0) < 0.1  # Should be ~150 PPM
    
    def test_ppm_conversion_with_calibration(self):
        """Test PPM conversion with custom calibration factor."""
        sensor = AirQualitySensor({'calibration_factor': 2.0})
        ppm = sensor._convert_to_ppm(511.5)
        
        # With 2.0 calibration, should be double
        assert abs(ppm - 300.0) < 0.1
    
    def test_ppm_conversion_non_negative(self):
        """Test that PPM conversion never returns negative values."""
        sensor = AirQualitySensor()
        
        # Even with negative raw value, should return 0
        ppm = sensor._convert_to_ppm(-100)
        assert ppm >= 0


class TestCalibration:
    """Tests for sensor calibration functionality."""
    
    def test_calibration_basic(self):
        """Test basic calibration with known PPM value."""
        sensor = AirQualitySensor({'calibration_factor': 1.0})
        
        # If sensor reads 500 raw when actual is 100 PPM
        # Calibration should adjust factor
        new_factor = sensor.calibrate(known_ppm=100, measured_raw=500)
        
        assert new_factor != 1.0
        assert sensor.calibration_factor == new_factor
    
    def test_calibration_updates_factor(self):
        """Test that calibration updates the calibration factor."""
        sensor = AirQualitySensor()
        original_factor = sensor.calibration_factor
        
        sensor.calibrate(known_ppm=75, measured_raw=512)
        
        assert sensor.calibration_factor != original_factor
    
    def test_calibration_invalid_raw(self):
        """Test calibration with invalid raw value."""
        sensor = AirQualitySensor()
        
        with pytest.raises(ValueError):
            sensor.calibrate(known_ppm=100, measured_raw=0)
        
        with pytest.raises(ValueError):
            sensor.calibrate(known_ppm=100, measured_raw=-50)
    
    def test_get_last_reading(self):
        """Test getting last PPM reading."""
        sensor = AirQualitySensor({'mock_mode': True})
        
        assert sensor.get_last_reading() is None
        
        sensor.start()
        data = sensor.read()
        
        last_reading = sensor.get_last_reading()
        assert last_reading is not None
        assert abs(last_reading - data['ppm']) < 0.01  # Allow for rounding differences
        
        sensor.stop()


class TestSensorCapture:
    """Tests for sensor data capture."""
    
    def test_capture_when_inactive(self):
        """Test that capture fails when sensor is inactive."""
        sensor = AirQualitySensor()
        
        with pytest.raises(SensorError):
            sensor.read()
    
    def test_capture_mock_data_structure(self):
        """Test mock data capture returns correct structure."""
        sensor = AirQualitySensor({'mock_mode': True})
        sensor.start()
        
        data = sensor.read()
        
        required_fields = [
            'timestamp', 'sensor_type', 'ppm', 'air_quality_level',
            'raw_value', 'calibration_factor', 'sample_count', 'backend'
        ]
        
        for field in required_fields:
            assert field in data
        
        sensor.stop()


class TestConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_get_air_quality_reading(self):
        """Test quick reading function."""
        data = get_air_quality_reading({'mock_mode': True})
        
        assert 'ppm' in data
        assert 'air_quality_level' in data
        assert data['sensor_type'] == 'air_quality'
    
    def test_check_air_quality_available(self):
        """Test hardware availability check."""
        # Should return False on systems without MQ-135 hardware
        available = check_air_quality_available()
        
        assert isinstance(available, bool)


class TestSensorConfiguration:
    """Tests for sensor configuration."""
    
    def test_custom_calibration_factor(self):
        """Test custom calibration factor configuration."""
        sensor = AirQualitySensor({'calibration_factor': 2.5})
        
        assert sensor.calibration_factor == 2.5
    
    def test_custom_sample_count(self):
        """Test custom sample count configuration."""
        sensor = AirQualitySensor({'sample_count': 20})
        
        assert sensor.sample_count == 20
    
    def test_backend_selection(self):
        """Test backend selection configuration."""
        sensor = AirQualitySensor({'backend': 'mock'})
        
        assert sensor.backend == 'mock'
    
    def test_serial_port_config(self):
        """Test serial port configuration."""
        sensor = AirQualitySensor({'serial_port': '/dev/ttyACM0'})
        
        assert sensor.serial_port == '/dev/ttyACM0'
    
    def test_gpio_pin_config(self):
        """Test GPIO pin configuration."""
        sensor = AirQualitySensor({'gpio_pin': 7})
        
        assert sensor.gpio_pin == 7


class TestSensorStatus:
    """Tests for sensor status tracking."""
    
    def test_status_after_init(self):
        """Test sensor status after initialization."""
        sensor = AirQualitySensor()
        
        status = sensor.get_status()
        
        assert status['name'] == "MQ-135 Air Quality Sensor"
        assert status['type'] == "air_quality"
        assert status['status'] == SensorStatus.INACTIVE.value
        assert status['active'] is False
    
    def test_status_in_mock_mode(self):
        """Test sensor status in mock mode."""
        sensor = AirQualitySensor({'mock_mode': True})
        sensor.start()
        
        status = sensor.get_status()
        
        assert status['status'] == SensorStatus.MOCK_MODE.value
        assert status['active'] is True
        assert status['mock_mode'] is True
        
        sensor.stop()
    
    def test_status_after_cleanup(self):
        """Test sensor status after cleanup."""
        sensor = AirQualitySensor({'mock_mode': True})
        sensor.start()
        sensor.stop()
        
        status = sensor.get_status()
        
        assert status['status'] == SensorStatus.INACTIVE.value
        assert status['active'] is False


class TestHardwareDetection:
    """Tests for hardware detection."""
    
    def test_hardware_check_mock_backend(self):
        """Test hardware check with mock backend."""
        sensor = AirQualitySensor({'backend': 'mock'})
        
        assert sensor.check_hardware_available() is False
    
    def test_hardware_check_auto_backend(self):
        """Test hardware check with auto backend."""
        sensor = AirQualitySensor({'backend': 'auto'})
        
        # On test systems, should likely return False
        available = sensor.check_hardware_available()
        assert isinstance(available, bool)


class TestAirQualityLevelClass:
    """Tests for AirQualityLevel class."""
    
    def test_level_values(self):
        """Test air quality level constant values."""
        assert AirQualityLevel.EXCELLENT == "excellent"
        assert AirQualityLevel.GOOD == "good"
        assert AirQualityLevel.MODERATE == "moderate"
        assert AirQualityLevel.POOR == "poor"
        assert AirQualityLevel.HAZARDOUS == "hazardous"


class TestSensorCleanup:
    """Tests for sensor cleanup and resource management."""
    
    def test_cleanup_in_mock_mode(self):
        """Test cleanup succeeds in mock mode."""
        sensor = AirQualitySensor({'mock_mode': True})
        sensor.start()
        
        result = sensor.cleanup()
        
        assert result is True
        assert sensor._last_reading is None
        assert sensor._serial_connection is None
        assert sensor._adc is None
    
    def test_multiple_start_stop_cycles(self):
        """Test sensor handles multiple start/stop cycles."""
        sensor = AirQualitySensor({'mock_mode': True})
        
        for _ in range(3):
            assert sensor.start() is True
            assert sensor.is_active()
            data = sensor.read()
            assert 'ppm' in data
            assert sensor.stop() is True
            assert not sensor.is_active()
