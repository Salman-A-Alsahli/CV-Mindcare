"""
MQ-135 Air Quality Sensor Module (Phase 1: MQ-135 Integration).

This module provides air quality monitoring using the MQ-135 gas sensor,
which detects various gases including CO2, NH3, benzene, smoke, and other
air pollutants. The sensor outputs analog values that are converted to
air quality classifications.

Key Features:
- MQ-135 sensor integration via I2C (ADS1115), SPI (MCP3008), or serial adapter
- PPM (parts per million) calibration and conversion
- Air quality level classification (Excellent to Hazardous)
- Mock mode for testing without hardware
- Automatic hardware detection and fallback
- Data logging and trend analysis

Air Quality Levels:
- Excellent: 0-50 PPM (Fresh air)
- Good: 51-100 PPM (Acceptable air quality)
- Moderate: 101-150 PPM (Sensitive groups may be affected)
- Poor: 151-200 PPM (Health effects for everyone)
- Hazardous: 200+ PPM (Serious health effects)

Hardware Requirements:
- MQ-135 analog gas sensor
- Analog-to-digital converter (ADC) for Raspberry Pi:
  - ADS1115 (16-bit I2C ADC) - RECOMMENDED for best accuracy
  - MCP3008 (10-bit SPI ADC) - Alternative option
  - Serial communication adapter - USB option

Usage:
    # Basic usage with mock mode
    sensor = AirQualitySensor(config={'mock_mode': True})
    sensor.start()
    data = sensor.read()
    print(f"Air Quality: {data['air_quality_level']}, PPM: {data['ppm']}")
    sensor.stop()

    # Real hardware usage with ADS1115 (I2C)
    sensor = AirQualitySensor(config={
        'backend': 'i2c',
        'i2c': {'channel': 0},
        'calibration_factor': 1.0
    })
    sensor.start()
    data = sensor.read()

Optimized for Raspberry Pi 5 deployment with graceful hardware detection.
"""

from datetime import datetime
from typing import Dict, Any, Optional
import logging
import random

from .base import BaseSensor, SensorError

logger = logging.getLogger(__name__)


class AirQualityLevel:
    """Air quality level classifications based on PPM readings."""

    EXCELLENT = "excellent"  # 0-50 PPM
    GOOD = "good"  # 51-100 PPM
    MODERATE = "moderate"  # 101-150 PPM
    POOR = "poor"  # 151-200 PPM
    HAZARDOUS = "hazardous"  # 200+ PPM


