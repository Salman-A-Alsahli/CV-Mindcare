#!/usr/bin/env python3
"""
Picamera2 + OpenCV Integration Demo
====================================

This script demonstrates how CV-Mindcare integrates Picamera2 (Raspberry Pi camera)
with OpenCV for image processing and greenery detection.

Key Features:
- Auto-detection of camera backend (Picamera2 or OpenCV)
- Picamera2 captures frames in RGB format
- OpenCV processes frames for greenery detection using HSV color space
- Automatic fallback to mock mode if no hardware available

Usage:
    python3 examples/picamera2_opencv_demo.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.sensors.camera_sensor import CameraSensor
import numpy as np


def demo_backend_selection():
    """Demonstrate automatic backend selection."""
    print("=" * 70)
    print("DEMO 1: Automatic Backend Selection")
    print("=" * 70)
    
    # Auto-detection (default)
    sensor = CameraSensor(config={'backend': 'auto'})
    print(f"\n✓ Created sensor with backend='auto'")
    print(f"  - Configured backend: {sensor.backend}")
    print(f"  - Resolution: {sensor.resolution}")
    print(f"  - Will try Picamera2 first, then OpenCV")
    
    # Force Picamera2
    sensor_pi = CameraSensor(config={'backend': 'picamera2'})
    print(f"\n✓ Created sensor with backend='picamera2'")
    print(f"  - Configured backend: {sensor_pi.backend}")
    print(f"  - Native Raspberry Pi camera support")
    
    # Force OpenCV
    sensor_cv = CameraSensor(config={'backend': 'opencv'})
    print(f"\n✓ Created sensor with backend='opencv'")
    print(f"  - Configured backend: {sensor_cv.backend}")
    print(f"  - USB webcam / generic camera support")
    print()


def demo_opencv_processing():
    """Demonstrate OpenCV processing of Picamera2 frames."""
    print("=" * 70)
    print("DEMO 2: OpenCV Processing of Camera Frames")
    print("=" * 70)
    
    sensor = CameraSensor(config={'backend': 'auto'})
    
    print("\n✓ HSV Color Space Parameters for Greenery Detection:")
    print(f"  - Hue range: {sensor.green_hue_range}° (green spectrum)")
    print(f"  - Saturation min: {sensor.saturation_min}")
    print(f"  - Value min: {sensor.value_min}")
    
    print("\n✓ OpenCV Functions Used:")
    print("  - cv2.cvtColor() - Convert RGB/BGR to HSV")
    print("  - cv2.inRange() - Create binary mask for green pixels")
    print("  - cv2.VideoCapture() - For OpenCV backend")
    print("  - Picamera2.capture_array() - For Picamera2 backend")
    
    print("\n✓ Processing Pipeline:")
    print("  1. Picamera2/OpenCV captures frame (RGB/BGR)")
    print("  2. OpenCV converts frame to HSV color space")
    print("  3. Create mask for pixels in green hue range")
    print("  4. Count green pixels to calculate percentage")
    print()


def demo_frame_capture():
    """Demonstrate actual frame capture and processing."""
    print("=" * 70)
    print("DEMO 3: Live Frame Capture and Greenery Detection")
    print("=" * 70)
    
    sensor = CameraSensor(config={'backend': 'auto'})
    
    print("\n✓ Starting sensor...")
    sensor.start()
    
    print(f"  - Hardware available: {not sensor.mock_mode}")
    print(f"  - Active backend: {sensor.backend}")
    print(f"  - Mock mode: {sensor.mock_mode}")
    
    print("\n✓ Capturing and analyzing 3 frames...\n")
    
    for i in range(3):
        data = sensor.read()
        
        print(f"  Frame {i+1}:")
        print(f"    - Timestamp: {data.get('timestamp', 'N/A')}")
        print(f"    - Greenery %: {data.get('greenery_percentage', 0):.2f}%")
        print(f"    - Frame shape: {data.get('frame_shape', 'N/A')}")
        print(f"    - Resolution: {data.get('resolution', 'N/A')}")
        
        if sensor.mock_mode:
            print(f"    - Mock scenario: {data.get('mock_scenario', 'N/A')}")
    
    print("\n✓ Stopping sensor...")
    sensor.stop()
    print()


def demo_color_space_conversion():
    """Demonstrate RGB vs BGR color space handling."""
    print("=" * 70)
    print("DEMO 4: Color Space Handling (Picamera2 RGB vs OpenCV BGR)")
    print("=" * 70)
    
    print("\n✓ Color Format Differences:")
    print("  - Picamera2: Captures in RGB format (Red, Green, Blue)")
    print("  - OpenCV: Captures in BGR format (Blue, Green, Red)")
    
    print("\n✓ Automatic Detection and Conversion:")
    print("  - System detects which backend is active")
    print("  - Applies correct conversion:")
    print("    • Picamera2: cv2.COLOR_RGB2HSV")
    print("    • OpenCV:    cv2.COLOR_BGR2HSV")
    
    print("\n✓ This ensures consistent HSV analysis regardless of backend!")
    print()


def demo_configuration():
    """Demonstrate configuration options."""
    print("=" * 70)
    print("DEMO 5: Configuration Options")
    print("=" * 70)
    
    print("\n✓ Basic Configuration (config/sensors.yaml):")
    print("""
camera:
  backend: auto              # 'auto', 'opencv', or 'picamera2'
  device_index: 0            # Camera index
  resolution:
    width: 640
    height: 480
  greenery_detection:
    lower_hsv: [35, 40, 40]  # Lower bound for green
    upper_hsv: [85, 255, 255] # Upper bound for green
    """)
    
    print("\n✓ Programmatic Configuration:")
    config = {
        'backend': 'auto',
        'resolution': (1280, 720),  # Higher resolution
        'green_hue_range': (30, 90),  # Wider green range
        'saturation_min': 50,
        'value_min': 50,
    }
    
    sensor = CameraSensor(config=config)
    print(f"  - Backend: {sensor.backend}")
    print(f"  - Resolution: {sensor.resolution}")
    print(f"  - Green hue range: {sensor.green_hue_range}")
    print(f"  - Saturation min: {sensor.saturation_min}")
    print()


def demo_installation():
    """Show installation instructions."""
    print("=" * 70)
    print("DEMO 6: Installation Instructions")
    print("=" * 70)
    
    print("\n✓ Install CV-Mindcare with Picamera2 support:")
    print("""
# On Raspberry Pi:
pip install -e .[rpi]

# This installs:
# - opencv-python (for image processing)
# - picamera2 (for Raspberry Pi camera)
# - All other dependencies
    """)
    
    print("✓ Verify Installation:")
    print("""
# Test OpenCV
python3 -c "import cv2; print('OpenCV:', cv2.__version__)"

# Test Picamera2 (on Raspberry Pi)
python3 -c "from picamera2 import Picamera2; print('Picamera2: OK')"

# Test integration
python3 examples/picamera2_opencv_demo.py
    """)
    print()


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Picamera2 + OpenCV Integration Demo for CV-Mindcare".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    try:
        demo_backend_selection()
        demo_opencv_processing()
        demo_color_space_conversion()
        demo_configuration()
        demo_frame_capture()
        demo_installation()
        
        print("=" * 70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nKey Takeaways:")
        print("  • Picamera2 support is fully integrated")
        print("  • OpenCV processes frames from both Picamera2 and USB cameras")
        print("  • Auto-detection tries Picamera2 first (faster on RPi)")
        print("  • Automatic fallback to mock mode for development")
        print("  • Consistent greenery detection across backends")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
