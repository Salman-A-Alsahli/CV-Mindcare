# Hardware Setup Guide

Configure camera, microphone, and MQ-135 air quality sensor for CV-Mindcare.

## Overview

CV-Mindcare supports three environmental sensors:
1. **Camera** - Greenery detection
2. **Microphone** - Noise level monitoring  
3. **MQ-135** - Air quality (CO₂, NH₃, benzene, smoke)

**Note**: All sensors work in mock mode without hardware for testing!

## Camera Sensor

### Supported Cameras
- USB webcams
- Laptop built-in cameras
- Raspberry Pi Camera Module v2/v3
- Any V4L2-compatible camera (Linux)

### Setup

**Linux**:
```bash
# List available cameras
ls /dev/video*

# Test camera
python -c "from backend.sensors.camera_sensor import check_camera_available; print(check_camera_available())"

# Configure in config/sensors.yaml
camera:
  backend: auto  # or 'opencv', 'picamera'
  device_index: 0
```

**macOS/Windows**:
```bash
# Cameras are auto-detected
# Configure device index if multiple cameras
```

**Raspberry Pi**:
```bash
# Enable camera
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable

# Install picamera2 (for native Raspberry Pi camera support)
pip install picamera2

# Configure in config/sensors.yaml
camera:
  backend: auto  # Recommended: auto-detects picamera2 or opencv
  device_index: 0
```

**Backend Auto-Detection**: 
When `backend: auto` is configured, the camera sensor will:
1. First try to use `picamera2` (native Raspberry Pi camera - 10x faster)
2. Fall back to `opencv` (USB cameras, webcams) if picamera2 unavailable
3. Enter mock mode if no camera hardware is detected

This allows the same configuration to work on both Raspberry Pi (with native camera) and other systems (with USB cameras).

### Troubleshooting
- **Camera not detected**: Check USB connection or drivers
- **Permission denied**: Add user to video group (Linux)
  ```bash
  sudo usermod -a -G video $USER
  ```
- **Raspberry Pi camera not working**: 
  - Ensure camera cable is properly connected to CSI port
  - Enable camera interface with `sudo raspi-config`
  - Check camera detection: `libcamera-hello` (for newer Raspberry Pi OS)
  - Verify picamera2 is installed: `pip show picamera2`

## Microphone Sensor

### Supported Microphones
- USB microphones
- Built-in laptop microphones
- Audio interfaces
- Any ALSA/CoreAudio/WASAPI device

### Setup

**Linux**:
```bash
# Install dependencies
sudo apt install portaudio19-dev python3-pyaudio

# List audio devices
python -c "from backend.sensors.microphone_sensor import list_audio_devices; list_audio_devices()"

# Configure in config/sensors.yaml
microphone:
  backend: sounddevice
  device: null  # null = default device
  sample_rate: 44100
```

**macOS**:
```bash
# Install portaudio
brew install portaudio

# List devices
python -c "from backend.sensors.microphone_sensor import list_audio_devices; list_audio_devices()"
```

**Windows**:
```bash
# Microphones auto-detected
# Use Device Manager to check microphone status
```

### Troubleshooting
- **No audio input**: Check microphone permissions in OS settings
- **PortAudio error**: Reinstall sounddevice
  ```bash
  pip install sounddevice --force-reinstall
  ```

## MQ-135 Air Quality Sensor

### Hardware Requirements
- MQ-135 analog gas sensor module
- Analog-to-digital converter (ADC):
  - **USB Serial Adapter** (easiest): Any USB-to-serial that outputs sensor readings
  - **MCP3008 SPI ADC** (Raspberry Pi): 8-channel 10-bit ADC
  - **ADS1115 I2C ADC** (alternative): 4-channel 16-bit ADC

### Quick Setup (Serial Connection)

1. **Connect MQ-135 to USB Serial Adapter**
2. **Identify Serial Port**:
   ```bash
   # Linux/Mac
   ls /dev/ttyUSB*  # or /dev/ttyACM*
   
   # Windows
   # Check Device Manager > Ports (COM & LPT)
   ```

