"""
Sound Analysis Module with FFT
------------------------------
Provides frequency analysis, noise classification, and pattern recognition
using Fast Fourier Transform (FFT).
"""

import numpy as np
import sounddevice as sd
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import logging

try:
    from scipy import signal
    from scipy.fft import fft, fftfreq
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning("SciPy not available. Install with: pip install scipy")

from .base import BaseSensor, SensorUnavailableError

logger = logging.getLogger(__name__)


class SoundAnalyzer(BaseSensor):
    """
    Sound analysis sensor with FFT-based frequency analysis.
    
    Provides real-time audio analysis including:
    - FFT frequency spectrum
    - Dominant frequency detection
    - Amplitude analysis (peak, average, RMS)
    - Noise classification
    - Pattern recognition (speech, music, noise)
    """
    
    # Frequency bands for spectral analysis (Hz)
    FREQ_BANDS = {
        "sub_bass": (20, 60),
        "bass": (60, 250),
        "low_mid": (250, 500),
        "mid": (500, 2000),
        "high_mid": (2000, 4000),
        "presence": (4000, 6000),
        "brilliance": (6000, 20000)
    }
    
    # Noise classification thresholds (dB)
    NOISE_LEVELS = [
        (0, 30, "Quiet"),
        (30, 50, "Normal"),
        (50, 70, "Moderate"),
        (70, 85, "Loud"),
        (85, 100, "Very Loud"),
        (100, float('inf'), "Stress Zone")
    ]
    
    def __init__(
        self,
        device_index: Optional[int] = None,
        sample_rate: int = 44100,
        duration: float = 1.0,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize sound analyzer.
        
        Args:
            device_index: Audio device index (None for default)
            sample_rate: Sample rate in Hz (default 44100)
            duration: Duration of each sample in seconds (default 1.0)
            config: Optional configuration dictionary
        """
        super().__init__(
            name="Sound Analyzer",
            sensor_type="sound_analysis",
            config=config or {}
        )
        
        self.device_index = device_index
        self.sample_rate = sample_rate
        self.duration = duration
        self.buffer_size = int(sample_rate * duration)
        
        # Analysis settings
        self.window_function = 'hann'  # Hanning window for FFT
        self.freq_resolution = sample_rate / self.buffer_size
        
        # History for rolling averages
        self.analysis_history: List[Dict[str, Any]] = []
        self.history_size = 10
    
    def initialize(self) -> bool:
        """
        Initialize the sound analyzer and check audio device.
        
        Returns:
            bool: True if initialization successful
        """
        if not SCIPY_AVAILABLE:
            raise SensorUnavailableError(
                "SciPy library not available. Install with: pip install scipy"
            )
        
        try:
            # Test audio device availability
            devices = sd.query_devices()
            
            if self.device_index is not None:
                device = sd.query_devices(self.device_index)
                if device['max_input_channels'] == 0:
                    raise SensorUnavailableError(
                        f"Device {self.device_index} has no input channels"
                    )
            else:
                # Check for any input device
                input_devices = [
                    d for d in devices 
                    if isinstance(d, dict) and d.get('max_input_channels', 0) > 0
                ]
                if not input_devices:
                    raise SensorUnavailableError("No audio input devices found")
            
            # Test recording
            test_recording = sd.rec(
                int(0.1 * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                device=self.device_index,
                dtype='float32'
            )
            sd.wait()
            
            if test_recording is None:
                raise SensorUnavailableError("Failed to record test audio")
            
            logger.info(
                f"Sound analyzer initialized (SR: {self.sample_rate} Hz, "
                f"Duration: {self.duration}s)"
            )
            return True
            
        except SensorUnavailableError:
            raise
        except Exception as e:
            logger.error(f"Error initializing sound analyzer: {e}")
            return False
    
    def capture(self) -> Dict[str, Any]:
        """
        Capture and analyze audio sample.
        
        Returns:
            Dict containing sound analysis results
        """
        if not self.is_active():
            return {
                "timestamp": datetime.now().isoformat(),
                "sensor_type": self.sensor_type,
                "available": False,
                "error": "Sensor not active"
            }
        
        try:
            # Record audio
            recording = sd.rec(
                self.buffer_size,
                samplerate=self.sample_rate,
                channels=1,
                device=self.device_index,
                dtype='float32'
            )
            sd.wait()
            
            if recording is None:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "sensor_type": self.sensor_type,
                    "available": False,
                    "error": "Failed to record audio"
                }
            
            # Flatten to 1D array
            audio_data = recording.flatten()
            
            # Analyze audio
            result = self._analyze_audio(audio_data)
            result["timestamp"] = datetime.now().isoformat()
            result["sensor_type"] = self.sensor_type
            
            # Add to history
            self._update_history(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error during sound capture: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "sensor_type": self.sensor_type,
                "available": False,
                "error": str(e)
            }
    
    def cleanup(self) -> bool:
        """
        Clean up sound analyzer resources.
        
        Returns:
            bool: True if cleanup successful
        """
        try:
            # Clear history
            self.analysis_history.clear()
            
            logger.info("Sound analyzer cleaned up successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during sound analyzer cleanup: {e}")
            return False
    
    def _analyze_audio(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """
        Perform comprehensive audio analysis.
        
        Args:
            audio_data: Audio samples as numpy array
            
        Returns:
            Dict with analysis results
        """
        try:
            # Calculate amplitude metrics
            amplitude_metrics = self._calculate_amplitudes(audio_data)
            
            # Perform FFT analysis
            fft_results = self._perform_fft(audio_data)
            
            # Analyze frequency spectrum
            spectrum_analysis = self._analyze_spectrum(fft_results)
            
            # Classify noise level
            classification = self._classify_noise(amplitude_metrics['avg_db'])
            
            # Detect pattern (speech, music, noise)
            pattern = self._detect_pattern(fft_results, spectrum_analysis)
            
            return {
                "available": True,
                **amplitude_metrics,
                "classification": classification,
                "dominant_frequency": fft_results['dominant_freq'],
                "spectrum": spectrum_analysis,
                "pattern": pattern,
                "sample_rate": self.sample_rate,
                "duration": self.duration
            }
            
        except Exception as e:
            logger.error(f"Error analyzing audio: {e}")
            return {
                "available": False,
                "error": str(e)
            }
    
    def _calculate_amplitudes(self, audio_data: np.ndarray) -> Dict[str, float]:
        """
        Calculate amplitude metrics (RMS, peak, average dB).
        
        Args:
            audio_data: Audio samples
            
        Returns:
            Dict with amplitude metrics
        """
        # Calculate RMS (Root Mean Square)
        rms = np.sqrt(np.mean(audio_data**2))
        
        # Peak amplitude
        peak = np.max(np.abs(audio_data))
        
        # Convert to dB scale
        epsilon = 1e-10
        rms_db = 20 * np.log10(rms + epsilon)
        peak_db = 20 * np.log10(peak + epsilon)
        
        # Normalize to 0-100 range (assuming -60 dB to 0 dB range)
        avg_db = max(0, min(100, (rms_db + 60) * 100 / 60))
        peak_db_norm = max(0, min(100, (peak_db + 60) * 100 / 60))
        
        return {
            "avg_db": round(avg_db, 2),
            "peak_db": round(peak_db_norm, 2),
            "rms": round(float(rms), 6),
            "peak_amplitude": round(float(peak), 6)
        }
    
    def _perform_fft(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """
        Perform Fast Fourier Transform on audio data.
        
        Args:
            audio_data: Audio samples
            
        Returns:
            Dict with FFT results
        """
        # Apply window function to reduce spectral leakage
        window = signal.get_window(self.window_function, len(audio_data))
        windowed_data = audio_data * window
        
        # Perform FFT
        fft_values = fft(windowed_data)
        fft_freqs = fftfreq(len(windowed_data), 1/self.sample_rate)
        
        # Get magnitude spectrum (positive frequencies only)
        n = len(fft_values) // 2
        magnitudes = np.abs(fft_values[:n])
        frequencies = fft_freqs[:n]
        
        # Find dominant frequency
        dominant_idx = np.argmax(magnitudes)
        dominant_freq = float(frequencies[dominant_idx])
        dominant_magnitude = float(magnitudes[dominant_idx])
        
        return {
            "frequencies": frequencies,
            "magnitudes": magnitudes,
            "dominant_freq": round(dominant_freq, 2),
            "dominant_magnitude": round(dominant_magnitude, 2)
        }
    
    def _analyze_spectrum(self, fft_results: Dict[str, Any]) -> Dict[str, float]:
        """
        Analyze frequency spectrum by bands.
        
        Args:
            fft_results: Results from FFT analysis
            
        Returns:
            Dict with energy per frequency band
        """
        frequencies = fft_results['frequencies']
        magnitudes = fft_results['magnitudes']
        
        spectrum = {}
        
        for band_name, (freq_min, freq_max) in self.FREQ_BANDS.items():
            # Find indices for this frequency band
            band_mask = (frequencies >= freq_min) & (frequencies < freq_max)
            band_magnitudes = magnitudes[band_mask]
            
            # Calculate average energy in this band
            if len(band_magnitudes) > 0:
                energy = float(np.mean(band_magnitudes))
            else:
                energy = 0.0
            
            spectrum[band_name] = round(energy, 6)
        
        return spectrum
    
    def _classify_noise(self, db_level: float) -> str:
        """
        Classify noise level based on dB.
        
        Args:
            db_level: Decibel level (0-100 normalized)
            
        Returns:
            Classification string
        """
        for min_db, max_db, classification in self.NOISE_LEVELS:
            if min_db <= db_level < max_db:
                return classification
        
        return "Unknown"
    
    def _detect_pattern(
        self,
        fft_results: Dict[str, Any],
        spectrum: Dict[str, float]
    ) -> str:
        """
        Detect audio pattern (speech, music, noise).
        
        Args:
            fft_results: FFT analysis results
            spectrum: Spectrum analysis by bands
            
        Returns:
            Pattern classification
        """
        dominant_freq = fft_results['dominant_freq']
        
        # Speech typically has strong presence in 250-2000 Hz (vowel formants)
        speech_energy = spectrum['low_mid'] + spectrum['mid']
        
        # Music has more distributed energy across spectrum
        music_energy = (
            spectrum['bass'] + 
            spectrum['mid'] + 
            spectrum['high_mid']
        ) / 3
        
        # Noise has more uniform energy distribution
        total_energy = sum(spectrum.values())
        if total_energy == 0:
            return "silence"
        
        # Calculate energy variance
        energies = list(spectrum.values())
        energy_variance = np.var(energies)
        
        # Classification heuristics
        if total_energy < 0.001:
            return "silence"
        elif 85 <= dominant_freq <= 255 and speech_energy > music_energy:
            return "speech"
        elif energy_variance > 0.0001 and music_energy > speech_energy:
            return "music"
        else:
            return "noise"
    
    def _update_history(self, analysis: Dict[str, Any]) -> None:
        """
        Update analysis history for rolling averages.
        
        Args:
            analysis: Current analysis results
        """
        self.analysis_history.append(analysis)
        
        # Keep only recent history
        if len(self.analysis_history) > self.history_size:
            self.analysis_history.pop(0)
    
    def get_rolling_average(self) -> Dict[str, Any]:
        """
        Get rolling average of recent analyses.
        
        Returns:
            Dict with averaged metrics
        """
        if not self.analysis_history:
            return {
                "samples": 0,
                "avg_db": 0.0,
                "avg_dominant_frequency": 0.0,
                "most_common_pattern": None
            }
        
        # Average dB levels
        db_values = [h['avg_db'] for h in self.analysis_history if h.get('available', False)]
        
        # Average dominant frequencies
        freq_values = [h['dominant_frequency'] for h in self.analysis_history if h.get('available', False)]
        
        # Most common pattern
        patterns = [h['pattern'] for h in self.analysis_history if h.get('available', False) and 'pattern' in h]
        most_common_pattern = max(set(patterns), key=patterns.count) if patterns else None
        
        return {
            "samples": len(self.analysis_history),
            "avg_db": round(np.mean(db_values), 2) if db_values else 0.0,
            "avg_dominant_frequency": round(np.mean(freq_values), 2) if freq_values else 0.0,
            "most_common_pattern": most_common_pattern
        }


# Convenience functions

def analyze_sound(
    device_index: Optional[int] = None,
    duration: float = 1.0
) -> Dict[str, Any]:
    """
    Analyze sound from a single audio sample.
    
    Args:
        device_index: Audio device index
        duration: Duration of sample in seconds
        
    Returns:
        Sound analysis results
    """
    analyzer = SoundAnalyzer(device_index=device_index, duration=duration)
    
    if not analyzer.start():
        return {
            "available": False,
            "error": "Failed to start sound analyzer"
        }
    
    result = analyzer.capture()
    analyzer.stop()
    
    return result


def get_audio_devices() -> List[Dict[str, Any]]:
    """
    Get list of available audio input devices.
    
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
    except Exception as e:
        logger.error(f"Error listing audio devices: {e}")
        return []


def check_scipy_available() -> bool:
    """
    Check if SciPy is available.
    
    Returns:
        True if SciPy can be imported
    """
    return SCIPY_AVAILABLE
