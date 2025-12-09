"""
Unit Tests for Microphone Sensor (Phase 4)
-------------------------------------------
Tests for microphone sensor with RMS dB calculation, noise classification,
and mock mode support.
"""

import pytest
import numpy as np
from datetime import datetime
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock sounddevice before importing microphone_sensor to avoid PortAudio dependency
sys.modules['sounddevice'] = MagicMock()
sys.modules['alsaaudio'] = MagicMock()

from backend.sensors.microphone_sensor import (
    MicrophoneSensor,
    get_microphone_reading,
    check_microphone_available,
    list_audio_devices
)
from backend.sensors.base import SensorStatus, SensorError


class TestMicrophoneSensorInitialization:
    """Test microphone sensor initialization."""
    
    def test_basic_init(self):
        """Test basic sensor initialization."""
        sensor = MicrophoneSensor()
        assert sensor.name == "Microphone Sensor"
        assert sensor.sensor_type == "microphone"
        assert sensor.device_index is None
        assert sensor.backend == 'sounddevice'
        assert sensor.sample_rate == 44100
        assert sensor.sample_duration == 1.0
    
    def test_init_with_config(self):
        """Test initialization with custom configuration."""
        config = {
            'device_index': 1,
            'backend': 'alsa',
            'sample_rate': 48000,
            'sample_duration': 0.5,
            'db_reference': -50.0,
            'mock_mode': True,
        }
        sensor = MicrophoneSensor(config=config)
        
        assert sensor.device_index == 1
        assert sensor.backend == 'alsa'
        assert sensor.sample_rate == 48000
        assert sensor.sample_duration == 0.5
        assert sensor.db_reference == -50.0
        assert sensor.mock_mode is True
    
    def test_init_default_parameters(self):
        """Test default parameters initialization."""
        sensor = MicrophoneSensor()
        assert sensor.sample_rate == 44100
        assert sensor.sample_duration == 1.0
        assert sensor.db_reference == -60.0