class AirQualitySensor(BaseSensor):
    """
    MQ-135 Air Quality Sensor implementation.

    Monitors air quality using MQ-135 gas sensor with automatic
    PPM conversion and air quality classification.

    Supports multiple ADC backends:
    - I2C (ADS1115) - RECOMMENDED: 16-bit resolution, easy wiring
    - SPI (MCP3008) - 10-bit resolution, more GPIO pins needed
    - Serial - USB adapter option

    Attributes:
        serial_port: Serial port for sensor communication (e.g., '/dev/ttyUSB0')
        calibration_factor: Calibration multiplier for PPM conversion (default: 1.0)
        sample_count: Number of samples to average (default: 10)
        backend: Communication backend ('i2c', 'spi', 'serial', 'auto')
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize MQ-135 air quality sensor.

        Args:
            config: Configuration dictionary with options:
                - mock_mode (bool): Enable mock/simulation mode
                - backend (str): 'i2c', 'ads1115', 'spi', 'gpio', 'serial', 'auto'
                - serial_port (str): Serial port path (e.g., '/dev/ttyUSB0')
                - i2c (dict): I2C config with 'channel' (0-3) and 'address' (default 0x48)
                - gpio_pin (int): GPIO pin/channel number for ADC connection
                - calibration_factor (float): Calibration multiplier (default: 1.0)
                - sample_count (int): Number of samples to average (default: 10)
        """
        super().__init__("MQ-135 Air Quality Sensor", "air_quality", config)

        # Configuration
        self.serial_port = self.config.get("serial_port", "/dev/ttyUSB0")
        self.gpio_pin = self.config.get("gpio_pin", None)
        self.calibration_factor = self.config.get("calibration_factor", 1.0)
        self.sample_count = self.config.get("sample_count", 10)
        self.backend = self.config.get("backend", "auto")

        # Runtime state
        self._serial_connection = None
        self._adc = None
        self._analog_input = None  # For ADS1115 I2C ADC
        self._adc_channel = 0  # ADC channel number
        self._last_reading: Optional[float] = None

        logger.info(
            f"AirQualitySensor initialized (backend={self.backend}, "
            f"calibration={self.calibration_factor}, samples={self.sample_count})"
        )

    def check_hardware_available(self) -> bool:
        """
        Check if MQ-135 sensor hardware is available.

        Attempts to detect sensor via serial port, GPIO/ADC, or I2C (ADS1115).

        Returns:
            bool: True if hardware detected, False otherwise
        """
        if self.backend == "mock":
            return False

        # Check serial backend
        if self.backend in ("serial", "auto"):
            try:
                import os

                if os.path.exists(self.serial_port):
                    logger.info(f"Serial port {self.serial_port} detected")
                    return True
            except Exception as e:
                logger.debug(f"Serial check failed: {e}")

        # Check I2C backend (ADS1115 ADC)
        if self.backend in ("i2c", "ads1115", "auto"):
            try:
                import board
                import busio

                # Try to initialize I2C bus
                i2c = busio.I2C(board.SCL, board.SDA)
                i2c.deinit()
                logger.info("I2C hardware detected (ADS1115 ADC available)")
                return True
            except (ImportError, RuntimeError, ValueError) as e:
                logger.debug(f"I2C/ADS1115 check failed: {e}")

        # Check GPIO backend (MCP3008 via SPI)
        if self.backend in ("gpio", "spi", "auto"):
            try:
                import spidev

                # Try to open SPI device
                spi = spidev.SpiDev()
                spi.open(0, 0)
                spi.close()
                logger.info("SPI hardware detected (MCP3008 ADC available)")
                return True
            except (ImportError, FileNotFoundError, OSError) as e:
                logger.debug(f"SPI/GPIO check failed: {e}")

        logger.warning("No MQ-135 sensor hardware detected")
        return False

    def initialize(self) -> bool:
        """
        Initialize MQ-135 sensor hardware.

        Sets up serial connection, I2C (ADS1115), or GPIO/ADC (MCP3008) interface
        based on detected hardware and configuration.

        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Determine backend if auto-detection
            if self.backend == "auto":
                # Try backends in order of preference: I2C, Serial, SPI
                if self._initialize_ads1115():
                    self.backend = "i2c"
                    return True
                elif self._initialize_serial():
                    self.backend = "serial"
                    return True
                elif self._initialize_gpio():
                    self.backend = "spi"
                    return True
                else:
                    logger.error("Failed to initialize any backend")
                    return False

            # Initialize specific backend
            if self.backend == "serial":
                return self._initialize_serial()
            elif self.backend in ("gpio", "spi"):
                return self._initialize_gpio()
            elif self.backend in ("i2c", "ads1115"):
                return self._initialize_ads1115()
            else:
                logger.error(f"Unknown backend: {self.backend}")
                return False

        except Exception as e:
            logger.error(f"Initialization error: {e}", exc_info=True)
            self.error_message = str(e)
            return False

    def _initialize_serial(self) -> bool:
        """
        Initialize serial communication with MQ-135 sensor.

        Returns:
            bool: True if serial connection established
        """
        try:
            import serial
            import os

            if not os.path.exists(self.serial_port):
                logger.debug(f"Serial port {self.serial_port} not found")
                return False

            self._serial_connection = serial.Serial(self.serial_port, baudrate=9600, timeout=1)

            # Flush any old data
            self._serial_connection.reset_input_buffer()

            logger.info(f"Serial connection established on {self.serial_port}")
            return True

        except ImportError:
            logger.debug("pyserial not installed")
            return False
        except Exception as e:
            logger.debug(f"Serial initialization failed: {e}")
            return False

    def _initialize_gpio(self) -> bool:
        """
        Initialize GPIO/ADC interface for MQ-135 sensor (MCP3008 via SPI).

        Returns:
            bool: True if GPIO/ADC initialized
        """
        try:
            # Try MCP3008 ADC (common for Raspberry Pi)
            import spidev

            self._adc = spidev.SpiDev()
            self._adc.open(0, 0)  # SPI bus 0, device 0
            self._adc.max_speed_hz = 1350000

            logger.info("GPIO/SPI ADC initialized (MCP3008)")
            return True

        except ImportError:
            logger.debug("spidev not installed (ADC unavailable)")
            return False
        except Exception as e:
            logger.debug(f"GPIO/ADC initialization failed: {e}")
            return False

    def _initialize_ads1115(self) -> bool:
        """
        Initialize ADS1115 I2C ADC for MQ-135 sensor.

        ADS1115 is a 16-bit I2C ADC commonly used with Raspberry Pi
        for analog sensors like the MQ-135.

        Returns:
            bool: True if ADS1115 initialized successfully
        """
        try:
            import board
            import busio
            import adafruit_ads1x15.ads1115 as ADS
            from adafruit_ads1x15.analog_in import AnalogIn

            # Create I2C bus
            i2c = busio.I2C(board.SCL, board.SDA)

            # Get I2C configuration
            i2c_config = self.config.get("i2c", {})
            i2c_address = i2c_config.get("address", 0x48)  # Default ADS1115 address
            self._adc_channel = i2c_config.get("channel", 0)

            # Create ADS1115 object with specified address
            self._adc = ADS.ADS1115(i2c, address=i2c_address)

            # Map channel number to ADS1115 pin constant
            channel_map = {0: ADS.P0, 1: ADS.P1, 2: ADS.P2, 3: ADS.P3}
            
            if self._adc_channel not in channel_map:
                raise ValueError(f"Invalid I2C channel: {self._adc_channel}. Must be 0-3.")
            
            # Create analog input on specified channel
            self._analog_input = AnalogIn(self._adc, channel_map[self._adc_channel])

            # Test read to verify connection
            test_value = self._analog_input.value
            logger.info(
                f"ADS1115 I2C ADC initialized (channel={self._adc_channel}, test_value={test_value})"
            )
            return True

        except ImportError as e:
            logger.debug(f"ADS1115 libraries not installed: {e}")
            return False
        except Exception as e:
            logger.debug(f"ADS1115 initialization failed: {e}")
            return False

    def capture(self) -> Dict[str, Any]:
        """
        Capture air quality data from MQ-135 sensor.

        Reads raw analog value, converts to PPM, and classifies air quality.
        Takes multiple samples and averages for stability.

        Returns:
            Dict containing:
                - timestamp: ISO 8601 timestamp
                - sensor_type: 'air_quality'
                - raw_value: Raw analog reading (0-1023 or voltage)
                - ppm: Parts per million concentration
                - air_quality_level: Classification (excellent, good, etc.)
                - calibration_factor: Current calibration factor
                - sample_count: Number of samples averaged

        Raises:
            SensorError: If capture fails
        """
        if not self.is_active():
            raise SensorError("Sensor not active")

        try:
            # Read raw values
            raw_values = []
            for _ in range(self.sample_count):
                if self.backend == "serial":
                    raw_value = self._read_serial()
                elif self.backend in ("gpio", "spi"):
                    raw_value = self._read_gpio()
                elif self.backend in ("i2c", "ads1115"):
                    raw_value = self._read_i2c()
                else:
                    raise SensorError(f"Unknown backend: {self.backend}")

                raw_values.append(raw_value)

            # Average readings for stability
            avg_raw = sum(raw_values) / len(raw_values)

            # Convert to PPM using calibration
            ppm = self._convert_to_ppm(avg_raw)

            # Classify air quality
            air_quality_level = self._classify_air_quality(ppm)

            # Store last reading
            self._last_reading = ppm

            return {
                "timestamp": datetime.now().isoformat(),
                "sensor_type": "air_quality",
                "raw_value": avg_raw,
                "ppm": round(ppm, 2),
                "air_quality_level": air_quality_level,
                "calibration_factor": self.calibration_factor,
                "sample_count": len(raw_values),
                "backend": self.backend,
            }

        except Exception as e:
            logger.error(f"Capture error: {e}", exc_info=True)
            raise SensorError(f"Failed to capture air quality data: {e}")

    def _read_serial(self) -> float:
        """
        Read raw value from serial connection.

        Returns:
            float: Raw sensor value (0-1023)
        """
        if not self._serial_connection:
            raise SensorError("Serial connection not initialized")

        try:
            # Read line from serial (assumes sensor sends numeric values)
            line = self._serial_connection.readline().decode("utf-8").strip()
            raw_value = float(line)
            return raw_value
        except Exception as e:
            raise SensorError(f"Serial read error: {e}")

    def _read_gpio(self) -> float:
        """
        Read raw value from GPIO/ADC.

        Returns:
            float: Raw sensor value (0-1023)
        """
        if not self._adc:
            raise SensorError("ADC not initialized")

        try:
            # Read from ADC channel (assuming MCP3008)
            channel = self.gpio_pin or 0
            adc_value = self._read_adc_channel(channel)
            return adc_value
        except Exception as e:
            raise SensorError(f"GPIO/ADC read error: {e}")

    def _read_adc_channel(self, channel: int) -> float:
        """
        Read value from specific ADC channel.

        Args:
            channel: ADC channel number (0-7 for MCP3008)

        Returns:
            float: ADC reading (0-1023)
        """
        if channel < 0 or channel > 7:
            raise ValueError(f"Invalid channel: {channel}")

        # MCP3008 SPI protocol
        adc = self._adc.xfer2([1, (8 + channel) << 4, 0])
        data = ((adc[1] & 3) << 8) + adc[2]
        return float(data)

    def _read_i2c(self) -> float:
        """
        Read raw value from I2C ADC (ADS1115).

        Reads from ADS1115 16-bit ADC and normalizes to 0-1023 range
        for compatibility with 10-bit ADCs (MCP3008, etc).

        Returns:
            float: Normalized sensor value (0-1023 range, scaled from 16-bit ADC)
        """
        if not self._analog_input:
            raise SensorError("I2C ADC (ADS1115) not initialized")

        try:
            # Read from ADS1115
            # The Adafruit AnalogIn.value property returns a SIGNED 16-bit integer
            # Range: -32768 to +32767 (differential mode)
            # For single-ended reads (MQ-135): typically 0 to +32767 (positive only)
            # Negative values can occur in differential mode or with electrical noise
            # We normalize to 0-1023 range for compatibility with 10-bit ADCs
            adc_value = self._analog_input.value
            
            # Clamp negative values to 0 (shouldn't happen with single-ended reads)
            if adc_value < 0:
                logger.warning(f"ADS1115 returned negative value: {adc_value}, clamping to 0")
                adc_value = 0
            
            # Normalize signed 16-bit value to 10-bit range (0-1023)
            # ADS1115 signed range: -32768 to +32767
            # For positive values (sensor readings): 0 to 32767
            # Normalization formula: (value / 32767) * 1023
            normalized_value = (adc_value / 32767.0) * 1023.0
            
            return float(normalized_value)
        except Exception as e:
            raise SensorError(f"I2C/ADS1115 read error: {e}")

    def _convert_to_ppm(self, raw_value: float) -> float:
        """
        Convert raw sensor value to PPM concentration.

        Uses calibration factor and sensor characteristics curve.

        IMPORTANT: This is a simplified linear conversion suitable for
        initial testing and development. For production deployment with
        real MQ-135 hardware, implement proper logarithmic curve fitting
        based on the MQ-135 datasheet specifications:

        Production formula should be:
        Rs = ((Vc * RL) / Vout) - RL  # Sensor resistance
        PPM = a * (Rs/R0)^b  # Where a,b are gas-specific constants

        Gas-specific constants (from MQ-135 datasheet):
        - CO2: a=116.6020682, b=-2.769034857
        - NH3: a=102.2, b=-2.473
        - Benzene: a=34.668, b=-3.369

        See: https://github.com/GeorgK/MQ135 for reference implementation

        Args:
            raw_value: Raw analog reading (0-1023 for 10-bit ADC)

        Returns:
            float: PPM concentration (approximate)
        """
        # Simplified PPM conversion (assumes 0-1023 ADC range)
        # Linear approximation for development/testing only
        max_adc = 1023.0
        max_ppm = 300.0  # Maximum PPM we'll measure

        # Linear approximation - replace with logarithmic curve for production
        ppm = self.calibration_factor * (raw_value / max_adc) * max_ppm

        return max(0.0, ppm)  # Ensure non-negative

    def _classify_air_quality(self, ppm: float) -> str:
        """
        Classify air quality based on PPM concentration.

        Args:
            ppm: Parts per million concentration

        Returns:
            str: Air quality level classification
        """
        if ppm <= 50:
            return AirQualityLevel.EXCELLENT
        elif ppm <= 100:
            return AirQualityLevel.GOOD
        elif ppm <= 150:
            return AirQualityLevel.MODERATE
        elif ppm <= 200:
            return AirQualityLevel.POOR
        else:
            return AirQualityLevel.HAZARDOUS

    def capture_mock_data(self) -> Dict[str, Any]:
        """
        Generate mock air quality data for testing.

        Simulates realistic MQ-135 sensor readings with variation
        and different air quality scenarios.

        Returns:
            Dict containing mock sensor data in same format as capture()
        """
        # Generate realistic mock PPM value
        # Vary between different air quality levels
        scenarios = [
            (30, 20),  # Excellent air (30 ± 20 PPM)
            (75, 15),  # Good air (75 ± 15 PPM)
            (125, 15),  # Moderate air (125 ± 15 PPM)
            (175, 15),  # Poor air (175 ± 15 PPM)
            (250, 30),  # Hazardous air (250 ± 30 PPM)
        ]

        # Pick random scenario
        base_ppm, variation = random.choice(scenarios)
        ppm = base_ppm + random.uniform(-variation, variation)
        ppm = max(0.0, ppm)  # Ensure non-negative

        # Convert back to raw value for consistency
        max_ppm = 300.0
        raw_value = (ppm / max_ppm) * 1023.0

        # Classify
        air_quality_level = self._classify_air_quality(ppm)

        # Store last reading
        self._last_reading = ppm

        return {
            "timestamp": datetime.now().isoformat(),
            "sensor_type": "air_quality",
            "raw_value": round(raw_value, 2),
            "ppm": round(ppm, 2),
            "air_quality_level": air_quality_level,
            "calibration_factor": self.calibration_factor,
            "sample_count": self.sample_count,
            "backend": "mock",
            "mock_mode": True,
        }

    def cleanup(self) -> bool:
        """
        Clean up sensor resources.

        Closes serial connection, I2C, or GPIO/ADC interface.

        Returns:
            bool: True if cleanup successful
        """
        try:
            if self._serial_connection:
                self._serial_connection.close()
                self._serial_connection = None
                logger.info("Serial connection closed")

            if self._adc:
                # Close ADC if it has a close method
                if hasattr(self._adc, 'close'):
                    self._adc.close()
                self._adc = None
                logger.info("ADC connection closed")

            if self._analog_input:
                self._analog_input = None
                logger.info("I2C analog input released")

            self._last_reading = None
            return True

        except Exception as e:
            logger.error(f"Cleanup error: {e}", exc_info=True)
            return False

    def get_last_reading(self) -> Optional[float]:
        """
        Get the last PPM reading.

        Returns:
            float: Last PPM reading, or None if no readings yet
        """
        return self._last_reading

    def calibrate(self, known_ppm: float, measured_raw: float) -> float:
        """
        Calibrate sensor against known PPM concentration.

        Use this method to calibrate the sensor by exposing it to a
        known concentration and recording the raw sensor value.

        Args:
            known_ppm: Known PPM concentration
            measured_raw: Raw sensor value at that concentration

        Returns:
            float: New calibration factor
        """
        if measured_raw <= 0:
            raise ValueError("Measured raw value must be positive")

        # Calculate expected PPM with current calibration
        expected_ppm = self._convert_to_ppm(measured_raw)

        # Adjust calibration factor
        if expected_ppm > 0:
            new_factor = self.calibration_factor * (known_ppm / expected_ppm)
            self.calibration_factor = new_factor
            logger.info(
                f"Calibration updated: {new_factor:.4f} "
                f"(known={known_ppm}, measured_raw={measured_raw})"
            )
            return new_factor
        else:
            raise ValueError("Cannot calibrate with zero expected PPM")


# Convenience functions for quick access


def get_air_quality_reading(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Quick function to get a single air quality reading.

    Creates sensor, starts it, reads once, and cleans up.
    Automatically uses mock mode if hardware unavailable.

    Args:
        config: Optional sensor configuration

    Returns:
        Dict containing air quality data

    Example:
        data = get_air_quality_reading()
        print(f"Air Quality: {data['air_quality_level']}")
    """
    sensor = AirQualitySensor(config)
    sensor.start()
    try:
        return sensor.read()
    finally:
        sensor.stop()


def check_air_quality_available() -> bool:
    """
    Check if MQ-135 air quality sensor hardware is available.

    Returns:
        bool: True if hardware detected, False otherwise

    Example:
        if check_air_quality_available():
            print("MQ-135 sensor detected")
        else:
            print("Running in mock mode")
    """
    sensor = AirQualitySensor()
    return sensor.check_hardware_available()
