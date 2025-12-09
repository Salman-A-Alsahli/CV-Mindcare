"""
Microphone Sensor Implementation (Phase 4)

Implements microphone-based noise analysis with RMS dB calculation and
noise classification. Supports both sounddevice (development) and ALSA 
(Raspberry Pi). Includes automatic mock mode fallback for development 
without hardware.
"""

import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import random

# Import base sensor
from .base import BaseSensor, SensorStatus, SensorUnavailableError

logger = logging.getLogger(__name__)


class MicrophoneSensor(BaseSensor):
    """
    Microphone sensor for noise level monitoring and classification.
    
    Supports two backends:
    - sounddevice - for development and general use
    - ALSA (pyalsaaudio) - for Raspberry Pi (lower overhead)
    
    Features:
    - RMS amplitude dB calculation
    - Noise classification (Quiet, Normal, Moderate, Noisy, Very Noisy)
    - Automatic mock mode if hardware unavailable
    - Configurable sample duration and rate
    - Real-time audio capture and analysis
    
    Configuration options:
        - device_index (int): Audio device index (default: None = default device)
        - backend (str): 'sounddevice' or 'alsa' (default: 'sounddevice')
        - sample_rate (int): Sample rate in Hz (default: 44100)
        - sample_duration (float): Sample duration in seconds (default: 1.0)
        - mock_mode (bool): Force mock mode (default: False)
        - db_reference (float): Reference dB level for normalization (default: -60.0)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize microphone sensor."""
        super().__init__(
            name="Microphone Sensor",
            sensor_type="microphone",
            config=config
        )
        
        # Configuration
        self.device_index = self.config.get('device_index', None)
        self.backend = self.config.get('backend', 'sounddevice')
        self.sample_rate = self.config.get('sample_rate', 44100)
        self.sample_duration = self.config.get('sample_duration', 1.0)
        self.db_reference = self.config.get('db_reference', -60.0)
        
        # Hardware objects
        self.stream = None
        self.alsa_device = None
        
        logger.info(f"MicrophoneSensor initialized (backend={self.backend}, rate={self.sample_rate}Hz)")
    
    def check_hardware_available(self) -> bool:
        """
        Check if microphone hardware is available.
        
        Returns:
            bool: True if microphone can be accessed
        """
        if self.backend == 'alsa':
            try:
                import alsaaudio
                # Try to list capture devices
                devices = alsaaudio.pcms(alsaaudio.PCM_CAPTURE)
                if devices:
                    logger.info(f"ALSA capture devices detected: {len(devices)}")
                    return True
                logger.warning("No ALSA capture devices found")
                return False
            except Exception as e:
                logger.warning(f"ALSA not available: {e}")
                return False
        else:
            # sounddevice backend
            try:
                import sounddevice as sd
                devices = sd.query_devices()
                
                if self.device_index is not None:
                    device = sd.query_devices(self.device_index)
                    available = device.get('max_input_channels', 0) > 0
                else:
                    # Check for any input device
                    input_devices = [d for d in devices if isinstance(d, dict) and d.get('max_input_channels', 0) > 0]
                    available = len(input_devices) > 0
                
                if available:
                    logger.info(f"Sounddevice microphone detected")
                else:
                    logger.warning("No sounddevice input devices found")
                return available
            except Exception as e:
                logger.warning(f"Sounddevice check failed: {e}")
                return False
    
    def initialize(self) -> bool:
        """
        Initialize microphone hardware.
        
        Returns:
            bool: True if initialization successful
        
        Raises:
            SensorUnavailableError: If hardware cannot be initialized
        """
        if self.backend == 'alsa':
            return self._initialize_alsa()
        else:
            return self._initialize_sounddevice()
    
    def _initialize_sounddevice(self) -> bool:
        """Initialize sounddevice backend."""
        try:
            import sounddevice as sd
            
            # Test device availability
            if self.device_index is not None:
                device = sd.query_devices(self.device_index)
                if device.get('max_input_channels', 0) <= 0:
                    raise SensorUnavailableError(f"Device {self.device_index} has no input channels")
            else:
                # Get default input device
                default_device = sd.query_devices(kind='input')
                if default_device.get('max_input_channels', 0) <= 0:
                    raise SensorUnavailableError("Default device has no input channels")
            
            # Test recording
            test_recording = sd.rec(
                int(0.1 * self.sample_rate),  # 100ms test
                samplerate=self.sample_rate,
                channels=1,
                device=self.device_index,
                dtype='float32'
            )
            sd.wait()
            
            if test_recording is None or len(test_recording) == 0:
                raise SensorUnavailableError("Test recording failed")
            
            logger.info(f"Sounddevice microphone initialized")
            return True
            
        except ImportError:
            raise SensorUnavailableError("sounddevice not installed")
        except Exception as e:
            raise SensorUnavailableError(f"Microphone initialization failed: {e}")
    
    def _initialize_alsa(self) -> bool:
        """Initialize ALSA backend (Raspberry Pi)."""
        try:
            import alsaaudio
            
            # Open PCM device for capture
            device_name = 'default' if self.device_index is None else f'hw:{self.device_index}'
            self.alsa_device = alsaaudio.PCM(
                alsaaudio.PCM_CAPTURE,
                alsaaudio.PCM_NORMAL,
                device=device_name
            )
            
            # Set attributes
            self.alsa_device.setchannels(1)
            self.alsa_device.setrate(self.sample_rate)
            self.alsa_device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
            self.alsa_device.setperiodsize(int(self.sample_rate * 0.1))  # 100ms periods
            
            logger.info(f"ALSA microphone initialized (device={device_name})")
            return True
            
        except ImportError:
            raise SensorUnavailableError("alsaaudio (pyalsaaudio) not installed")
        except Exception as e:
            raise SensorUnavailableError(f"ALSA initialization failed: {e}")
    
    def capture(self) -> Dict[str, Any]:
        """
        Capture audio and analyze noise level.
        
        Returns:
            Dict containing:
                - timestamp: ISO 8601 timestamp
                - sensor_type: 'microphone'
                - db_level: RMS dB level (0-100 normalized)
                - raw_db: Raw dB value (negative)
                - rms_amplitude: RMS amplitude value
                - noise_classification: Text classification of noise level
                - sample_rate: Sample rate used
                - sample_duration: Duration of sample
        
        Raises:
            SensorError: If capture or analysis fails
        """
        from .base import SensorError
        
        # Capture audio
        if self.backend == 'alsa':
            audio_data = self._capture_alsa()
        else:
            audio_data = self._capture_sounddevice()
        
        if audio_data is None or len(audio_data) == 0:
            raise SensorError("Failed to capture audio data")
        
        # Analyze audio
        rms, raw_db, normalized_db, classification = self._analyze_audio(audio_data)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "sensor_type": "microphone",
            "db_level": normalized_db,
            "raw_db": round(raw_db, 2),
            "rms_amplitude": round(rms, 6),
            "noise_classification": classification,
            "sample_rate": self.sample_rate,
            "sample_duration": self.sample_duration,
        }
    
    def _capture_sounddevice(self) -> Optional[np.ndarray]:
        """Capture audio using sounddevice."""
        try:
            import sounddevice as sd
            
            recording = sd.rec(
                int(self.sample_duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                device=self.device_index,
                dtype='float32'
            )
            sd.wait()
            
            return recording.flatten()
            
        except Exception as e:
            logger.error(f"Sounddevice capture failed: {e}")
            return None
    
    def _capture_alsa(self) -> Optional[np.ndarray]:
        """Capture audio using ALSA."""
        if self.alsa_device is None:
            logger.error("ALSA device not initialized")
            return None
        
        try:
            # Calculate number of samples needed
            total_samples = int(self.sample_duration * self.sample_rate)
            audio_data = []
            
            # Read data in chunks with timeout protection
            max_iterations = int(total_samples / 4410) + 100  # Allow ~100ms periods + margin
            iteration = 0
            
            while len(audio_data) < total_samples and iteration < max_iterations:
                length, data = self.alsa_device.read()
                if length > 0:
                    # Convert bytes to numpy array (16-bit PCM)
                    samples = np.frombuffer(data, dtype=np.int16)
                    audio_data.extend(samples)
                iteration += 1
            
            if len(audio_data) < total_samples:
                logger.warning(f"ALSA capture incomplete: {len(audio_data)}/{total_samples} samples")
            
            # Convert to float32 and normalize to [-1, 1]
            audio_array = np.array(audio_data[:total_samples], dtype=np.float32) / 32768.0
            return audio_array
            
        except Exception as e:
            logger.error(f"ALSA capture failed: {e}")
            return None
    
    def _analyze_audio(self, audio_data: np.ndarray) -> tuple:
        """
        Analyze audio data to calculate dB level and classification.
        
        Algorithm:
        1. Calculate RMS (Root Mean Square) amplitude
        2. Convert to dB: dB = 20 * log10(RMS)
        3. Normalize to 0-100 range based on reference dB
        4. Classify into noise categories
        
        Args:
            audio_data: Audio samples as numpy array
            
        Returns:
            tuple: (rms, raw_db, normalized_db, classification)
        """
        try:
            # Calculate RMS amplitude
            rms = np.sqrt(np.mean(audio_data ** 2))
            
            # Convert to dB (add epsilon to avoid log(0))
            epsilon = 1e-10
            raw_db = 20 * np.log10(rms + epsilon)
            
            # Normalize to 0-100 range
            # Assuming typical range from db_reference (default -60) to 0 dB
            normalized_db = max(0, min(100, (raw_db - self.db_reference) * 100 / abs(self.db_reference)))
            
            # Classify noise level
            if normalized_db < 30:
                classification = "Quiet"
            elif normalized_db < 50:
                classification = "Normal"
            elif normalized_db < 70:
                classification = "Moderate"
            elif normalized_db < 85:
                classification = "Noisy"
            else:
                classification = "Very Noisy"
            
            logger.debug(f"Audio analysis: RMS={rms:.6f}, raw_dB={raw_db:.2f}, norm_dB={normalized_db:.2f}, class={classification}")
            return (rms, raw_db, normalized_db, classification)
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return (0.0, self.db_reference, 0.0, "Unknown")
    
    def capture_mock_data(self) -> Dict[str, Any]:
        """
        Generate realistic mock microphone data.
        
        Simulates various noise scenarios common in work environments.
        
        Returns:
            Dict with same structure as capture()
        """
        # Generate realistic dB levels based on common scenarios
        scenarios = [
            (0, 20, "Silent room/library", "Quiet"),
            (20, 35, "Quiet office/bedroom", "Quiet"),
            (35, 50, "Normal conversation/office", "Normal"),
            (50, 65, "Busy office/traffic", "Moderate"),
            (65, 80, "Noisy street/restaurant", "Noisy"),
            (80, 95, "Very noisy traffic/construction", "Very Noisy"),
        ]
        
        # Weighted random selection (favor normal office scenarios)
        weights = [0.10, 0.25, 0.35, 0.20, 0.08, 0.02]
        scenario = random.choices(scenarios, weights=weights)[0]
        
        normalized_db = random.uniform(scenario[0], scenario[1])
        
        # Calculate corresponding raw dB and RMS
        raw_db = self.db_reference + (normalized_db / 100.0) * abs(self.db_reference)
        rms = 10 ** (raw_db / 20.0)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "sensor_type": "microphone",
            "db_level": round(normalized_db, 2),
            "raw_db": round(raw_db, 2),
            "rms_amplitude": round(rms, 6),
            "noise_classification": scenario[3],
            "sample_rate": self.sample_rate,
            "sample_duration": self.sample_duration,
            "mock_scenario": scenario[2],
        }
    
    def cleanup(self) -> bool:
        """
        Clean up microphone resources.
        
        Returns:
            bool: True if cleanup successful
        """
        try:
            if self.alsa_device is not None:
                try:
                    self.alsa_device.close()
                except (OSError, AttributeError) as e:
                    logger.warning(f"Error closing ALSA device: {e}")
                self.alsa_device = None
                logger.info("ALSA device closed")
            
            self.stream = None
            return True
            
        except Exception as e:
            logger.error(f"Microphone cleanup error: {e}")
            return False


