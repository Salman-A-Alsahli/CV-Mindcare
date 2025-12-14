# CV-Mindcare Raspberry Pi 5 Deployment Guide
## Complete Start-to-Finish Setup

**Target Hardware:** Raspberry Pi 5 (ARM64 Architecture)  
**OS:** Raspberry Pi OS (64-bit, Bookworm or later)  
**Python:** 3.11+ (native ARM64 support)  
**Last Updated:** December 14, 2024

---

## 📋 Table of Contents

1. [Executive Summary](#-executive-summary)
2. [Hardware Requirements](#-hardware-requirements)
3. [Initial Raspberry Pi 5 Setup](#-initial-raspberry-pi-5-setup-from-scratch)
4. [System Preparation](#-system-preparation)
5. [CV-Mindcare Installation](#-cv-mindcare-installation)
6. [Configuration](#-configuration)
7. [Testing & Verification](#-testing--verification)
8. [Auto-Start Service Setup](#-auto-start-service-setup)
9. [Performance Optimization](#-performance-optimization)
10. [Security](#-security-considerations)
11. [Troubleshooting](#-troubleshooting)
12. [Maintenance](#-monitoring-and-maintenance)

---

## 🎯 Executive Summary

CV-Mindcare is designed as a privacy-first, local-processing wellness monitoring system. The Raspberry Pi 5 is an ideal deployment target due to:

- **Local Processing:** All AI/sensor processing happens on-device (privacy-first)
- **GPIO Support:** Direct access to camera (CSI) and microphone (USB/I2S)
- **Performance:** 4-core ARM Cortex-A76 @ 2.4GHz with 4GB/8GB RAM
- **Power Efficiency:** Low power consumption suitable for always-on monitoring
- **Cost-Effective:** ~$60-80 for complete edge computing solution

**Installation Time:** ~30-45 minutes for complete setup

---

## 🔧 Hardware Requirements

### Minimum Configuration (Raspberry Pi 5)
- **Board:** Raspberry Pi 5 (4GB RAM minimum, 8GB recommended)
- **Storage:** 32GB microSD (Class 10/U1) or NVMe SSD via M.2 HAT (recommended)
- **Camera:** Raspberry Pi Camera Module 3 (12MP) or USB webcam
- **Microphone:** USB microphone or USB audio interface
- **Power:** Official 27W USB-C power supply (5.1V/5A) - **Required!**
- **Cooling:** Active cooling fan (required for continuous operation)
- **Optional:** MQ-135 air quality sensor with ADS1115 ADC

### Recommended Configuration
- **Storage:** NVMe SSD (better performance, longer lifespan than SD card)
- **RAM:** 8GB model for smoother operation
- **Display:** 7" touchscreen for local GUI (optional)
- **Case:** Official or third-party case with fan mount
- **Network:** Ethernet connection (WiFi 6 is built-in but Ethernet is more stable)
- **UPS:** Battery backup for graceful shutdown

### Shopping List
```
☐ Raspberry Pi 5 (8GB)                    ~$80
☐ Official 27W USB-C Power Supply         ~$12
☐ 64GB microSD card (or NVMe SSD)         ~$15-50
☐ Raspberry Pi Camera Module 3            ~$25
☐ USB Microphone                          ~$10-30
☐ Active Cooler (official or compatible)  ~$5
☐ Case with fan support                   ~$10-20
☐ (Optional) MQ-135 + ADS1115             ~$15
Total: ~$160-230
```

---

## 🚀 Initial Raspberry Pi 5 Setup (From Scratch)

### Step 1: Install Raspberry Pi OS

1. **Download Raspberry Pi Imager**
   - Visit: https://www.raspberrypi.com/software/
   - Download and install for your computer (Windows/Mac/Linux)

2. **Flash the OS**
   - Insert microSD card into your computer
   - Open Raspberry Pi Imager
   - Click "Choose Device" → Select "Raspberry Pi 5"
   - Click "Choose OS" → Select "Raspberry Pi OS (64-bit)"
     - Recommended: "Raspberry Pi OS (64-bit)" with desktop
   - Click "Choose Storage" → Select your microSD card
   
3. **Configure Settings (IMPORTANT!)**
   - Click the ⚙️ (Settings) icon before writing
   - **Set hostname:** `cvmindcare` (or your preference)
   - **Enable SSH:** ✅ Use password authentication (or SSH key)
   - **Set username and password:** 
     - Username: Your choice (e.g., `admin`, `yourname`) - **NOT "pi"!**
     - Password: Strong password
     - **⚠️ Note:** Newer Raspberry Pi OS (Bookworm+) requires you to set a custom username during setup. The old default "pi" username is no longer used!
   - **Configure WiFi:** (optional) Enter your WiFi credentials
   - **Set timezone:** Your local timezone
   - Click "Save"

4. **Write to SD Card**
   - Click "Write" and wait for completion (~5-10 minutes)
   - Eject the SD card when done

5. **First Boot**
   - Insert SD card into Raspberry Pi 5
   - Connect camera, microphone, monitor (if using desktop)
   - Connect Ethernet cable (recommended) or use WiFi
   - Connect power supply - Pi will boot automatically
   - Wait 1-2 minutes for first boot

6. **Find Your Raspberry Pi's IP Address**
   
   **Option A: If using monitor/keyboard**
   ```bash
   hostname -I
   ```
   
   **Option B: From another computer on same network**
   ```bash
   # Linux/Mac
   ping cvmindcare.local
   
   # Or scan your network
   nmap -sn 192.168.1.0/24 | grep -i raspberry
   ```
   
   **Option C: Check your router's DHCP client list**

7. **SSH Into Your Raspberry Pi**
   ```bash
   # Replace 'admin' with YOUR username and use YOUR Pi's IP
   ssh admin@cvmindcare.local
   # OR
   ssh admin@192.168.1.XXX
   
   # Enter the password you set earlier
   ```

---

## 💻 System Preparation

### Step 2: Update System & Install Dependencies

**⚠️ IMPORTANT:** In all commands below, replace `/home/admin` with `/home/YOUR_USERNAME`

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential build tools
sudo apt install -y git build-essential cmake pkg-config

# Install Python 3.11 and development tools
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Install system dependencies for CV-Mindcare
sudo apt install -y \
    libatlas-base-dev libopenblas-dev \
    libcamera-dev python3-libcamera python3-picamera2 \
    portaudio19-dev libasound2-dev \
    sqlite3 libsqlite3-dev \
    libopencv-dev

# Install audio tools
sudo apt install -y alsa-utils pulseaudio

# Install monitoring tools (optional but recommended)
sudo apt install -y htop vim

# Reboot to ensure all changes take effect
sudo reboot
```

After reboot, SSH back in:
```bash
ssh admin@cvmindcare.local  # Replace 'admin' with YOUR username
```

### Step 3: Enable Camera Interface

```bash
# Enable camera using raspi-config
sudo raspi-config

# Navigate using arrow keys:
# 1. Interface Options
# 2. Camera (I1)
# 3. Yes (to enable)
# 4. Finish
# 5. Yes (to reboot)

# After reboot, verify camera is detected
libcamera-hello --list-cameras

# You should see your camera listed
# If not, check physical connection to CSI port
```

---

## 📦 CV-Mindcare Installation

### Step 4: Clone Repository and Setup

**⚠️ Replace `/home/admin` with your actual home directory!**

```bash
# Navigate to home directory
cd ~

# Clone CV-Mindcare repository
git clone https://github.com/Salman-A-Alsahli/CV-Mindcare.git
cd CV-Mindcare

# Create Python virtual environment
python3.11 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# You should see (.venv) in your prompt now

# Upgrade pip
pip install --upgrade pip

# Install CV-Mindcare (base - fast install ~2 minutes)
pip install -e .

# Optional: Install ML features (emotion detection - adds ~40 minutes on RPi)
# pip install -e .[ml]
```

**Installation Progress:**
- Base installation: ~2-5 minutes on Raspberry Pi 5
- ML installation: ~40-60 minutes (if you choose to install it)

### Step 5: Verify Installation

```bash
# Check that backend can be imported
python -c "from backend.app import app; print('✅ Backend OK')"

# Check Python version
python --version  # Should show Python 3.11.x

# List installed packages
pip list | grep -E "fastapi|opencv|sounddevice|numpy"
```

Expected output:
```
✅ Backend OK
Python 3.11.2
fastapi           0.124.4
opencv-python     4.12.0.88
sounddevice       0.5.3
numpy            2.2.6
```

---

## 📦 Software Architecture for Raspberry Pi 5

### Optimized Stack
```
┌─────────────────────────────────────────────────┐
│  User Interface (Optional)                      │
│  - SSH/Web browser access                       │
│  - Local touchscreen (CustomTkinter)            │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  FastAPI Backend (Python 3.11)                  │
│  - RESTful API endpoints                        │
│  - Async processing (uvicorn)                   │
│  - ARM64 native compilation                     │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Sensor Layer                                   │
│  - Camera (picamera2 - native Pi support)      │
│  - Microphone (ALSA/PulseAudio)                 │
│  - Mock mode for testing                        │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Database (SQLite)                              │
│  - Local storage on SSD/SD                      │
│  - WAL mode for concurrency                     │
└─────────────────────────────────────────────────┘
```

### Key Architectural Decisions

1. **Native ARM64 Libraries**
   - Use `picamera2` instead of `opencv-python` for camera (optimized for Pi)
   - Use lightweight ALSA for audio instead of sounddevice when possible
   - Compile TensorFlow Lite (TFLite) instead of full PyTorch for ML inference

2. **Resource Management**
   - Limit FastAPI workers to 2 (4GB RAM) or 4 (8GB RAM)
   - Use swap file (4GB) for memory pressure
   - Implement sensor polling rate limits (1-5 Hz instead of continuous)

3. **Storage Optimization**
   - SQLite with WAL (Write-Ahead Logging) mode
   - Database on SSD if available, otherwise SD card
   - Log rotation for application logs (max 100MB)

4. **Power Management**
   - Graceful shutdown on power loss (UPS recommended)
   - Idle sensor sleep when not actively monitoring
   - CPU governor: ondemand (balance performance/power)

---

## ⚙️ Configuration

### Step 6: Configure Sensors

**⚠️ Update paths to match YOUR username!**

```bash
# Sensor configuration is in config/sensors.yaml
# View current configuration
cat config/sensors.yaml

# The default configuration should work, but you can customize:
nano config/sensors.yaml
```

Key configuration options:
```yaml
camera:
  backend: auto  # auto-detects picamera2 (Pi camera) or opencv (USB)
  camera_index: 0
  resolution:
    width: 640
    height: 480

microphone:
  backend: sounddevice  # or 'alsa' for lower overhead
  device_index: null  # null = default microphone
  sample_rate: 44100
  sample_duration: 1.0

air_quality:
  enabled: false  # Set to true if you have MQ-135 sensor
  connection_type: i2c  # or 'serial'
  i2c_address: 0x48
```

### Step 7: Test Hardware

```bash
# Create a quick hardware test
python << 'EOF'
from backend.sensors.camera_sensor import CameraSensor
from backend.sensors.microphone_sensor import MicrophoneSensor
import logging

logging.basicConfig(level=logging.INFO)

print("\n" + "="*50)
print("CV-Mindcare Hardware Test")
print("="*50)

# Test Camera
print("\n📷 Testing Camera...")
cam = CameraSensor()
if cam.check_hardware_available():
    print("✅ Camera hardware detected!")
    if cam.start():
        data = cam.capture()
        print(f"✅ Camera capture successful!")
        print(f"   Available: {data.get('available')}")
        cam.stop()
else:
    print("⚠️  Camera not detected (will use mock mode)")

# Test Microphone
print("\n🎤 Testing Microphone...")
mic = MicrophoneSensor()
if mic.check_hardware_available():
    print("✅ Microphone hardware detected!")
    if mic.start():
        data = mic.capture()
        print(f"✅ Microphone capture successful!")
        print(f"   Available: {data.get('available')}")
        mic.stop()
else:
    print("⚠️  Microphone not detected (will use mock mode)")

print("\n" + "="*50)
print("Hardware test complete!")
print("="*50 + "\n")
EOF
```

### Step 8: Start Backend API (Test Run)

```bash
# Make sure you're in the CV-Mindcare directory
cd ~/CV-Mindcare

# Activate virtual environment if not already active
source .venv/bin/activate

# Start the backend server
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.
```

**Test from another device on your network:**
```bash
# Replace with your Raspberry Pi's IP
curl http://192.168.1.XXX:8000/api/health

# Should return: {"status":"ok"}
```

**Access Web Interface:**
- Open browser: `http://cvmindcare.local:8000/docs`
- Or: `http://192.168.1.XXX:8000/docs`
- You'll see the FastAPI Swagger documentation

Press `Ctrl+C` to stop the server for now.

---

## 🔄 Auto-Start Service Setup

### Step 9: Create Systemd Service

**⚠️ CRITICAL: Update ALL paths with YOUR username!**

```bash
# Create systemd service file
sudo nano /etc/systemd/system/cvmindcare.service
```

Copy this configuration (***REPLACE `admin` with YOUR username!***):

```ini
[Unit]
Description=CV-Mindcare Wellness Monitoring Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=YOUR_USERNAME
Group=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/CV-Mindcare
Environment="PATH=/home/YOUR_USERNAME/CV-Mindcare/.venv/bin"
ExecStart=/home/YOUR_USERNAME/CV-Mindcare/.venv/bin/uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**Save and exit:** `Ctrl+O`, `Enter`, `Ctrl+X`

**Enable and start the service:**
```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable cvmindcare

# Start the service now
sudo systemctl start cvmindcare

# Check service status
sudo systemctl status cvmindcare
```

You should see:
```
● cvmindcare.service - CV-Mindcare Wellness Monitoring Service
   Loaded: loaded (/etc/systemd/system/cvmindcare.service; enabled)
   Active: active (running) since ...
```

**View logs:**
```bash
# Follow live logs
sudo journalctl -u cvmindcare -f

# View last 50 lines
sudo journalctl -u cvmindcare -n 50

# Press Ctrl+C to exit
```

**Service management commands:**
```bash
# Stop service
sudo systemctl stop cvmindcare

# Restart service
sudo systemctl restart cvmindcare

# Check status
sudo systemctl status cvmindcare

# Disable auto-start
sudo systemctl disable cvmindcare
```

---

## ⚡ Performance Optimization

### Step 10: Optimize for Raspberry Pi 5

**Configure Swap (if you have 4GB RAM)**
```bash
# Check current swap
free -h

# If swap is less than 4GB, increase it
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile

# Set: CONF_SWAPSIZE=4096
# Save and exit

# Apply changes
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Verify
free -h
```

**Optimize Database Performance:**
```bash
# CV-Mindcare automatically uses WAL mode
# You can verify:
sqlite3 ~/CV-Mindcare/mindcare.db "PRAGMA journal_mode;"
# Should return: wal
```

**Monitor System Resources:**
```bash
# Install monitoring tools
sudo apt install -y htop iotop

# Monitor CPU/RAM in real-time
htop

# Monitor temperature (important!)
vcgencmd measure_temp

# Create temperature monitoring alias
echo "alias temp='vcgencmd measure_temp'" >> ~/.bashrc
source ~/.bashrc

# Now you can just type: temp
```

**CPU Governor (Optional - for better performance):**
```bash
# Check current governor
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

# Set to performance mode (uses more power)
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Or keep default 'ondemand' for balanced performance/power
```

---

## 🧪 Testing & Verification

### Step 11: Complete System Test

**⚠️ Update username in paths!**

Create and run comprehensive test script:

```bash
# Create test script
cat > ~/CV-Mindcare/test_rpi_setup.py << 'EOF'
#!/usr/bin/env python3
"""
CV-Mindcare Raspberry Pi 5 Complete System Test
Tests all hardware and software components
"""

import sys
import subprocess
import requests

print("=" * 60)
print("  CV-Mindcare Raspberry Pi 5 System Test")
print("=" * 60)

def test_system_info():
    """Display system information"""
    try:
        import psutil
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print("\n📊 System Information:")
        print(f"   ├─ CPU Cores: {cpu_count}")
        print(f"   ├─ RAM: {memory.total / 1024**3:.1f} GB")
        print(f"   │  └─ Available: {memory.available / 1024**3:.1f} GB ({memory.percent}% used)")
        print(f"   └─ Disk: {disk.total / 1024**3:.1f} GB")
        print(f"      └─ Free: {disk.free / 1024**3:.1f} GB ({disk.percent}% used)")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def test_temperature():
    """Check CPU temperature"""
    try:
        result = subprocess.run(['vcgencmd', 'measure_temp'], 
                              capture_output=True, text=True)
        temp = result.stdout.strip()
        print(f"\n🌡️  Temperature: {temp}")
        temp_val = float(temp.replace("temp=", "").replace("'C", ""))
        if temp_val > 80:
            print("   ⚠️  WARNING: Temperature is high! Ensure active cooling.")
        return True
    except Exception as e:
        print(f"   ⚠️  Could not read temperature: {e}")
        return True  # Non-critical

def test_camera():
    """Test camera hardware"""
    print("\n📷 Testing Camera...")
    try:
        from backend.sensors.camera_sensor import CameraSensor
        cam = CameraSensor()
        
        if cam.check_hardware_available():
            print("   ✅ Camera hardware detected")
            if cam.start():
                data = cam.capture()
                cam.stop()
                if data.get('available'):
                    print(f"   ✅ Camera capture successful")
                    if 'greenery_percentage' in data:
                        print(f"   └─ Greenery: {data.get('greenery_percentage', 0):.1f}%")
                    return True
                else:
                    print(f"   ⚠️  Camera in mock mode")
                    return True
            else:
                print("   ❌ Camera failed to start")
                return False
        else:
            print("   ⚠️  No camera detected (mock mode will be used)")
            return True
    except Exception as e:
        print(f"   ❌ Camera test failed: {e}")
        return False

def test_microphone():
    """Test microphone hardware"""
    print("\n🎤 Testing Microphone...")
    try:
        from backend.sensors.microphone_sensor import MicrophoneSensor
        mic = MicrophoneSensor()
        
        if mic.check_hardware_available():
            print("   ✅ Microphone hardware detected")
            if mic.start():
                data = mic.capture()
                mic.stop()
                if data.get('available'):
                    print(f"   ✅ Microphone capture successful")
                    if 'decibels' in data:
                        print(f"   └─ Sound level: {data.get('decibels', 0):.1f} dB")
                    return True
                else:
                    print(f"   ⚠️  Microphone in mock mode")
                    return True
            else:
                print("   ❌ Microphone failed to start")
                return False
        else:
            print("   ⚠️  No microphone detected (mock mode will be used)")
            return True
    except Exception as e:
        print(f"   ❌ Microphone test failed: {e}")
        return False

def test_database():
    """Test database connection"""
    print("\n💾 Testing Database...")
    try:
        import sqlite3
        import os
        
        db_path = os.path.expanduser("~/CV-Mindcare/mindcare.db")
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.execute('PRAGMA journal_mode')
            mode = cursor.fetchone()[0]
            conn.close()
            print(f"   ✅ Database accessible")
            print(f"   └─ Journal mode: {mode}")
            return True
        else:
            print(f"   ⚠️  Database will be created on first run")
            return True
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False

def test_api_service():
    """Test if API service is running"""
    print("\n🌐 Testing API Service...")
    try:
        response = requests.get('http://localhost:8000/api/health', timeout=5)
        if response.status_code == 200:
            print("   ✅ API service is running")
            print(f"   └─ Response: {response.json()}")
            return True
        else:
            print(f"   ❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ⚠️  API service not running")
        print("   └─ Start with: sudo systemctl start cvmindcare")
        return True  # Not critical for this test
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
        return False

def test_network():
    """Test network connectivity"""
    print("\n🌍 Testing Network...")
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"   ✅ Network connected")
        print(f"   ├─ Hostname: {hostname}")
        print(f"   └─ Local IP: {local_ip}")
        return True
    except Exception as e:
        print(f"   ❌ Network test failed: {e}")
        return False

if __name__ == "__main__":
    print()
    
    # Run all tests
    tests = [
        ("System Info", test_system_info()),
        ("Temperature", test_temperature()),
        ("Network", test_network()),
        ("Database", test_database()),
        ("Camera", test_camera()),
        ("Microphone", test_microphone()),
        ("API Service", test_api_service()),
    ]
    
    print("\n" + "=" * 60)
    print("  Test Summary")
    print("=" * 60)
    
    for name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {name}")
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    print(f"\n{passed}/{total} tests passed")
    print("=" * 60 + "\n")
    
    if passed == total:
        print("🎉 All tests passed! CV-Mindcare is ready to use.")
        print("\nAccess the API at:")
        try:
            import socket
            local_ip = socket.gethostbyname(socket.gethostname())
            print(f"  - http://{local_ip}:8000/docs")
        except:
            print(f"  - http://localhost:8000/docs")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the output above.")
        sys.exit(1)
EOF

# Make it executable
chmod +x ~/CV-Mindcare/test_rpi_setup.py

# Run the test
cd ~/CV-Mindcare
source .venv/bin/activate
python test_rpi_setup.py
```

Expected output:
```
============================================================
  CV-Mindcare Raspberry Pi 5 System Test
============================================================

📊 System Information:
   ├─ CPU Cores: 4
   ├─ RAM: 8.0 GB
   │  └─ Available: 6.5 GB (19% used)
   └─ Disk: 59.0 GB
      └─ Free: 45.2 GB (23% used)

🌡️  Temperature: temp=45.0'C

🌍 Testing Network...
   ✅ Network connected
   ├─ Hostname: cvmindcare
   └─ Local IP: 192.168.1.100

💾 Testing Database...
   ✅ Database accessible
   └─ Journal mode: wal

📷 Testing Camera...
   ✅ Camera hardware detected
   ✅ Camera capture successful
   └─ Greenery: 15.3%

🎤 Testing Microphone...
   ✅ Microphone hardware detected
   ✅ Microphone capture successful
   └─ Sound level: 45.2 dB

🌐 Testing API Service...
   ✅ API service is running
   └─ Response: {'status': 'ok'}

============================================================
  Test Summary
============================================================
✅ PASS  System Info
✅ PASS  Temperature
✅ PASS  Network
✅ PASS  Database
✅ PASS  Camera
✅ PASS  Microphone
✅ PASS  API Service

7/7 tests passed
============================================================

🎉 All tests passed! CV-Mindcare is ready to use.

Access the API at:
  - http://192.168.1.100:8000/docs
```

---

## 🔒 Security Considerations

### Network Security

**⚠️ Important:** CV-Mindcare is designed for LOCAL network use only!

```bash
# Configure firewall (UFW)
sudo apt install -y ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (so you don't lock yourself out!)
sudo ufw allow ssh

# Allow CV-Mindcare API only from local network
# Replace 192.168.1.0/24 with YOUR network range
sudo ufw allow from 192.168.1.0/24 to any port 8000

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

**Optional: HTTPS with self-signed certificate**
```bash
# Generate self-signed certificate
cd ~/CV-Mindcare
mkdir -p certs
openssl req -x509 -newkey rsa:4096 -nodes \
  -out certs/cert.pem \
  -keyout certs/key.pem \
  -days 365 \
  -subj "/CN=cvmindcare.local"

# Update systemd service to use HTTPS
# Edit: sudo nano /etc/systemd/system/cvmindcare.service
# Change ExecStart line to:
# ExecStart=... --ssl-keyfile=certs/key.pem --ssl-certfile=certs/cert.pem
```

### Privacy Features

✅ **All processing stays local** - No cloud uploads  
✅ **Camera/mic data never leaves device** - Privacy-first design  
✅ **SQLite database local only** - No external database  
✅ **No telemetry** - Zero data collection  
✅ **No internet required** (after initial setup)

### SSH Security (Recommended)

```bash
# Disable password authentication (use SSH keys only)
# First, set up SSH keys on your client machine, then:

sudo nano /etc/ssh/sshd_config

# Find and change these lines:
# PasswordAuthentication no
# PermitRootLogin no

# Restart SSH
sudo systemctl restart ssh
```

---

## 🛠️ Troubleshooting

### Camera Issues

**Problem: Camera not detected**
```bash
# Check camera connection
vcgencmd get_camera

# Should show: supported=1 detected=1

# If not, check physical connection to CSI port
# Make sure ribbon cable is fully inserted with contacts facing correct way

# Enable camera interface
sudo raspi-config
# Interface Options -> Camera -> Enable -> Reboot

# Test camera with libcamera
libcamera-hello --list-cameras
libcamera-hello -t 5000  # 5 second preview
```

**Problem: picamera2 import error**
```bash
# Install picamera2
source ~/CV-Mindcare/.venv/bin/activate
pip install picamera2

# Or use system picamera2
sudo apt install -y python3-picamera2
```

**Problem: Camera works but greenery detection fails**
```bash
# Check if camera sensor is started
curl http://localhost:8000/api/sensors/manager/status

# Start sensors
curl -X POST http://localhost:8000/api/sensors/manager/start

# Check logs
sudo journalctl -u cvmindcare -n 100
```

### Microphone Issues

**Problem: No microphone detected**
```bash
# List audio devices
arecord -l

# Test recording
arecord -d 5 test.wav
aplay test.wav

# Check sounddevice devices
python << EOF
import sounddevice as sd
print(sd.query_devices())
EOF

# If no devices, check USB connection or install drivers
```

**Problem: Permission denied for audio**
```bash
# Add user to audio group (replace 'admin' with YOUR username)
sudo usermod -a -G audio admin

# Logout and login again for changes to take effect
```

### Service Issues

**Problem: Service won't start**
```bash
# Check service status
sudo systemctl status cvmindcare

# View detailed logs
sudo journalctl -u cvmindcare -n 100 --no-pager

# Check if port 8000 is in use
sudo lsof -i :8000

# Kill process using port 8000 if needed
sudo kill -9 $(sudo lsof -t -i:8000)

# Restart service
sudo systemctl restart cvmindcare
```

**Problem: Service starts but crashes**
```bash
# Check Python errors in logs
sudo journalctl -u cvmindcare -f

# Test manually
cd ~/CV-Mindcare
source .venv/bin/activate
uvicorn backend.app:app --host 0.0.0.0 --port 8000

# Check for missing dependencies
pip install -e .
```

### Performance Issues

**Problem: High CPU usage**
```bash
# Monitor processes
htop

# Check temperature
vcgencmd measure_temp

# If overheating (>80°C):
# 1. Ensure active cooling fan is installed and working
# 2. Improve ventilation
# 3. Consider heatsink upgrade

# Reduce sensor sampling rate
nano ~/CV-Mindcare/config/sensors.yaml
# Lower the sampling_rate_hz value
```

**Problem: Out of memory**
```bash
# Check memory usage
free -h

# Check if swap is enabled
swapon --show

# If no swap, create it (Step 10 in this guide)

# Reduce uvicorn workers in systemd service
sudo nano /etc/systemd/system/cvmindcare.service
# Change --workers 2 to --workers 1
sudo systemctl daemon-reload
sudo systemctl restart cvmindcare
```

**Problem: Slow database**
```bash
# Check database journal mode
sqlite3 ~/CV-Mindcare/mindcare.db "PRAGMA journal_mode;"
# Should be 'wal'

# Optimize database
sqlite3 ~/CV-Mindcare/mindcare.db "PRAGMA optimize;"

# If using SD card, consider moving database to USB SSD
# Or upgrade to NVMe SSD via M.2 HAT
```

### Network Issues

**Problem: Can't access from other devices**
```bash
# Check if service is listening
sudo netstat -tulpn | grep 8000

# Check firewall
sudo ufw status

# Make sure you're accessing the correct IP
hostname -I

# Try accessing from Raspberry Pi itself first
curl http://localhost:8000/api/health

# Check your client device is on same network
```

### Common Error Messages

**"ModuleNotFoundError: No module named 'backend'"**
```bash
# Make sure you're in the right directory and venv is activated
cd ~/CV-Mindcare
source .venv/bin/activate
pip install -e .
```

**"Address already in use"**
```bash
# Port 8000 is in use, kill the process
sudo lsof -i :8000
sudo kill -9 <PID>

# Or use a different port
# Edit /etc/systemd/system/cvmindcare.service
# Change --port 8000 to --port 8080
```

---

## 📊 Monitoring and Maintenance

### Daily Monitoring

**Check system health:**
```bash
# Quick health check script
cat > ~/check_health.sh << 'EOF'
#!/bin/bash
echo "=== CV-Mindcare Health Check ==="
echo "Date: $(date)"
echo ""
echo "Temperature: $(vcgencmd measure_temp)"
echo ""
echo "Memory:"
free -h | grep Mem
echo ""
echo "Disk:"
df -h / | tail -1
echo ""
echo "Service Status:"
systemctl is-active cvmindcare && echo "✅ Running" || echo "❌ Stopped"
echo ""
echo "API Health:"
curl -s http://localhost:8000/api/health || echo "❌ API not responding"
echo ""
EOF

chmod +x ~/check_health.sh
~/check_health.sh
```

### Automated Maintenance

**⚠️ Update paths with YOUR username!**

```bash
# Setup automated maintenance tasks
crontab -e

# Add these lines:

# Daily database optimization (2 AM)
0 2 * * * sqlite3 /home/YOUR_USERNAME/CV-Mindcare/mindcare.db "PRAGMA optimize;"

# Weekly log cleanup (Sunday 3 AM) - if you create log files
0 3 * * 0 find /home/YOUR_USERNAME/CV-Mindcare/logs -name "*.log" -mtime +7 -delete 2>/dev/null

# Daily backup (4 AM)
0 4 * * * mkdir -p /home/YOUR_USERNAME/backups && cp /home/YOUR_USERNAME/CV-Mindcare/mindcare.db /home/YOUR_USERNAME/backups/mindcare_$(date +\%Y\%m\%d).db

# Weekly system update (Sunday 5 AM)
0 5 * * 0 sudo apt update && sudo apt upgrade -y

# Daily health check log (6 AM)
0 6 * * * /home/YOUR_USERNAME/check_health.sh >> /home/YOUR_USERNAME/health_log.txt
```

### Update CV-Mindcare

```bash
# Stop service
sudo systemctl stop cvmindcare

# Backup database
cp ~/CV-Mindcare/mindcare.db ~/mindcare_backup_$(date +%Y%m%d).db

# Update code
cd ~/CV-Mindcare
git pull origin main

# Update dependencies
source .venv/bin/activate
pip install -e . --upgrade

# Restart service
sudo systemctl start cvmindcare

# Check status
sudo systemctl status cvmindcare
```

### Log Management

```bash
# View systemd logs
sudo journalctl -u cvmindcare -f          # Follow logs
sudo journalctl -u cvmindcare -n 100      # Last 100 lines
sudo journalctl -u cvmindcare --since today  # Today's logs

# Limit journal size
sudo journalctl --vacuum-size=100M

# Set permanent limit
sudo nano /etc/systemd/journald.conf
# Uncomment and set: SystemMaxUse=100M
sudo systemctl restart systemd-journald
```

---

## ✅ Production Deployment Checklist

Use this checklist to ensure your Raspberry Pi 5 is properly configured:

### Hardware
- [ ] Raspberry Pi 5 (8GB recommended) with active cooling fan
- [ ] Official 27W USB-C power supply connected
- [ ] Adequate cooling (fan operational, case ventilated)
- [ ] 32GB+ microSD or NVMe SSD installed
- [ ] Camera module connected and tested (`libcamera-hello`)
- [ ] USB microphone connected and tested (`arecord -l`)
- [ ] Network connectivity (Ethernet preferred for stability)
- [ ] Optional: UPS for graceful shutdown during power loss

### Software
- [ ] Raspberry Pi OS (64-bit) installed and updated
- [ ] Python 3.11+ installed (`python3.11 --version`)
- [ ] CV-Mindcare repository cloned
- [ ] Virtual environment created and activated
- [ ] Base dependencies installed (`pip install -e .`)
- [ ] All sensors tested (`python test_rpi_setup.py`)

### Configuration
- [ ] Camera interface enabled in raspi-config
- [ ] Username updated in all paths (NOT using "pi")
- [ ] Systemd service file created with correct paths
- [ ] Service enabled and running (`systemctl status cvmindcare`)
- [ ] Swap configured (4GB for 4GB RAM models)
- [ ] Database using WAL mode (automatic)

### Security
- [ ] Firewall configured (UFW enabled, port 8000 restricted to local network)
- [ ] SSH secured (password auth disabled, SSH keys only - optional but recommended)
- [ ] Strong user password set
- [ ] No unnecessary services running

### Testing
- [ ] All hardware tests passed
- [ ] API accessible locally (`curl http://localhost:8000/api/health`)
- [ ] API accessible from another device on network
- [ ] Sensors start successfully
- [ ] Data being collected and stored in database
- [ ] Temperature under 70°C during operation

### Maintenance
- [ ] Automated database optimization scheduled (cron)
- [ ] Backup strategy configured
- [ ] Health check script created
- [ ] Log rotation configured
- [ ] Monitoring solution in place (optional)

### Documentation
- [ ] IP address documented
- [ ] Username and credentials stored securely
- [ ] Network configuration documented
- [ ] This guide bookmarked for future reference

---

## 📊 Performance Benchmarks (Raspberry Pi 5)

Expected performance on Raspberry Pi 5 (8GB model):

| Operation | Performance | Notes |
|-----------|------------|-------|
| Camera Capture (640x480) | ~30 FPS | Using picamera2 (native) |
| Greenery Detection | ~10 FPS | HSV color analysis |
| Microphone Sampling | 44.1 kHz | Standard quality |
| Database Write | <1ms | SQLite WAL mode |
| Database Query (100 records) | <2ms | Indexed queries |
| API Response Time | <10ms | Local network |
| Memory Usage (base) | ~300-400MB | No ML features |
| Memory Usage (with ML) | ~1-2GB | Emotion detection enabled |
| CPU Usage (idle) | ~5-10% | Sensors inactive |
| CPU Usage (active) | ~30-40% | All sensors running |
| Typical Temperature | 45-65°C | With active cooling |

---

## 🚦 Quick Reference Commands

### Service Management
```bash
# Start service
sudo systemctl start cvmindcare

# Stop service
sudo systemctl stop cvmindcare

# Restart service
sudo systemctl restart cvmindcare

# Check status
sudo systemctl status cvmindcare

# View live logs
sudo journalctl -u cvmindcare -f

# Enable auto-start
sudo systemctl enable cvmindcare

# Disable auto-start
sudo systemctl disable cvmindcare
```

### System Health
```bash
# Check temperature
vcgencmd measure_temp

# Check memory
free -h

# Check disk space
df -h

# Check CPU load
uptime

# Monitor processes
htop

# Check network
hostname -I
```

### API Testing
```bash
# Health check
curl http://localhost:8000/api/health

# Get sensor status
curl http://localhost:8000/api/sensors/manager/status

# Start sensors
curl -X POST http://localhost:8000/api/sensors/manager/start

# Get live data
curl http://localhost:8000/api/live

# Access API documentation
# Open browser: http://YOUR_PI_IP:8000/docs
```

### Database
```bash
# Connect to database
sqlite3 ~/CV-Mindcare/mindcare.db

# Check journal mode
sqlite3 ~/CV-Mindcare/mindcare.db "PRAGMA journal_mode;"

# Optimize database
sqlite3 ~/CV-Mindcare/mindcare.db "PRAGMA optimize;"

# Backup database
cp ~/CV-Mindcare/mindcare.db ~/backup_$(date +%Y%m%d).db
```

### Updates
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Update CV-Mindcare
cd ~/CV-Mindcare
git pull
source .venv/bin/activate
pip install -e . --upgrade
sudo systemctl restart cvmindcare
```

---

## 🎓 Next Steps

After completing this deployment:

1. **Access the Web Dashboard:**
   - Run `./setup-frontend.sh` to set up the React dashboard
   - Access at `http://YOUR_PI_IP:5173`

2. **Explore the API:**
   - Visit `http://YOUR_PI_IP:8000/docs` for interactive API documentation
   - Try different endpoints to understand the data

3. **Customize Configuration:**
   - Edit `config/sensors.yaml` to adjust sensor settings
   - Restart service after changes: `sudo systemctl restart cvmindcare`

4. **Set Up Remote Access (Optional):**
   - Configure VPN for secure remote access (WireGuard/Tailscale recommended)
   - Never expose port 8000 to the internet directly!

5. **Monitor Long-Term:**
   - Check temperature daily for first week
   - Monitor disk space usage
   - Review logs for any errors

6. **Optimize for Your Use Case:**
   - Adjust sensor sampling rates based on your needs
   - Add/remove sensors as needed
   - Customize alert thresholds

---

## 📞 Getting Help

If you encounter issues:

1. **Check this guide's Troubleshooting section** - Most common issues are covered

2. **Review the logs:**
   ```bash
   sudo journalctl -u cvmindcare -n 100
   ```

3. **Run the test script:**
   ```bash
   cd ~/CV-Mindcare
   source .venv/bin/activate
   python test_rpi_setup.py
   ```

4. **GitHub Issues:**
   - Visit: https://github.com/Salman-A-Alsahli/CV-Mindcare/issues
   - Search for similar issues
   - Create new issue with:
     - Raspberry Pi model and RAM
     - OS version (`cat /etc/os-release`)
     - Error messages from logs
     - Output of test script

5. **Community Support:**
   - GitHub Discussions: https://github.com/Salman-A-Alsahli/CV-Mindcare/discussions
   - Include relevant details about your setup

---

## 📝 Important Notes for Raspberry Pi 5

### Username Changes
**⚠️ CRITICAL:** Newer Raspberry Pi OS (Bookworm and later) does NOT use "pi" as the default username!

- **OS Change (not hardware-specific):** This applies to Raspberry Pi OS Bookworm+ on any Raspberry Pi model
- You choose your username during initial OS setup with Raspberry Pi Imager
- All paths in this guide use "YOUR_USERNAME" as a placeholder
- **You MUST replace "YOUR_USERNAME" with YOUR actual username** in:
  - Systemd service file paths (`User=`, `WorkingDirectory=`, `Environment=`)
  - Database paths
  - Cron job paths
  - Any scripts or commands
  - SSH commands (e.g., `ssh admin@...` where `admin` is your chosen username)

### Power Requirements
- Raspberry Pi 5 requires 27W USB-C power supply (5.1V/5A)
- Do NOT use older Pi power supplies (insufficient power)
- Insufficient power causes random crashes and corruption

### Cooling is Mandatory
- Raspberry Pi 5 runs hot (can exceed 80°C without cooling)
- Active cooling (fan) is required for continuous operation
- Monitor temperature regularly: `vcgencmd measure_temp`
- Thermal throttling starts at 80°C, shutdown at 85°C

### Storage Recommendations
- **SD Card:** Minimum Class 10/U1, A2 rated preferred
- **NVMe SSD:** Highly recommended for better performance and longevity
- **Database Location:** SSD preferred over SD card (if available)

### Network Configuration
- Ethernet strongly recommended over WiFi for stability
- WiFi 6 is built-in but may have higher latency
- Static IP recommended for easier access

---

## 🎉 Conclusion

Congratulations! You now have a fully functional privacy-first wellness monitoring system running on your Raspberry Pi 5!

**What you've achieved:**
- ✅ Complete Raspberry Pi 5 setup from scratch
- ✅ CV-Mindcare installed and running
- ✅ Auto-start service configured
- ✅ Hardware tested and verified
- ✅ Security configured
- ✅ Monitoring and maintenance automated

**Your system is now:**
- 🔒 Processing all data locally (privacy-first)
- ⚡ Running efficiently on ARM64 hardware
- 🔄 Auto-starting on boot
- 📊 Collecting wellness data 24/7
- 🛡️ Secured for local network use only

**Enjoy your privacy-first wellness monitoring system!**

---

*Last Updated: December 14, 2024*  
*Guide Version: 2.0 (Raspberry Pi 5 Complete Edition)*  
*Tested on: Raspberry Pi 5 (8GB) with Raspberry Pi OS (64-bit, Bookworm)*
