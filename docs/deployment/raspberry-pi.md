# CV-Mindcare Raspberry Pi 5 Deployment Guide

**Target Hardware:** Raspberry Pi 5 (ARM64 Architecture)  
**OS:** Raspberry Pi OS (64-bit) / Ubuntu 22.04 ARM64  
**Python:** 3.11+ (native ARM64 support)  
**Generated:** December 9, 2024

---

## 🎯 Executive Summary

CV-Mindcare is designed as a privacy-first, local-processing wellness monitoring system. The Raspberry Pi 5 is an ideal deployment target due to:

- **Local Processing:** All AI/sensor processing happens on-device (privacy-first)
- **GPIO Support:** Direct access to camera (CSI) and microphone (USB/I2S)
- **Performance:** 4-core ARM Cortex-A76 @ 2.4GHz with 4GB/8GB RAM
- **Power Efficiency:** Low power consumption suitable for always-on monitoring
- **Cost-Effective:** ~$60-80 for complete edge computing solution

---

## 🔧 Hardware Requirements

### Minimum Configuration (Raspberry Pi 5)
- **Board:** Raspberry Pi 5 (4GB RAM minimum, 8GB recommended)
- **Storage:** 32GB microSD (Class 10) or NVMe SSD (recommended for database)
- **Camera:** Raspberry Pi Camera Module 3 (12MP, official support)
- **Microphone:** USB microphone or I2S MEMS microphone
- **Power:** Official 27W USB-C power supply (5.1V/5A)
- **Cooling:** Active cooling fan (required for continuous operation)

### Optional Enhancements
- **Display:** 7" touchscreen for local GUI (launcher interface)
- **Case:** Official or third-party case with fan mount
- **Network:** Ethernet connection for stability (WiFi 6 built-in)

### GPIO Pinout Considerations
- **Camera:** CSI connector (direct hardware interface)
- **I2S Microphone:** GPIO 18, 19, 21 (PCM interface)
- **Status LED:** GPIO 17 (system health indicator)

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

## 🚀 Installation for Raspberry Pi 5

### Step 1: Prepare Raspberry Pi OS

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip \
    git libatlas-base-dev libopenblas-dev \
    libcamera-dev python3-libcamera python3-picamera2 \
    alsa-utils pulseaudio libasound2-dev \
    sqlite3 libsqlite3-dev

# Enable camera
sudo raspi-config
# Navigate to: Interface Options -> Camera -> Enable
```

### Step 2: Clone and Setup Project

```bash
# Clone repository
cd /home/pi
git clone https://github.com/Salman-A-Alsahli/CV-Mindcare.git
cd CV-Mindcare

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install base dependencies (optimized for Pi)
pip install -r requirements-base.txt

# For ML features (optional, ~1GB on ARM64)
# pip install -r requirements-ml-rpi.txt  # We'll create this
```

### Step 3: Create Raspberry Pi Optimized ML Requirements

We need a specialized requirements file for Raspberry Pi that uses ARM64-optimized packages.

### Step 4: Configure for Raspberry Pi

```bash
# Create configuration directory
mkdir -p ~/.cvmindcare

# Copy and edit configuration
cat > ~/.cvmindcare/config.json << EOF
{
  "backend": {
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 2
  },
  "sensors": {
    "camera_backend": "picamera2",
    "camera_index": 0,
    "audio_backend": "alsa",
    "sampling_rate_hz": 2,
    "enable_camera": true,
    "enable_microphone": true
  },
  "database": {
    "path": "/home/pi/CV-Mindcare/mindcare.db",
    "wal_mode": true
  },
  "performance": {
    "max_workers": 2,
    "thread_pool_size": 4,
    "async_io": true
  }
}
EOF
```

### Step 5: Setup Systemd Service (Auto-start on Boot)

```bash
# Create systemd service file
sudo nano /etc/systemd/system/cvmindcare.service
```

```ini
[Unit]
Description=CV-Mindcare Wellness Monitoring Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/CV-Mindcare
Environment="PATH=/home/pi/CV-Mindcare/.venv/bin"
ExecStart=/home/pi/CV-Mindcare/.venv/bin/python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable cvmindcare
sudo systemctl start cvmindcare

# Check status
sudo systemctl status cvmindcare
```

---

## 🔍 Performance Optimization for Raspberry Pi 5

### CPU Optimization

```python
# In backend/app.py - add worker configuration
import multiprocessing

