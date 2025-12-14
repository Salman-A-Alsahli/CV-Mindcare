# ADS1115 ADC Setup for MQ-135 Air Quality Sensor

This guide explains how to connect the MQ-135 air quality sensor to your Raspberry Pi using the ADS1115 16-bit I2C ADC.

## Why ADS1115?

The ADS1115 is the **recommended ADC** for the MQ-135 sensor because:

- **16-bit resolution** (vs 10-bit for MCP3008) provides more accurate PPM readings
- **I2C interface** requires only 2 wires (SDA, SCL) vs 4+ for SPI
- **Built-in programmable gain amplifier** for better signal quality
- **Wide availability** and low cost (~$5-10)
- **Better noise immunity** than SPI or analog connections

## Hardware Requirements

- Raspberry Pi (3, 4, or 5)
- MQ-135 air quality gas sensor module
- ADS1115 16-bit I2C ADC module
- Jumper wires
- Breadboard (optional)

## Wiring Diagram

### ADS1115 to Raspberry Pi

```
ADS1115          Raspberry Pi
-------          ------------
VDD      ---->   3.3V (Pin 1)
GND      ---->   GND (Pin 6)
SCL      ---->   SCL/GPIO 3 (Pin 5)
SDA      ---->   SDA/GPIO 2 (Pin 3)
```

### MQ-135 to ADS1115

```
MQ-135           ADS1115
------           -------
VCC      ---->   VDD (or separate 5V supply)
GND      ---->   GND
AOUT     ---->   A0 (or A1, A2, A3 - note your choice)
```

**Important Notes:**
- The MQ-135 sensor requires 5V power for the heater element
- The analog output (AOUT) can connect to any ADS1115 channel (A0-A3)
- If using separate 5V for MQ-135, **make sure grounds are connected**

## Complete Wiring Example

```
         +3.3V (Pin 1) ----+---- ADS1115 VDD
                           |
         +5V (Pin 2) -----------+ MQ-135 VCC
                           |    |
         GND (Pin 6) ------+----|---- ADS1115 GND
                                |---- MQ-135 GND
                                
         GPIO 2/SDA (Pin 3) ---- ADS1115 SDA
         GPIO 3/SCL (Pin 5) ---- ADS1115 SCL
         
         ADS1115 A0 ------------ MQ-135 AOUT
```

## Software Setup

### 1. Enable I2C on Raspberry Pi

```bash
sudo raspi-config
# Navigate to: Interface Options -> I2C -> Enable
```

Or manually edit `/boot/config.txt`:
```bash
sudo nano /boot/config.txt
# Add or uncomment:
dtparam=i2c_arm=on
```

Reboot after changes:
```bash
sudo reboot
```

### 2. Install Required Libraries

```bash
# Install system packages
sudo apt-get update
sudo apt-get install -y python3-pip i2c-tools

# Install Python libraries
pip3 install adafruit-circuitpython-ads1x15
pip3 install adafruit-blinka
```

### 3. Verify I2C Connection

```bash
# Check that I2C is enabled
ls -l /dev/i2c*
# Should show: /dev/i2c-1

# Scan for I2C devices (should show 0x48 for ADS1115)
sudo i2cdetect -y 1
```

Expected output:
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- 48 -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --
```

The `48` indicates the ADS1115 is detected at address 0x48 (default).

### 4. Test ADS1115 Reading

```python
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create ADS1115 object
ads = ADS.ADS1115(i2c)

# Create analog input on channel 0
chan = AnalogIn(ads, ADS.P0)

# Read values
print(f"Raw ADC Value: {chan.value}")
print(f"Voltage: {chan.voltage}V")
```

## Configuration

### Update `config/sensors.yaml`

For ADS1115 on I2C channel 0:

```yaml
air_quality:
  # Use 'i2c' or 'ads1115' backend
  backend: i2c
  
  # I2C/ADS1115 configuration
  i2c:
    channel: 0      # ADS1115 channel (0-3 for A0-A3)
    address: 0x48   # I2C address (default is 0x48)
  
  # Calibration
  calibration_factor: 1.0
  sample_count: 10
  
  # Mock mode disabled (use real hardware)
  mock_mode: false
```

### Channel Selection

Choose the channel based on your wiring:

```yaml
channel: 0  # For ADS1115 A0
channel: 1  # For ADS1115 A1
channel: 2  # For ADS1115 A2
channel: 3  # For ADS1115 A3
```

## Using the Sensor

### Python Code Example

```python
from backend.sensors.air_quality import AirQualitySensor

