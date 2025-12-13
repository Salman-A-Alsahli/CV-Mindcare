# Troubleshooting Guide

Complete guide to diagnosing and fixing common issues with CV-Mindcare.

---

## Quick Diagnostics

Run this command to check system health:

```bash
python -c "from backend.sensors.camera_sensor import check_camera_available; \
           from backend.sensors.microphone_sensor import check_microphone_available; \
           print(f'Camera: {check_camera_available()}'); \
           print(f'Microphone: {check_microphone_available()}')"
```

---

## Common Issues

### 1. API Server Won't Start

**Symptoms:**
- `ModuleNotFoundError` when starting server
- Port already in use error
- Database errors on startup

**Solutions:**

```bash
# 1. Check dependencies are installed
pip install -e .[dev,ml]

# 2. Check if port 8000 is in use
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# 3. Kill existing process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows

# 4. Use different port
uvicorn backend.app:app --port 8001

# 5. Initialize database manually
python -c "from backend.database import init_db; init_db()"

# 6. Check Python version (requires 3.9+)
python --version
```

---

### 2. Tests Failing

**Symptoms:**
- Import errors
- ModuleNotFoundError for cv2 or sounddevice
- Database locked errors

**Solutions:**

```bash
# 1. Install all test dependencies
pip install -e .[dev,ml]

# 2. Install specific missing packages
pip install opencv-python sounddevice

# 3. Clean pytest cache
rm -rf .pytest_cache __pycache__ */__pycache__
pytest --cache-clear

# 4. Run with verbose output
pytest -vv --tb=short

# 5. Run specific test file
pytest tests/unit/test_camera_sensor.py -v

# 6. Check for database locks
rm backend/cv_mindcare.db
python -c "from backend.database import init_db; init_db()"
```

---

### 3. Camera Sensor Not Working

**Symptoms:**
- "No camera available" errors
- Camera status shows "UNAVAILABLE"
- OpenCV errors

**Solutions:**

```bash
# 1. Check if OpenCV is installed
python -c "import cv2; print(cv2.__version__)"

# 2. Install OpenCV
pip install opencv-python

# 3. Test camera directly
python -c "import cv2; cap = cv2.VideoCapture(0); \
           print('Camera works!' if cap.isOpened() else 'Camera failed'); \
           cap.release()"

# 4. Check camera permissions (Linux)
ls -l /dev/video*
sudo usermod -a -G video $USER
# Logout and login again

# 5. Use mock mode for development
# In backend/sensors/camera_sensor.py, sensor auto-detects
# and falls back to mock mode if hardware unavailable

# 6. Try different camera index
python -c "import cv2; \
           for i in range(5): \
               cap = cv2.VideoCapture(i); \
               if cap.isOpened(): \
                   print(f'Camera found at index {i}'); \
               cap.release()"
```

---

### 4. Microphone Sensor Not Working

**Symptoms:**
- "No microphone available" errors
- Microphone status shows "UNAVAILABLE"
- sounddevice import errors

**Solutions:**

```bash
# 1. Check if sounddevice is installed
python -c "import sounddevice; print(sounddevice.__version__)"

# 2. Install sounddevice
pip install sounddevice

# 3. List available audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# 4. Test recording
python -c "import sounddevice as sd; import numpy as np; \
           data = sd.rec(int(1 * 44100), samplerate=44100, channels=1); \
           sd.wait(); print('Recording successful!')"

# 5. Check audio permissions (Linux)
groups | grep audio
sudo usermod -a -G audio $USER
# Logout and login again

# 6. Install ALSA libraries (Linux)
sudo apt-get install libasound2-dev portaudio19-dev

# 7. Use mock mode for development
# Sensor automatically falls back to mock mode if hardware unavailable
```

---

### 5. Air Quality Sensor Not Working

**Symptoms:**
- "Sensor not calibrated" warnings
- Invalid PPM readings
- Serial port errors

**Solutions:**

```bash
# 1. Check if running in mock mode
curl http://localhost:8000/api/sensors/air_quality/status

# 2. For hardware setup, check serial connection
ls -l /dev/ttyUSB* /dev/ttyACM*  # Linux
ls -l /dev/tty.*  # macOS

# 3. Install serial library
pip install pyserial

# 4. Check MQ-135 wiring
# See: docs/getting-started/hardware-setup.md

# 5. Calibrate sensor
curl -X POST http://localhost:8000/api/sensors/air_quality/calibrate \
  -H "Content-Type: application/json" \
  -d '{"clean_air_resistance": 10.0}'

# 6. Mock mode works without hardware
# Generates realistic test data automatically
```

---

### 6. WebSocket Connection Issues

**Symptoms:**
- WebSocket connection refused
- Connection drops frequently
- No data received

**Solutions:**

```bash
# 1. Check if API server is running
curl http://localhost:8000/api/health

# 2. Test WebSocket with simple client
python docs/examples/websocket_client.py

# 3. Check firewall settings
sudo ufw allow 8000  # Linux
# Windows: Allow port 8000 in Windows Firewall

# 4. Use correct WebSocket URL
ws://localhost:8000/ws/live  # NOT http://

# 5. Check CORS settings in backend/app.py
# Ensure your origin is in allow_origins list

# 6. Enable WebSocket debugging in browser
# Chrome DevTools -> Network -> WS filter
```

---

### 7. Database Errors

**Symptoms:**
- "Database is locked" errors
- "Table doesn't exist" errors
- Integrity errors

**Solutions:**