# For Raspberry Pi 5 (4 cores)
WORKERS = min(2, multiprocessing.cpu_count())  # Conservative for 4GB RAM
WORKER_CLASS = "uvicorn.workers.UvicornWorker"
```

### Memory Optimization

```bash
# Create swap file (if not exists)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Database Optimization

```python
# In backend/database.py - enable WAL mode
import sqlite3

def init_db():
    conn = sqlite3.connect('mindcare.db')
    conn.execute('PRAGMA journal_mode=WAL')  # Write-Ahead Logging
    conn.execute('PRAGMA synchronous=NORMAL')  # Balance safety/speed
    conn.execute('PRAGMA cache_size=-64000')  # 64MB cache
    conn.execute('PRAGMA temp_store=MEMORY')  # Use RAM for temp tables
    # ... rest of initialization
```

### Camera Optimization (Raspberry Pi Camera)

```python
# Use picamera2 (native Pi support, much faster than OpenCV)
from picamera2 import Picamera2
import numpy as np

class RaspberryPiCamera:
    def __init__(self):
        self.picam = Picamera2()
        # Configure for low resolution (faster processing)
        config = self.picam.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        self.picam.configure(config)
        self.picam.start()
    
    def capture_frame(self):
        # Direct numpy array, no conversion needed
        return self.picam.capture_array()
    
    def __del__(self):
        self.picam.stop()
```

---

## 🧪 Testing on Raspberry Pi 5

### Hardware Test Script

Create a test script to verify all hardware:

```bash
# Create test script
cat > /home/pi/CV-Mindcare/test_rpi_hardware.py << 'EOF'
#!/usr/bin/env python3
"""Test Raspberry Pi 5 Hardware for CV-Mindcare"""

import sys
import subprocess

def test_camera():
    """Test Raspberry Pi camera"""
    try:
        from picamera2 import Picamera2
        picam = Picamera2()
        picam.start()
        frame = picam.capture_array()
        picam.stop()
        print("✅ Camera: OK (Resolution: {})".format(frame.shape))
        return True
    except Exception as e:
        print(f"❌ Camera: FAILED - {e}")
        return False

def test_microphone():
    """Test microphone/audio"""
    try:
        result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
        if 'card' in result.stdout.lower():
            print("✅ Microphone: OK")
            return True
        else:
            print("❌ Microphone: No audio devices found")
            return False
    except Exception as e:
        print(f"❌ Microphone: FAILED - {e}")
        return False

def test_system_resources():
    """Test system resources"""
    try:
        import psutil
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"✅ System Resources:")
        print(f"   - CPU Cores: {cpu_count}")
        print(f"   - RAM: {memory.total / 1024**3:.1f} GB (Available: {memory.available / 1024**3:.1f} GB)")
        print(f"   - Disk: {disk.total / 1024**3:.1f} GB (Free: {disk.free / 1024**3:.1f} GB)")
        return True
    except Exception as e:
        print(f"❌ System Resources: FAILED - {e}")
        return False

def test_database():
    """Test SQLite database"""
    try:
        import sqlite3
        conn = sqlite3.connect(':memory:')
        conn.execute('CREATE TABLE test (id INTEGER)')
        conn.execute('INSERT INTO test VALUES (1)')
        result = conn.execute('SELECT * FROM test').fetchone()
        conn.close()
        print("✅ Database: OK")
        return True
    except Exception as e:
        print(f"❌ Database: FAILED - {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("CV-Mindcare Raspberry Pi 5 Hardware Test")
    print("=" * 50)
    
    tests = [
        test_system_resources(),
        test_database(),
        test_camera(),
        test_microphone(),
    ]
    
    print("=" * 50)
    if all(tests):
        print("✅ All hardware tests PASSED")
        sys.exit(0)
    else:
        print("❌ Some hardware tests FAILED")
        sys.exit(1)
EOF

chmod +x /home/pi/CV-Mindcare/test_rpi_hardware.py
python3 /home/pi/CV-Mindcare/test_rpi_hardware.py
```

---

## 🔒 Security Considerations for Edge Deployment

### Network Security
- **Firewall:** Only open port 8000 for local network
- **No Cloud:** All data stays on-device (privacy-first)
- **HTTPS:** Use self-signed cert for encrypted local access

```bash
# Configure UFW firewall
sudo apt install ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.1.0/24 to any port 8000  # Local network only
sudo ufw enable
```