# Create sensor with I2C backend
sensor = AirQualitySensor(config={
    'backend': 'i2c',
    'i2c': {
        'channel': 0,
        'address': 0x48
    },
    'calibration_factor': 1.0
})

# Start sensor (will use ADS1115 if available, otherwise mock mode)
sensor.start()

# Read air quality data
data = sensor.read()
print(f"PPM: {data['ppm']}")
print(f"Air Quality: {data['air_quality_level']}")
print(f"Backend: {data['backend']}")  # Should show 'i2c'
print(f"Mock Mode: {data['mock_mode']}")  # Should show False

# Stop sensor
sensor.stop()
```

### Automatic Backend Selection

The sensor supports automatic backend detection. If you set `backend: auto`, it will try backends in this order:

1. **I2C (ADS1115)** - Preferred
2. **Serial** - If serial port exists
3. **SPI (MCP3008)** - Fallback
4. **Mock Mode** - If no hardware detected

```yaml
air_quality:
  backend: auto  # Will auto-detect and prefer I2C
```

## Troubleshooting

### I2C Device Not Detected

**Problem:** `i2cdetect` doesn't show device at 0x48

**Solutions:**
1. Check wiring - especially SDA/SCL connections
2. Verify I2C is enabled: `ls -l /dev/i2c*`
3. Try different I2C address (some modules use 0x49, 0x4A, 0x4B)
4. Check power supply to ADS1115 (should be 3.3V)

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'board'`

**Solution:**
```bash
pip3 install adafruit-blinka adafruit-circuitpython-ads1x15
```

### Sensor Always in Mock Mode

**Problem:** Sensor starts but uses mock mode despite I2C setup

**Solutions:**
1. Check logs for initialization errors
2. Verify `mock_mode: false` in config
3. Ensure ADS1115 libraries are installed
4. Test I2C connection with `i2cdetect -y 1`
5. Check MQ-135 is powered and connected to ADS1115

### Unstable or Noisy Readings

**Problem:** PPM values fluctuate wildly

**Solutions:**
1. **Wait for warm-up** - MQ-135 needs 24-48 hours initial burn-in
2. **Use averaging** - Increase `sample_count` in config (e.g., 20-50 samples)
3. **Add capacitor** - 0.1µF between AOUT and GND on MQ-135
4. **Calibrate** - Use the calibration feature with known concentration
5. **Check power supply** - Ensure stable 5V for MQ-135 heater

## Calibration

To calibrate the sensor with a known gas concentration:

```python
sensor = AirQualitySensor(config={'backend': 'i2c'})
sensor.start()

# Expose sensor to known concentration (e.g., 100 PPM)
# Wait for reading to stabilize
data = sensor.read()
raw_value = data['raw_value']

# Calibrate against known value
new_factor = sensor.calibrate(known_ppm=100.0, measured_raw=raw_value)
print(f"New calibration factor: {new_factor}")

# Update config with new calibration factor
# config/sensors.yaml:
#   air_quality:
#     calibration_factor: <new_factor>
```

## Independent Operation

**Important:** Each sensor (camera, microphone, air quality) operates **independently**. If the MQ-135/ADS1115 is not connected:

- The air quality sensor will enter **mock mode** automatically
- Other sensors (camera, microphone) will continue with **real hardware** if available
- The system will NOT force all sensors into mock mode

Example scenario:
```
Camera: No hardware → Mock mode
Microphone: Hardware available → Real mode
Air Quality (ADS1115): Hardware available → Real mode
```

All three sensors run independently with their own hardware status.

## Additional Resources

- [ADS1115 Datasheet](https://www.ti.com/lit/ds/symlink/ads1115.pdf)
- [MQ-135 Datasheet](https://www.winsen-sensor.com/d/files/PDF/Semiconductor%20Gas%20Sensor/MQ135%20(Ver1.4)%20-%20Manual.pdf)
- [Adafruit ADS1x15 Guide](https://learn.adafruit.com/adafruit-4-channel-adc-breakouts)
- [Raspberry Pi I2C Setup](https://www.raspberrypi.com/documentation/computers/os.html#i2c)

## Reference Specifications

### ADS1115 Specifications
- Resolution: 16-bit (65536 levels)
- Input Range: ±6.144V (programmable)
- Sample Rate: 8-860 SPS
- I2C Interface: Standard/Fast mode
- Operating Voltage: 2.0-5.5V

### MQ-135 Specifications
- Detects: NH3, NOx, alcohol, benzene, smoke, CO2
- Operating Voltage: 5V ±0.1V
- Preheat Time: >24 hours (optimal: 48 hours)
- Sensing Resistance: 30kΩ-200kΩ
- Concentration Range: 10-1000 PPM