3. **Configure**:
   ```yaml
   # config/sensors.yaml
   air_quality:
     backend: serial
     serial:
       port: /dev/ttyUSB0  # or COM3 on Windows
       baudrate: 9600
   ```

4. **Test**:
   ```bash
   python -c "from backend.sensors.air_quality import get_air_quality_reading; print(get_air_quality_reading())"
   ```

### Raspberry Pi GPIO Setup (MCP3008)

1. **Enable SPI**:
   ```bash
   sudo raspi-config
   # Navigate to: Interface Options > SPI > Enable
   ```

2. **Install spidev**:
   ```bash
   pip install spidev
   ```

3. **Wiring**:
   ```
   MQ-135 Connections:
   - VCC  → 5V
   - GND  → GND
   - AOUT → MCP3008 CH0

   MCP3008 Connections:
   Pin 1  (CH0)  → MQ-135 AOUT
   Pin 9  (DGND) → GND
   Pin 10 (CS)   → GPIO 8 (CE0)
   Pin 11 (DIN)  → GPIO 10 (MOSI)
   Pin 12 (DOUT) → GPIO 9 (MISO)
   Pin 13 (CLK)  → GPIO 11 (SCLK)
   Pin 14 (AGND) → GND
   Pin 15 (VREF) → 3.3V
   Pin 16 (VDD)  → 3.3V
   ```

4. **Configure**:
   ```yaml
   # config/sensors.yaml
   air_quality:
     backend: gpio
     gpio:
       channel: 0
       spi_bus: 0
       spi_device: 0
   ```

5. **Test**:
   ```bash
   python -c "from backend.sensors.air_quality import get_air_quality_reading; print(get_air_quality_reading())"
   ```

### Calibration

For accurate PPM readings, calibrate your MQ-135:

```python
from backend.sensors.air_quality import AirQualitySensor

# Initialize sensor
sensor = AirQualitySensor()
sensor.start()

# Expose to clean air for 60 seconds
# Then expose to known concentration (e.g., 100 PPM)
# Record raw value
data = sensor.read()
raw_value = data['raw_value']

# Calibrate
new_factor = sensor.calibrate(known_ppm=100, measured_raw=raw_value)
print(f"New calibration factor: {new_factor}")

# Update config/sensors.yaml
# air_quality:
#   calibration_factor: {new_factor}

sensor.stop()
```

### Air Quality Levels

- **Excellent**: 0-50 PPM (Fresh air)
- **Good**: 51-100 PPM (Acceptable)
- **Moderate**: 101-150 PPM (Sensitive groups affected)
- **Poor**: 151-200 PPM (Health effects)
- **Hazardous**: 200+ PPM (Serious health effects)

## Mock Mode (Testing Without Hardware)

Enable mock mode for any sensor in `config/sensors.yaml`:

```yaml
camera:
  mock_mode: true

microphone:
  mock_mode: true

air_quality:
  mock_mode: true
```

Mock mode generates realistic test data without requiring physical sensors.

## Verification

Test all sensors:

```bash
# Check sensor status
curl http://localhost:8000/api/sensors

# Start sensors
curl -X POST http://localhost:8000/api/sensors/manager/start

# Get health status
curl http://localhost:8000/api/sensors/manager/health

# Capture from each sensor
curl http://localhost:8000/api/sensors/camera/capture
curl http://localhost:8000/api/sensors/microphone/capture
curl http://localhost:8000/api/sensors/air_quality/capture
```

## Next Steps

- [Quick Start Guide](quick-start.md) - Start using CV-Mindcare
- [Web Dashboard Guide](../user-guide/web-dashboard.md) - Learn the interface
- [API Reference](../development/api-reference.md) - API documentation

## Support

Need help? Check:
- [Installation Guide](installation.md)
- [GitHub Issues](https://github.com/Salman-A-Alsahli/CV-Mindcare/issues)
- [Troubleshooting](#troubleshooting)
