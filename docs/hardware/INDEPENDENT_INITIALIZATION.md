# Independent Sensor Initialization

## Overview

CV-Mindcare sensors (camera, microphone, air quality) operate **independently**. Each sensor:

- Initializes separately
- Detects its own hardware
- Falls back to mock mode individually if hardware is unavailable
- Does NOT affect other sensors' hardware status

## How It Works

### Individual Sensor Behavior

Each sensor follows this initialization flow:

```
1. Check if mock_mode explicitly requested in config
   ├─ Yes → Start in MOCK_MODE
   └─ No → Continue to hardware detection

2. Check hardware availability (check_hardware_available())
   ├─ Available → Try to initialize hardware
   │   ├─ Success → ACTIVE (real hardware mode)
   │   └─ Fail → Fall back to MOCK_MODE
   └─ Not Available → Fall back to MOCK_MODE
```

### Example Scenarios

#### Scenario 1: All Hardware Connected
```
Camera: ✓ Detected → ACTIVE (real mode)
Microphone: ✓ Detected → ACTIVE (real mode)
Air Quality: ✓ Detected → ACTIVE (real mode)
```

#### Scenario 2: Only Camera Missing
```
Camera: ✗ Not found → MOCK_MODE
Microphone: ✓ Detected → ACTIVE (real mode)
Air Quality: ✓ Detected → ACTIVE (real mode)
```

#### Scenario 3: Only Air Quality Connected
```
Camera: ✗ Not found → MOCK_MODE
Microphone: ✗ Not found → MOCK_MODE
Air Quality: ✓ Detected → ACTIVE (real mode)
```

#### Scenario 4: No Hardware
```
Camera: ✗ Not found → MOCK_MODE
Microphone: ✗ Not found → MOCK_MODE
Air Quality: ✗ Not found → MOCK_MODE
```

## Configuration

### Per-Sensor Mock Mode

You can force individual sensors into mock mode via configuration:

```yaml
# config/sensors.yaml

camera:
  backend: opencv
  mock_mode: false  # Use real hardware if available

microphone:
  backend: sounddevice
  mock_mode: true   # Force mock mode (testing)

air_quality:
  backend: auto
  mock_mode: false  # Use real hardware if available
```

In this configuration:
- Camera: Will use real hardware if camera is detected
- Microphone: **Forced** into mock mode (even if microphone available)
- Air Quality: Will use real hardware if ADS1115/MQ-135 detected

### Checking Sensor Status

```python
from backend.sensors.sensor_manager import SensorManager
from backend.config import config

# Create manager
manager = SensorManager(config.get_section('sensors'))
manager.start_all()

# Get status
status = manager.get_all_status()

for sensor_name, sensor_info in status['sensors'].items():
    print(f"{sensor_name}:")
    print(f"  Status: {sensor_info['status']}")
    print(f"  Mock mode: {sensor_info['mock_mode']}")
    print(f"  Active: {sensor_info['active']}")
```

Example output:
```
camera:
  Status: mock_mode
  Mock mode: True
  Active: True

microphone:
  Status: active
  Mock mode: False
  Active: True

air_quality:
  Status: active
  Mock mode: False
  Active: True
```

## Reading Data

### Individual Sensor

```python
from backend.sensors.camera_sensor import CameraSensor

# Create and start
sensor = CameraSensor()
sensor.start()  # Automatically detects hardware

# Check status
print(f"Mock mode: {sensor.mock_mode}")
print(f"Status: {sensor.status.value}")

# Read data (works in both real and mock mode)
data = sensor.read()
print(f"Greenery: {data['greenery_percentage']}%")
print(f"Is mock data: {data.get('mock_mode', False)}")

sensor.stop()
```

### Via Sensor Manager

```python
from backend.sensors.sensor_manager import SensorManager
from backend.config import config

# Start all sensors
manager = SensorManager(config.get_section('sensors'))
manager.start_all()  # Each sensor initializes independently

# Read from all (each provides real or mock data independently)
result = manager.read_all()

print("Data from sensors:")
for sensor_name, sensor_data in result['data'].items():
    print(f"  {sensor_name}: {sensor_data}")

print("\nErrors (if any):")
for sensor_name, error in result['errors'].items():
    print(f"  {sensor_name}: {error}")

manager.stop_all()
```

## Benefits of Independent Initialization

### 1. **Graceful Degradation**
- System continues to work even if some sensors are missing
- Users get partial data instead of complete failure

