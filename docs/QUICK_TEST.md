# Quick Test: Independent Sensor Initialization

This script demonstrates that sensors initialize independently - missing hardware for one sensor does NOT force others into mock mode.

## Quick Test

Run this command to test your system:

```bash
cd /path/to/CV-Mindcare
python3 -m backend.sensors.sensor_manager_test
```

Or use this quick Python test:

```python
from backend.sensors.sensor_manager import SensorManager
from backend.config import config

# Start all sensors
manager = SensorManager(config.get_section('sensors'))
manager.start_all()

# Check status
status = manager.get_all_status()
for sensor_name, info in status['sensors'].items():
    mode = "REAL HARDWARE" if not info['mock_mode'] else "MOCK MODE"
    print(f"{sensor_name.upper()}: {mode} ({info['status']})")

manager.stop_all()
```

## Expected Results

### With MQ-135 on ADS1115 (I2C)

If you have the MQ-135 connected via ADS1115:

```
CAMERA: MOCK MODE (mock_mode)              ← No camera = mock
MICROPHONE: MOCK MODE (mock_mode)          ← No microphone = mock
AIR_QUALITY: REAL HARDWARE (active)        ← ADS1115 detected = real!
```

### With All Hardware Connected

```
CAMERA: REAL HARDWARE (active)
MICROPHONE: REAL HARDWARE (active)
AIR_QUALITY: REAL HARDWARE (active)
```

### With Only Microphone

```
CAMERA: MOCK MODE (mock_mode)
MICROPHONE: REAL HARDWARE (active)         ← Mic works independently!
AIR_QUALITY: MOCK MODE (mock_mode)
```

## What This Proves

✅ Each sensor initializes **independently**
✅ Missing hardware for one sensor does **NOT** force others into mock mode
✅ System continues working with any combination of real/mock sensors

## Verifying ADS1115 Connection

If air quality sensor is in mock mode but you have ADS1115 connected:

### 1. Check I2C is enabled:
```bash
ls -l /dev/i2c*
# Should show: /dev/i2c-1
```

### 2. Scan for I2C devices:
```bash
sudo i2cdetect -y 1
# Should show '48' at address 0x48
```

### 3. Check configuration:
```bash
cat config/sensors.yaml | grep -A 10 "air_quality:"
# Verify: backend: auto or backend: i2c
# Verify: mock_mode: false
```

### 4. Install required libraries:
```bash
pip3 install adafruit-circuitpython-ads1x15 adafruit-blinka
```

### 5. Check logs:
```bash
# Look for messages like:
# "I2C hardware detected (ADS1115 ADC available)"
# or error messages explaining why hardware not detected
```

## Troubleshooting

### Sensor always in mock mode despite hardware

1. **Check hardware connection** - Run hardware-specific tests
2. **Check permissions** - Some hardware needs sudo/permissions
3. **Check libraries** - Install sensor-specific libraries
4. **Check configuration** - Ensure `mock_mode: false` in config

### All sensors in mock mode

This is **normal** if no hardware is connected. The system is designed to work without hardware for development and testing.

### Want to force specific sensor to real mode only

You can't force real mode (by design for reliability). If hardware isn't detected, sensor uses mock mode. Fix the hardware detection instead.

## Configuration Reference

To use ADS1115 for MQ-135:

```yaml
# config/sensors.yaml
air_quality:
  backend: i2c              # or 'auto' for auto-detection
  i2c:
    channel: 0              # ADS1115 channel (0-3)
    address: 0x48           # I2C address
  calibration_factor: 1.0
  sample_count: 10
  mock_mode: false          # Use real hardware
```

## Documentation

- Full hardware setup: `docs/hardware/ADS1115_SETUP.md`
- Independent initialization: `docs/hardware/INDEPENDENT_INITIALIZATION.md`

## Summary

Your sensors are working correctly! Each one:
- Checks for its own hardware independently
- Uses real hardware if available
- Falls back to mock mode if hardware is missing
- Does NOT affect other sensors

This is the **intended behavior** for reliability and development flexibility.
