# CV-Mindcare Examples

This directory contains example scripts demonstrating key features of CV-Mindcare.

## Available Examples

### 1. Picamera2 + OpenCV Integration Demo

**File:** `picamera2_opencv_demo.py`

Demonstrates how CV-Mindcare integrates Raspberry Pi's Picamera2 library with OpenCV for image processing.

**Features:**
- Automatic backend selection (Picamera2 vs OpenCV)
- Color space conversion (RGB from Picamera2, BGR from OpenCV)
- HSV-based greenery detection
- Mock mode fallback for development without hardware

**Usage:**
```bash
python3 examples/picamera2_opencv_demo.py
```

**What it shows:**
1. **Backend Selection** - Auto-detection tries Picamera2 first (native RPi camera), then falls back to OpenCV
2. **OpenCV Processing** - How OpenCV functions are used to process frames from both backends
3. **Frame Capture** - Live demonstration of frame capture and greenery analysis
4. **Color Space Handling** - Proper conversion of RGB (Picamera2) vs BGR (OpenCV) formats
5. **Configuration** - How to configure the camera sensor programmatically or via YAML
6. **Installation** - Setup instructions for Raspberry Pi

## Running Examples

All examples can be run from the repository root:

```bash
# Run the Picamera2 demo
python3 examples/picamera2_opencv_demo.py

# Run with verbose output
python3 -v examples/picamera2_opencv_demo.py
```

## Example Output

When running on a system without camera hardware, the demos will automatically fall back to mock mode:

```
╔════════════════════════════════════════════════════════════════════╗
║         Picamera2 + OpenCV Integration Demo for CV-Mindcare        ║
╚════════════════════════════════════════════════════════════════════╝

DEMO 1: Automatic Backend Selection
✓ Created sensor with backend='auto'
  - Will try Picamera2 first, then OpenCV

DEMO 3: Live Frame Capture and Greenery Detection
✓ Starting sensor...
  - Hardware available: False
  - Active backend: auto
  - Mock mode: True

✓ Capturing and analyzing 3 frames...
  Frame 1:
    - Greenery %: 25.01%
    - Frame shape: (480, 640, 3)
    - Mock scenario: indoor_many_plants
```

## Hardware Requirements

- **Raspberry Pi Camera:** Requires `picamera2` library (auto-installed with `pip install -e .[rpi]`)
- **USB Webcam:** Requires `opencv-python` (auto-installed with base package)
- **No Camera:** All examples work in mock mode for development

## Dependencies

All examples require the base CV-Mindcare installation:

```bash
# Install base package
pip install -e .

# Install with Raspberry Pi support
pip install -e .[rpi]

# Install development dependencies
pip install -e .[dev]
```

## Integration with Main Application

These examples demonstrate features that are fully integrated into the main CV-Mindcare application:

- **Web Dashboard:** View live camera feed with greenery detection at http://localhost:5173
- **API:** Access camera data via REST API at http://localhost:8000/api/camera
- **Configuration:** Customize settings in `config/sensors.yaml`

## Contributing Examples

To add a new example:

1. Create a new Python file in this directory
2. Add documentation at the top explaining what it demonstrates
3. Include usage instructions and expected output
4. Update this README with a description of your example
5. Ensure the example works in both real and mock mode

## Troubleshooting

**Issue:** `ModuleNotFoundError: No module named 'backend'`
- **Solution:** Run examples from the repository root: `python3 examples/your_example.py`

**Issue:** `picamera2 not found` on Raspberry Pi
- **Solution:** Install with `pip install -e .[rpi]` or `pip install picamera2`

**Issue:** Camera not detected
- **Solution:** Examples automatically fall back to mock mode. Check camera connection and permissions.

## Additional Resources

- [Camera Sensor Documentation](../docs/getting-started/hardware-setup.md)
- [Raspberry Pi Deployment Guide](../docs/deployment/raspberry-pi.md)
- [API Reference](../docs/development/api-reference.md)
- [Architecture Overview](../docs/development/architecture.md)