### Data Security
- **Encryption at Rest:** SQLite with SQLCipher (optional)
- **No Telemetry:** No data transmission to external servers
- **Local Only:** Camera/mic data never leaves device

---

## 📊 Performance Benchmarks (Expected on Raspberry Pi 5)

| Operation | Raspberry Pi 5 (8GB) | Notes |
|-----------|---------------------|-------|
| Camera Capture (640x480) | ~30 FPS | Using picamera2 |
| Greenery Detection | ~10 FPS | HSV color analysis |
| Microphone Sampling | 44.1 kHz | Standard audio quality |
| DB Write (single) | <1ms | SQLite WAL mode |
| DB Query (100 records) | <2ms | Indexed queries |
| API Response | <10ms | Local network |
| Face Detection (TFLite) | ~5 FPS | Lightweight model |
| Memory Usage | ~400MB | Base + sensors |
| CPU Usage (idle) | ~5% | Polling at 2Hz |
| CPU Usage (active) | ~40% | All sensors active |

---

## 🛠️ Troubleshooting

### Issue: Camera Not Detected
```bash
# Check camera connection
vcgencmd get_camera

# Enable camera interface
sudo raspi-config
# Interface Options -> Camera -> Enable

# Reboot
sudo reboot
```

### Issue: High CPU Usage
```python
# Reduce sensor sampling rate in config
"sensors": {
    "sampling_rate_hz": 1  # Lower from 2 to 1
}
```

### Issue: Out of Memory
```bash
# Increase swap size
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile  # Set CONF_SWAPSIZE=4096
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Issue: Slow Database
```bash
# Move database to SSD (if available)
# Or optimize SQLite
sqlite3 mindcare.db "PRAGMA optimize;"
```

---

## 📈 Monitoring and Maintenance

### System Monitoring
```bash
# Check service status
sudo systemctl status cvmindcare

# View logs
journalctl -u cvmindcare -f

# Check resource usage
htop

# Monitor temperature (critical for Pi 5)
vcgencmd measure_temp
```

### Automated Maintenance
```bash
# Create maintenance cron job
crontab -e

# Add these lines:
# Daily database optimization (2 AM)
0 2 * * * sqlite3 /home/pi/CV-Mindcare/mindcare.db "PRAGMA optimize;"

# Weekly log cleanup (Sunday 3 AM)
0 3 * * 0 find /home/pi/CV-Mindcare/logs -name "*.log" -mtime +7 -delete

# Daily backup (4 AM)
0 4 * * * cp /home/pi/CV-Mindcare/mindcare.db /home/pi/backups/mindcare_$(date +\%Y\%m\%d).db
```

---

## 🎯 Production Deployment Checklist

- [ ] Raspberry Pi 5 with adequate cooling (fan required)
- [ ] 8GB RAM model (recommended) or 4GB with swap configured
- [ ] 32GB+ microSD or NVMe SSD for better I/O
- [ ] Official camera module connected and tested
- [ ] USB microphone or I2S MEMS mic configured
- [ ] Network connectivity (Ethernet preferred)
- [ ] Systemd service configured and enabled
- [ ] Firewall rules configured (local network only)
- [ ] Swap file configured (4GB)
- [ ] Hardware tests passed
- [ ] Database initialized with WAL mode
- [ ] Automatic backups configured
- [ ] Monitoring solution in place
- [ ] UPS or clean shutdown mechanism (recommended)

---

## 🚦 Next Steps

1. **Complete Phase 2:** Implement sensor base class with Raspberry Pi optimizations
2. **Create requirements-ml-rpi.txt:** ARM64-optimized ML dependencies
3. **Implement picamera2 backend:** Native camera support for Pi
4. **Add ALSA audio backend:** Optimized microphone capture
5. **Test on actual Raspberry Pi 5:** Validate performance benchmarks
6. **Create deployment script:** One-command Pi setup
7. **Add monitoring dashboard:** System health visualization

---

**Lead Developer Notes:**

This deployment strategy prioritizes:
- **Privacy:** All processing on-device, no cloud dependencies
- **Performance:** ARM64-optimized libraries, efficient resource usage
- **Reliability:** Systemd service, automatic restart, proper error handling
- **Maintainability:** Simple configuration, clear documentation
- **Scalability:** Foundation for multi-Pi deployments (future)

The Raspberry Pi 5 provides an excellent balance of performance, cost, and power efficiency for this privacy-first wellness monitoring application.