class TestMicrophoneMockMode:
    """Test microphone mock mode functionality."""
    
    def test_start_in_mock_mode(self):
        """Test starting sensor in mock mode."""
        sensor = MicrophoneSensor(config={'mock_mode': True})
        result = sensor.start()
        
        assert result is True
        assert sensor.status == SensorStatus.MOCK_MODE
        assert sensor.is_active() is True
    
    def test_mock_data_generation(self):
        """Test mock data generation."""
        sensor = MicrophoneSensor(config={'mock_mode': True})
        sensor.start()
        
        data = sensor.read()
        
        assert data is not None
        assert 'timestamp' in data
        assert 'sensor_type' in data
        assert data['sensor_type'] == 'microphone'
        assert 'db_level' in data
        assert 0 <= data['db_level'] <= 100
        assert 'noise_classification' in data
        assert 'rms_amplitude' in data
        assert data['mock_mode'] is True
    
    def test_mock_data_scenarios(self):
        """Test that mock data generates varied scenarios."""
        sensor = MicrophoneSensor(config={'mock_mode': True})
        sensor.start()
        
        # Generate multiple samples to check variety
        samples = [sensor.read()['db_level'] for _ in range(10)]
        
        # Should have some variation
        assert len(set(samples)) > 1  # Not all the same
        assert all(0 <= s <= 100 for s in samples)  # All within valid range
    
    def test_mock_data_structure(self):
        """Test mock data has correct structure."""
        sensor = MicrophoneSensor(config={'mock_mode': True})
        sensor.start()
        
        data = sensor.read()
        
        # Check all required fields
        required_fields = [
            'timestamp', 'sensor_type', 'db_level', 'raw_db',
            'rms_amplitude', 'noise_classification', 'sample_rate', 'sample_duration'
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Check noise classification is valid
        valid_classifications = ["Quiet", "Normal", "Moderate", "Noisy", "Very Noisy"]
        assert data['noise_classification'] in valid_classifications
    
    def test_mock_noise_classifications(self):
        """Test mock data generates all noise classification types."""
        sensor = MicrophoneSensor(config={'mock_mode': True})
        sensor.start()
        
        classifications = set()
        for _ in range(50):  # Generate many samples
            data = sensor.read()
            classifications.add(data['noise_classification'])
        
        # Should generate multiple different classifications
        assert len(classifications) >= 3


@patch('sounddevice.query_devices')
class TestMicrophoneSounddeviceBackend:
    """Test sounddevice backend functionality."""
    
    def test_hardware_check_available(self, mock_query_devices):
        """Test hardware availability check when microphone is available."""
        mock_devices = [
            {'name': 'Microphone', 'max_input_channels': 1, 'default_samplerate': 44100},
            {'name': 'Speaker', 'max_input_channels': 0, 'default_samplerate': 44100},
        ]
        mock_query_devices.return_value = mock_devices
        
        sensor = MicrophoneSensor()
        available = sensor.check_hardware_available()
        
        assert available is True
    
    def test_hardware_check_unavailable(self, mock_query_devices):
        """Test hardware availability check when microphone is unavailable."""
        mock_devices = [
            {'name': 'Speaker', 'max_input_channels': 0, 'default_samplerate': 44100},
        ]
        mock_query_devices.return_value = mock_devices
        
        sensor = MicrophoneSensor()
        available = sensor.check_hardware_available()
        
        assert available is False
    
    def test_hardware_check_exception(self, mock_query_devices):
        """Test hardware check handles exceptions."""
        mock_query_devices.side_effect = Exception("Audio error")
        
        sensor = MicrophoneSensor()
        available = sensor.check_hardware_available()
        
        assert available is False
    
    @patch('sounddevice.rec')
    @patch('sounddevice.wait')
    def test_initialize_sounddevice(self, mock_wait, mock_rec, mock_query_devices):
        """Test sounddevice initialization."""
        # Mock successful device query
        mock_device = {
            'name': 'Microphone',
            'max_input_channels': 1,
            'default_samplerate': 44100
        }
        mock_query_devices.return_value = mock_device
        
        # Mock successful recording
        mock_rec.return_value = np.random.randn(4410, 1).astype(np.float32)
        
        sensor = MicrophoneSensor()
        result = sensor.initialize()
        
        assert result is True


class TestMicrophoneAudioAnalysis:
    """Test audio analysis algorithms."""
    
    def test_db_calculation_silent(self):
        """Test dB calculation for silent audio."""
        sensor = MicrophoneSensor(config={'mock_mode': True})
        sensor.start()
        
        # Create silent audio
        silent_audio = np.zeros(44100, dtype=np.float32)
        rms, raw_db, normalized_db, classification = sensor._analyze_audio(silent_audio)
        
        assert rms < 0.001  # Near zero
        assert normalized_db < 10  # Very quiet
        assert classification == "Quiet"
    
    def test_db_calculation_loud(self):
        """Test dB calculation for loud audio."""
        sensor = MicrophoneSensor(config={'mock_mode': True})
        sensor.start()
        
        # Create loud audio (full scale sine wave)
        t = np.linspace(0, 1, 44100)
        loud_audio = np.sin(2 * np.pi * 440 * t).astype(np.float32)  # 440 Hz at full amplitude
        rms, raw_db, normalized_db, classification = sensor._analyze_audio(loud_audio)
        
        assert rms > 0.5  # Significant amplitude
        assert normalized_db > 80  # Very loud
        assert classification in ["Noisy", "Very Noisy"]
    
    def test_db_calculation_moderate(self):
        """Test dB calculation for moderate audio."""
        sensor = MicrophoneSensor(config={'mock_mode': True})
        sensor.start()
        
        # Create moderate audio (scaled sine wave)
        t = np.linspace(0, 1, 44100)
        moderate_audio = (0.1 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
        rms, raw_db, normalized_db, classification = sensor._analyze_audio(moderate_audio)
        
        assert 0.05 < rms < 0.2  # Moderate amplitude
        assert 40 < normalized_db < 80  # Moderate noise
        assert classification in ["Normal", "Moderate", "Noisy"]
    
    def test_noise_classification_ranges(self):
        """Test noise classification ranges are correct."""
        sensor = MicrophoneSensor(config={'mock_mode': True})
        sensor.start()
        
        # Test boundary values
        test_cases = [
            (20, "Quiet"),
            (40, "Normal"),
            (60, "Moderate"),
            (75, "Noisy"),
            (90, "Very Noisy"),
        ]
        
        for db_level, expected_classification in test_cases:
            # Calculate audio that would give this dB level
            raw_db = -60 + (db_level / 100.0) * 60
            rms = 10 ** (raw_db / 20.0)
            
            # Create audio with this RMS
            audio = np.random.randn(44100).astype(np.float32)
            audio = audio * (rms / np.sqrt(np.mean(audio ** 2)))
            
            _, _, calc_db, classification = sensor._analyze_audio(audio)
            
            # Allow some tolerance due to calculation
            assert abs(calc_db - db_level) < 5
            assert classification == expected_classification


class TestMicrophoneCapture:
    """Test microphone capture functionality."""
    
    @patch('backend.sensors.microphone_sensor.MicrophoneSensor._capture_sounddevice')
    @patch('backend.sensors.microphone_sensor.MicrophoneSensor.check_hardware_available')
    @patch('backend.sensors.microphone_sensor.MicrophoneSensor.initialize')
    def test_capture_real_data(self, mock_init, mock_check, mock_capture_sd):
        """Test capturing real data from microphone."""
        # Mock hardware as available and initialized
        mock_check.return_value = True
        mock_init.return_value = True
        
        # Generate sample audio data
        sample_audio = 0.1 * np.random.randn(44100).astype(np.float32)
        mock_capture_sd.return_value = sample_audio
        
        sensor = MicrophoneSensor()
        sensor.start()
        
        data = sensor.read()
        
        assert data is not None
        assert 'db_level' in data
        assert 0 <= data['db_level'] <= 100
        assert 'noise_classification' in data
        assert data['mock_mode'] is False
    
    @patch('backend.sensors.microphone_sensor.MicrophoneSensor._capture_sounddevice')
    @patch('backend.sensors.microphone_sensor.MicrophoneSensor.check_hardware_available')
    @patch('backend.sensors.microphone_sensor.MicrophoneSensor.initialize')
    def test_capture_error_handling(self, mock_init, mock_check, mock_capture_sd):
        """Test error handling during capture."""
        # Mock hardware as available and initialized
        mock_check.return_value = True
        mock_init.return_value = True
        
        sensor = MicrophoneSensor()
        sensor.start()
        
        # Make capture fail
        mock_capture_sd.return_value = None
        
        with pytest.raises(SensorError):
            sensor.read()


class TestMicrophoneFallbackMechanism:
    """Test automatic fallback to mock mode."""
    
    @patch('sounddevice.query_devices')
    def test_fallback_when_hardware_unavailable(self, mock_query_devices):
        """Test sensor falls back to mock mode when hardware unavailable."""
        mock_query_devices.return_value = []  # No devices
        
        sensor = MicrophoneSensor()
        result = sensor.start()
        
        assert result is True
        assert sensor.status == SensorStatus.MOCK_MODE
        assert sensor.mock_mode is True
    
    @patch('sounddevice.query_devices')
    def test_data_capture_in_fallback_mode(self, mock_query_devices):
        """Test data capture works in fallback mode."""
        mock_query_devices.return_value = []  # No devices
        
        sensor = MicrophoneSensor()
        sensor.start()
        
        data = sensor.read()
        
        assert data is not None
        assert 'db_level' in data
        assert data['mock_mode'] is True


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @patch('backend.sensors.microphone_sensor.MicrophoneSensor')
    def test_get_microphone_reading(self, mock_sensor_class):
        """Test get_microphone_reading convenience function."""
        mock_sensor = MagicMock()
        mock_sensor.read.return_value = {
            'timestamp': datetime.now().isoformat(),
            'db_level': 45.0,
            'noise_classification': 'Normal',
            'mock_mode': True,
        }
        mock_sensor_class.return_value = mock_sensor
        
        result = get_microphone_reading(device_index=0)
        
        assert result is not None
        assert 'db_level' in result
        mock_sensor.start.assert_called_once()
        mock_sensor.stop.assert_called_once()
    
    @patch('backend.sensors.microphone_sensor.MicrophoneSensor')
    def test_check_microphone_available(self, mock_sensor_class):
        """Test check_microphone_available convenience function."""
        mock_sensor = MagicMock()
        mock_sensor.check_hardware_available.return_value = True
        mock_sensor_class.return_value = mock_sensor
        
        result = check_microphone_available(device_index=0)
        
        assert result is True
        mock_sensor.check_hardware_available.assert_called_once()
    
    @patch('sounddevice.query_devices')
    def test_list_audio_devices(self, mock_query_devices):
        """Test list_audio_devices convenience function."""
        mock_devices = [
            {'name': 'Mic 1', 'max_input_channels': 1, 'default_samplerate': 44100},
            {'name': 'Mic 2', 'max_input_channels': 2, 'default_samplerate': 48000},
            {'name': 'Speaker', 'max_input_channels': 0, 'default_samplerate': 44100},
        ]
        mock_query_devices.return_value = mock_devices
        
        result = list_audio_devices()
        
        assert len(result) == 2  # Only input devices
        assert result[0]['name'] == 'Mic 1'
        assert result[1]['name'] == 'Mic 2'


class TestMicrophoneConfiguration:
    """Test microphone configuration options."""
    
    def test_custom_sample_rate(self):
        """Test custom sample rate setting."""
        config = {
            'sample_rate': 48000,
            'mock_mode': True,
        }
        sensor = MicrophoneSensor(config=config)
        sensor.start()
        
        data = sensor.read()
        
        assert data['sample_rate'] == 48000
    
    def test_custom_sample_duration(self):
        """Test custom sample duration setting."""
        config = {
            'sample_duration': 0.5,
            'mock_mode': True,
        }
        sensor = MicrophoneSensor(config=config)
        sensor.start()
        
        data = sensor.read()
        
        assert data['sample_duration'] == 0.5
    
    def test_custom_db_reference(self):
        """Test custom dB reference setting."""
        config = {
            'db_reference': -50.0,
            'mock_mode': True,
        }
        sensor = MicrophoneSensor(config=config)
        
        assert sensor.db_reference == -50.0
    
    def test_backend_selection(self):
        """Test backend selection."""
        config_sounddevice = {'backend': 'sounddevice'}
        config_alsa = {'backend': 'alsa'}
        
        sensor_sd = MicrophoneSensor(config=config_sounddevice)
        sensor_alsa = MicrophoneSensor(config=config_alsa)
        
        assert sensor_sd.backend == 'sounddevice'
        assert sensor_alsa.backend == 'alsa'


class TestMicrophoneSensorStatus:
    """Test sensor status reporting."""
    
    def test_status_after_init(self):
        """Test status after initialization."""
        sensor = MicrophoneSensor()
        status = sensor.get_status()
        
        assert status['name'] == "Microphone Sensor"
        assert status['type'] == 'microphone'
        assert status['status'] == 'inactive'
        assert status['active'] is False
    
    def test_status_in_mock_mode(self):
        """Test status when running in mock mode."""
        sensor = MicrophoneSensor(config={'mock_mode': True})
        sensor.start()
        status = sensor.get_status()
        
        assert status['status'] == 'mock_mode'
        assert status['active'] is True
        assert status['mock_mode'] is True
    
    @patch('sounddevice.query_devices')
    def test_status_after_cleanup(self, mock_query_devices):
        """Test status after cleanup."""
        mock_query_devices.return_value = []  # No devices
        
        sensor = MicrophoneSensor()
        sensor.start()  # Will go to mock mode
        sensor.stop()
        status = sensor.get_status()
        
        assert status['status'] == 'inactive'
        assert status['active'] is False


class TestRMSCalculation:
    """Test RMS amplitude calculation."""
    
    def test_rms_known_signal(self):
        """Test RMS calculation with known signal."""
        sensor = MicrophoneSensor(config={'mock_mode': True})
        sensor.start()
        
        # Create sine wave with known RMS (peak/sqrt(2) for sine wave)
        t = np.linspace(0, 1, 44100)
        amplitude = 0.5
        sine_wave = amplitude * np.sin(2 * np.pi * 440 * t).astype(np.float32)
        
        rms, _, _, _ = sensor._analyze_audio(sine_wave)
        
        # RMS of sine wave should be amplitude / sqrt(2)
        expected_rms = amplitude / np.sqrt(2)
        assert abs(rms - expected_rms) < 0.01  # Small tolerance
    
    def test_rms_zero_signal(self):
        """Test RMS calculation with zero signal."""
        sensor = MicrophoneSensor(config={'mock_mode': True})
        sensor.start()
        
        zero_signal = np.zeros(44100, dtype=np.float32)
        rms, _, _, _ = sensor._analyze_audio(zero_signal)
        
        assert rms < 1e-9  # Essentially zero
