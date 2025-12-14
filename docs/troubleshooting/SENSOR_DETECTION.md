# Sensor Detection Troubleshooting Guide

This guide helps resolve issues where sensors are physically connected but the application still runs in mock mode.

## Quick Diagnosis

Run this command to check sensor hardware detection:

```bash
cd /path/to/CV-Mindcare  # Change to your project directory
python3 -c "
from backend.sensors.camera_sensor import CameraSensor
from backend.sensors.air_quality import AirQualitySensor

print('=== Camera Detection ===')
cam = CameraSensor({'backend': 'auto'})
print(f'Hardware available: {cam.check_hardware_available()}')

print('\n=== Air Quality Detection ===')
air = AirQualitySensor({'backend': 'auto'})
print(f'Hardware available: {air.check_hardware_available()}')
"
```

## Camera Sensor Issues

### Problem: Raspberry Pi Camera Connected but Not Detected

**Symptoms:**
- Camera hardware is physically connected (CSI cable to camera port)
- `libcamera-hello` or picamera2 shows camera is working
- Application logs show: "Camera hardware not available, falling back to MOCK_MODE"

**Solution:**

1. **Verify camera backend is set to `auto`** in `config/sensors.yaml`:
   ```yaml
   camera:
     backend: auto  # This enables auto-detection
     device_index: 0
   ```

2. **Check picamera2 is installed:**
   ```bash
   pip3 show picamera2
   # If not installed:
   pip3 install picamera2
   ```

3. **Test camera manually:**
   ```bash
   libcamera-hello --timeout 2000
   # Or:
   python3 -c "from picamera2 import Picamera2; cam = Picamera2(); print('Camera OK')"
   ```

4. **Review application logs** for initialization details:
   ```bash
   # Look for lines like:
   # "Auto-detecting camera backend..."
   # "Auto-selected backend: picamera2"
   # "Picamera2 hardware detected"
   ```

### Problem: USB Camera Not Detected

**Symptoms:**
- USB camera is plugged in
- Camera shows in `/dev/video0` (Linux)
- Application still uses mock mode

**Solution:**

1. **Verify OpenCV is installed:**
   ```bash
   pip3 show opencv-python
   # If not installed:
   pip3 install opencv-python
   ```

2. **Test camera access:**
   ```bash
   python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera opened:', cap.isOpened())"
   ```

3. **Check device index** in `config/sensors.yaml`:
   ```yaml
   camera:
     backend: auto
     device_index: 0  # Try 0, 1, 2 if you have multiple cameras
   ```

## Air Quality Sensor (I2C) Issues

### Problem: I2C Device Connected but Sensor in Mock Mode

**Symptoms:**
- `sudo i2cdetect -y 1` shows a device (e.g., at address 0x4b)
- Application logs show: "No I2C device found at 0x48"
- Sensor runs in mock mode

**Root Cause:** The I2C device address in configuration (default 0x48) doesn't match the actual device address.

**Solution:**

1. **Scan for I2C devices:**
   ```bash
   sudo i2cdetect -y 1
   ```

2. **Identify your device address** from the output:
   ```
        0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
   40: -- -- -- -- -- -- -- -- -- -- -- 4b -- -- -- --
   ```
   In this example, device is at **0x4b** (hex).

3. **Update `config/sensors.yaml`** with the correct address:
   ```yaml
   air_quality:
     backend: auto  # or 'i2c'
     
     i2c:
       channel: 0
       address: 0x4b  # Update this to match your device address!
   ```

4. **Restart the application:**
   ```bash
   python3 -m backend.app
   ```

5. **Verify in logs:**
   ```
   INFO: I2C device detected at address 0x4b
   INFO: ADS1115 I2C ADC initialized at 0x4b (channel=0, test_value=...)
   ```

### Common I2C Addresses

Different ADS1115 configurations use different addresses:

