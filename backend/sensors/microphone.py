"""
Microphone Sensor Module
-----------------------
Handles audio capture and sound level analysis.
"""

import sounddevice as sd
import numpy as np
from typing import Optional, Dict, List
import time

class MicrophoneSensor:
    """Microphone sensor for sound level monitoring."""
    
    def __init__(self, device_index: Optional[int] = None, sample_rate: int = 44100):
        """
        Initialize microphone sensor.
        
        Args:
            device_index: Audio device index (None for default)
            sample_rate: Sample rate in Hz (default 44100)
        """
        self.device_index = device_index
        self.sample_rate = sample_rate
        self.duration = 1.0  # Duration of each sample in seconds
    
    def is_available(self) -> bool:
        """
        Check if microphone is available.
        
        Returns:
            True if microphone can be accessed, False otherwise
        """
        try:
            devices = sd.query_devices()
            if self.device_index is not None:
                device = sd.query_devices(self.device_index)
                return device['max_input_channels'] > 0
            else:
                # Check for any input device
                input_devices = [d for d in devices if isinstance(d, dict) and d.get('max_input_channels', 0) > 0]
                return len(input_devices) > 0
        except:
            return False
    
    def get_device_info(self) -> Optional[Dict]:
        """
        Get information about the audio device.
        
        Returns:
            Device info dictionary or None if not available
        """
        try:
            if self.device_index is not None:
                return sd.query_devices(self.device_index)
            else:
                return sd.query_devices(kind='input')
        except:
            return None
    
    def record_sample(self, duration: Optional[float] = None) -> Optional[np.ndarray]:
        """
        Record audio sample.
        
        Args:
            duration: Duration in seconds (uses self.duration if None)
            
        Returns:
            Audio data as numpy array, or None if recording failed
        """
        if duration is None:
            duration = self.duration
        
        try:
            recording = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                device=self.device_index,
                dtype='float32'
            )
            sd.wait()  # Wait for recording to complete
            return recording
        except Exception as e:
            print(f"Error recording audio: {e}")
            return None
    
    def calculate_db_level(self, audio_data: np.ndarray) -> float:
        """
        Calculate decibel level from audio data.
        
        Args:
            audio_data: Audio samples as numpy array
            
        Returns:
            Average dB level
        """
        # Calculate RMS (Root Mean Square)
        rms = np.sqrt(np.mean(audio_data**2))
        
        # Convert to dB (relative to max amplitude of 1.0)
        # Add small epsilon to avoid log(0)
        epsilon = 1e-10
        db = 20 * np.log10(rms + epsilon)
        
        # Normalize to a more intuitive range (0-100)
        # Assuming -60 dB to 0 dB range
        db_normalized = max(0, min(100, (db + 60) * 100 / 60))
        
        return round(db_normalized, 2)
    
    def get_sound_level(self, duration: Optional[float] = None) -> Dict[str, any]:
        """
        Get current sound level measurement.
        
        Args:
            duration: Duration of sample in seconds
            
        Returns:
            Dictionary with sound level data:
            - avg_db: average dB level
            - available: whether measurement was successful
            - error: error message if any
        """
        if not self.is_available():
            return {
                "avg_db": 0.0,
                "available": False,
                "error": "Microphone not available"
            }
        
        audio_data = self.record_sample(duration)
        
        if audio_data is None:
            return {
                "avg_db": 0.0,
                "available": False,
                "error": "Failed to record audio"
            }
        
        try:
            db_level = self.calculate_db_level(audio_data)
            
            # Classify noise level
            if db_level < 30:
                classification = "Quiet"
            elif db_level < 50:
                classification = "Normal"
            elif db_level < 70:
                classification = "Moderate"
            elif db_level < 85:
                classification = "Noisy"
            else:
                classification = "Very Noisy"
            
            return {
                "avg_db": db_level,
                "classification": classification,
                "available": True
            }
        except Exception as e:
            return {
                "avg_db": 0.0,
                "available": False,
                "error": str(e)
            }
    
    def monitor_continuous(self, duration: float = 10.0, interval: float = 1.0) -> List[Dict[str, any]]:
        """
        Monitor sound levels continuously over a period.
        
        Args:
            duration: Total monitoring duration in seconds
            interval: Sampling interval in seconds
            
        Returns:
            List of sound level measurements
        """
        measurements = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            measurement = self.get_sound_level(interval)
            measurement['timestamp'] = time.time()
            measurements.append(measurement)
        
        return measurements
    
    def get_average_level(self, measurements: List[Dict[str, any]]) -> Dict[str, any]:
        """
        Calculate average from multiple measurements.
        
        Args:
            measurements: List of measurement dictionaries
            
        Returns:
            Dictionary with average statistics
        """
        if not measurements:
            return {
                "avg_db": 0.0,
                "min_db": 0.0,
                "max_db": 0.0,
                "samples": 0
            }
        
        db_values = [m.get('avg_db', 0) for m in measurements if m.get('available', False)]
        
        if not db_values:
            return {
                "avg_db": 0.0,
                "min_db": 0.0,
                "max_db": 0.0,
                "samples": 0
            }
        
        return {
            "avg_db": round(np.mean(db_values), 2),
            "min_db": round(min(db_values), 2),
            "max_db": round(max(db_values), 2),
            "samples": len(db_values)
        }


# Convenience functions

def get_sound_reading(device_index: Optional[int] = None, duration: float = 1.0) -> Dict[str, any]:
    """
    Get a single sound level reading.
    
    Args:
        device_index: Audio device index
        duration: Duration of sample
        
    Returns:
        Sound level dictionary
    """
    sensor = MicrophoneSensor(device_index)
    return sensor.get_sound_level(duration)


def check_microphone_available(device_index: Optional[int] = None) -> bool:
    """
    Check if microphone is available.
    
    Args:
        device_index: Audio device index
        
    Returns:
        True if microphone is available
    """
    sensor = MicrophoneSensor(device_index)
    return sensor.is_available()


def list_audio_devices() -> List[Dict]:
    """
    List all available audio devices.
    
    Returns:
        List of device info dictionaries
    """
    try:
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