# Convenience functions for backward compatibility

def get_microphone_reading(device_index: Optional[int] = None, backend: str = 'sounddevice', duration: float = 1.0) -> Dict[str, Any]:
    """
    Get a single microphone reading with noise analysis.
    
    Args:
        device_index: Audio device index
        backend: 'sounddevice' or 'alsa'
        duration: Sample duration in seconds
        
    Returns:
        Microphone reading dictionary
    """
    sensor = MicrophoneSensor(config={
        'device_index': device_index,
        'backend': backend,
        'sample_duration': duration
    })
    sensor.start()
    
    try:
        data = sensor.read()
        sensor.stop()
        return data
    except Exception as e:
        sensor.stop()
        return {
            "timestamp": datetime.now().isoformat(),
            "sensor_type": "microphone",
            "db_level": 0.0,
            "noise_classification": "Unknown",
            "error": str(e),
            "mock_mode": True,
        }


def check_microphone_available(device_index: Optional[int] = None, backend: str = 'sounddevice') -> bool:
    """
    Check if microphone is available.
    
    Args:
        device_index: Audio device index
        backend: 'sounddevice' or 'alsa'
        
    Returns:
        True if microphone is available
    """
    sensor = MicrophoneSensor(config={'device_index': device_index, 'backend': backend})
    return sensor.check_hardware_available()


def list_audio_devices() -> list:
    """
    List available audio input devices.
    
    Returns:
        List of device dictionaries
    """
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        return [
            {
                'index': i,
                'name': d['name'],
                'channels': d['max_input_channels'],
                'sample_rate': d['default_samplerate']
            }
            for i, d in enumerate(devices)
            if isinstance(d, dict) and d.get('max_input_channels', 0) > 0
        ]
    except:
        return []