```bash
# 1. Stop all running instances
pkill -f "uvicorn backend.app"
pkill -f "python launcher"

# 2. Delete and reinitialize database
rm backend/cv_mindcare.db
python -c "from backend.database import init_db; init_db()"

# 3. Enable WAL mode for better concurrency
python -c "import sqlite3; \
           conn = sqlite3.connect('backend/cv_mindcare.db'); \
           conn.execute('PRAGMA journal_mode=WAL'); \
           conn.close()"

# 4. Check database integrity
sqlite3 backend/cv_mindcare.db "PRAGMA integrity_check;"

# 5. Backup before major changes
cp backend/cv_mindcare.db backend/cv_mindcare.db.backup
```

---

### 8. Frontend Not Loading

**Symptoms:**
- Blank page
- "Cannot connect to backend" errors
- CORS errors in browser console

**Solutions:**

```bash
# 1. Check if backend is running
curl http://localhost:8000/api/health

# 2. Install frontend dependencies
cd frontend
npm install

# 3. Start development server
npm run dev

# 4. Check frontend is accessible
curl http://localhost:5173

# 5. Fix CORS errors
# In backend/app.py, add your frontend URL to allow_origins:
# allow_origins=["http://localhost:5173", ...]

# 6. Clear browser cache
# Chrome: Ctrl+Shift+Delete

# 7. Check for JavaScript errors
# Open Browser DevTools -> Console
```

---

### 9. High Memory Usage

**Symptoms:**
- System becomes slow
- Out of memory errors
- Process killed by OS

**Solutions:**

```bash
# 1. Check memory usage
python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"

# 2. Reduce polling frequency
# In sensor manager config:
curl -X PUT http://localhost:8000/api/sensors/manager/config \
  -H "Content-Type: application/json" \
  -d '{"polling_interval": 10.0}'

# 3. Limit database size
sqlite3 backend/cv_mindcare.db \
  "DELETE FROM sensor_data WHERE timestamp < datetime('now', '-30 days');"

# 4. Enable auto-vacuum
sqlite3 backend/cv_mindcare.db "PRAGMA auto_vacuum = FULL; VACUUM;"

# 5. Monitor with htop
htop  # Linux
Activity Monitor  # macOS
Task Manager  # Windows

# 6. Use production server (uses less memory)
gunicorn backend.app:app -w 2 -k uvicorn.workers.UvicornWorker
```

---

### 10. Raspberry Pi Specific Issues

**Symptoms:**
- Slow performance
- High CPU temperature
- Package installation failures

**Solutions:**

```bash
# 1. Check system resources
vcgencmd measure_temp  # Check temperature
top  # Check CPU/memory usage

# 2. Install Raspberry Pi optimized packages
pip install -e .[rpi]

# 3. Reduce resolution for camera
# In camera config: {"resolution": (640, 480)}

# 4. Enable GPU memory split
sudo raspi-config
# -> Performance Options -> GPU Memory -> Set to 128

# 5. Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon

# 6. Use lighter alternatives
# Use picamera2 instead of opencv on Pi
# Use tflite-runtime instead of full tensorflow

# 7. Add cooling
# Install heatsinks or active cooling fan
# Monitor with: watch -n 1 vcgencmd measure_temp
```

---

## Performance Optimization

### Database Performance

```bash
# Enable WAL mode
python -c "import sqlite3; \
           conn = sqlite3.connect('backend/cv_mindcare.db'); \
           conn.execute('PRAGMA journal_mode=WAL'); \
           conn.execute('PRAGMA synchronous=NORMAL'); \
           conn.execute('PRAGMA cache_size=10000'); \
           conn.close()"

# Add indexes (if not already present)
sqlite3 backend/cv_mindcare.db << EOF
CREATE INDEX IF NOT EXISTS idx_sensor_timestamp ON sensor_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_type ON sensor_data(sensor_type);
CREATE INDEX IF NOT EXISTS idx_air_quality_timestamp ON air_quality(timestamp);
EOF
```

### Sensor Polling Optimization

```python
# Adjust polling intervals based on needs
config = {
    "polling_interval": 5.0,  # Default: 5 seconds
    "camera": {"enabled": True},
    "microphone": {"enabled": True, "duration": 1.0},
    "air_quality": {"enabled": True}
}
```

### Memory Optimization

```bash
# Limit in-memory data
export SENSOR_BUFFER_SIZE=100

# Use database pagination
curl "http://localhost:8000/api/sensors?limit=10&offset=0"
```

---

## Logging & Debugging

### Enable Debug Logging

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Or in Python code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### View Logs

```bash
# Backend logs
uvicorn backend.app:app --log-level debug

# Check system logs
journalctl -u cv-mindcare  # If running as service

# Python logging to file
python backend/app.py 2>&1 | tee cv-mindcare.log
```

---

## Getting Help

If you still have issues:

1. **Check Documentation**: [docs/README.md](README.md)
2. **Search Issues**: [GitHub Issues](https://github.com/Salman-A-Alsahli/CV-Mindcare/issues)
3. **Create Issue**: Include:
   - OS and version
   - Python version
   - Full error message
   - Steps to reproduce
4. **Community**: [GitHub Discussions](https://github.com/Salman-A-Alsahli/CV-Mindcare/discussions)

---

## Quick Reference

### System Requirements

- **Python**: 3.9 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 1GB free space
- **OS**: Linux, macOS, Windows
- **Raspberry Pi**: Pi 4 or Pi 5 recommended

### Essential Commands

```bash
# Install
pip install -e .[dev,ml]

# Test
pytest tests/

# Run API
uvicorn backend.app:app --reload

# Run Frontend
cd frontend && npm run dev

# Run Launcher
python launcher/launcher.py

# Format Code
black backend/ launcher/ tests/

# Lint Code
flake8 backend/ launcher/ tests/
```

---

**Last Updated**: December 2024  
**Version**: 1.0.0