| ADDR Pin Connection | I2C Address |
|-------------------|-------------|
| GND (default)     | 0x48        |
| VDD               | 0x49        |
| SDA               | 0x4a        |
| SCL               | 0x4b        |

**Note:** If you see an I2C device but it's not an ADS1115, you may have a different sensor type. Check your hardware documentation.

## Backend Configuration Reference

### Camera Backend Options

```yaml
camera:
  backend: auto        # Auto-detect (tries picamera2 first, then opencv)
  # OR
  backend: picamera2   # Force Raspberry Pi camera
  # OR
  backend: opencv      # Force OpenCV/USB camera
```

### Air Quality Backend Options

```yaml
air_quality:
  backend: auto     # Auto-detect (tries I2C, then serial, then SPI)
  # OR
  backend: i2c      # Force I2C/ADS1115
  # OR
  backend: serial   # Force serial connection
  # OR
  backend: spi      # Force SPI/MCP3008
```

## Checking Logs for Errors

Enable detailed logging to diagnose issues:

```bash
# Set log level to DEBUG in backend/app.py or via environment variable
export LOG_LEVEL=DEBUG
python3 -m backend.app
```

Look for these log messages:

**Camera:**
- `Auto-detecting camera backend...`
- `Auto-selected backend: picamera2` (or `opencv`)
- `Picamera2 hardware detected` or `OpenCV camera 0 detected`
- `Camera Sensor started successfully`

**Air Quality:**
- `I2C device detected at address 0x...`
- `ADS1115 I2C ADC initialized at 0x... (channel=..., test_value=...)`
- `MQ-135 Air Quality Sensor started successfully`

**Errors to look for:**
- `No I2C device found at 0x...` → Update I2C address in config
- `Picamera2 not available:` → Install picamera2 or use opencv backend
- `OpenCV camera check failed:` → Check camera connection/drivers
- `Failed to initialize ADS1115 at address 0x...` → Check I2C wiring

## Still Having Issues?

If sensors still don't detect after following this guide:

1. **Check hardware connections:**
   - Camera: CSI cable firmly seated in both camera and board
   - I2C: SDA/SCL pins correctly connected, grounds shared
   - Power: All devices have proper voltage (3.3V for I2C, 5V for MQ-135)

2. **Verify I2C is enabled** (Raspberry Pi):
   ```bash
   sudo raspi-config
   # Interface Options → I2C → Enable
   sudo reboot
   ```

3. **Check for permission issues:**
   ```bash
   # Add user to required groups
   sudo usermod -a -G video,i2c,gpio $USER
   # Log out and log back in
   ```

4. **Test each sensor independently:**
   ```python
   # Test camera
   from backend.sensors.camera_sensor import CameraSensor
   sensor = CameraSensor({'backend': 'auto', 'mock_mode': False})
   sensor.start()
   print(f"Status: {sensor.status}")
   print(f"Mock mode: {sensor.mock_mode}")
   data = sensor.read()
   sensor.stop()
   
   # Test air quality
   from backend.sensors.air_quality import AirQualitySensor
   sensor = AirQualitySensor({'backend': 'auto', 'mock_mode': False})
   sensor.start()
   print(f"Status: {sensor.status}")
   print(f"Mock mode: {sensor.mock_mode}")
   data = sensor.read()
   sensor.stop()
   ```

5. **Check the GitHub issues** for similar problems or create a new issue with:
   - Output of `sudo i2cdetect -y 1`
   - Camera test results (`libcamera-hello` or cv2 test)
   - Application logs with DEBUG level
   - Your `config/sensors.yaml` configuration

## Related Documentation

- [ADS1115 Setup Guide](../hardware/ADS1115_SETUP.md) - Detailed I2C/ADC wiring
- [Hardware Setup Guide](../getting-started/hardware-setup.md) - All sensor setup
- [Raspberry Pi Deployment](../deployment/raspberry-pi.md) - Pi-specific configuration