### 2. **Development Flexibility**
- Test with any combination of real/mock sensors
- Develop without requiring all hardware

### 3. **Production Reliability**
- Sensor failure doesn't crash entire system
- Other sensors continue operating normally

### 4. **Easy Debugging**
- Identify which specific sensor has hardware issues
- Test sensors individually

## Testing Individual Sensors

### Camera Sensor

```bash
python3 -c "
from backend.sensors.camera_sensor import CameraSensor
sensor = CameraSensor()
sensor.start()
print(f'Camera: {sensor.status.value} (mock={sensor.mock_mode})')
data = sensor.read()
print(f'Greenery: {data[\"greenery_percentage\"]}%')
sensor.stop()
"
```

### Microphone Sensor

```bash
python3 -c "
from backend.sensors.microphone_sensor import MicrophoneSensor
sensor = MicrophoneSensor()
sensor.start()
print(f'Microphone: {sensor.status.value} (mock={sensor.mock_mode})')
data = sensor.read()
print(f'dB: {data[\"db_level\"]} ({data[\"noise_classification\"]})')
sensor.stop()
"
```

### Air Quality Sensor

```bash
python3 -c "
from backend.sensors.air_quality import AirQualitySensor
sensor = AirQualitySensor()
sensor.start()
print(f'Air Quality: {sensor.status.value} (mock={sensor.mock_mode})')
data = sensor.read()
print(f'PPM: {data[\"ppm\"]} ({data[\"air_quality_level\"]})')
sensor.stop()
"
```

## Implementation Details

### BaseSensor Class

All sensors inherit from `BaseSensor` which implements the independent initialization logic:

```python
# backend/sensors/base.py

def start(self) -> bool:
    # Check if mock mode explicitly requested
    if self.mock_mode:
        self.status = SensorStatus.MOCK_MODE
        return True
    
    # Check hardware availability
    if not self.check_hardware_available():
        logger.warning(f"{self.name} hardware not available, falling back to MOCK_MODE")
        self.status = SensorStatus.MOCK_MODE
        self.mock_mode = True
        return True
    
    # Try to initialize real hardware
    if self.initialize():
        self.status = SensorStatus.ACTIVE
        return True
    else:
        # Initialization failed, fall back to mock mode
        logger.warning(f"{self.name} initialization failed, falling back to MOCK_MODE")
        self.status = SensorStatus.MOCK_MODE
        self.mock_mode = True
        return True
```

### Hardware Detection Methods

Each sensor implements `check_hardware_available()`:

```python
# Camera sensor
def check_hardware_available(self) -> bool:
    if self.backend == "opencv":
        test_cap = cv2.VideoCapture(self.camera_index)
        available = test_cap.isOpened()
        test_cap.release()
        return available

# Microphone sensor
def check_hardware_available(self) -> bool:
    if self.backend == "sounddevice":
        devices = sd.query_devices()
        input_devices = [d for d in devices if d.get("max_input_channels", 0) > 0]
        return len(input_devices) > 0

# Air quality sensor
def check_hardware_available(self) -> bool:
    if self.backend in ("i2c", "ads1115", "auto"):
        try:
            import board, busio
            i2c = busio.I2C(board.SCL, board.SDA)
            i2c.deinit()
            return True
        except:
            return False
```

## Common Issues

### Issue: Sensor enters mock mode despite hardware being connected

**Diagnosis:**
1. Check sensor status: `sensor.get_status()`
2. Check logs for hardware detection messages
3. Verify hardware connections
4. Test hardware directly (e.g., `i2cdetect` for I2C devices)

**Solutions:**
- For camera: Check `/dev/video*` exists, verify OpenCV can access it
- For microphone: Run `arecord -l` to list capture devices
- For air quality: Run `i2cdetect -y 1` to check I2C devices

### Issue: Want to force sensor into real mode (disable mock fallback)

**Answer:** This is not supported by design. The mock mode fallback ensures system reliability. If hardware is not detected, the sensor will use mock mode to prevent crashes.

### Issue: Need to test system without any hardware

**Solution:** Set `mock_mode: true` for all sensors in config:

```yaml
camera:
  mock_mode: true

microphone:
  mock_mode: true

air_quality:
  mock_mode: true
```

## Summary

✓ Each sensor initializes **independently**
✓ Missing hardware for one sensor does **NOT** affect others
✓ Sensors automatically fall back to mock mode when hardware unavailable
✓ System continues operating with any combination of real/mock sensors
✓ Easy to test and debug individual sensors
