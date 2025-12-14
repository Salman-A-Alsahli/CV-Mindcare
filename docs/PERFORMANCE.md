# Performance Optimization Guide

Complete guide to optimizing CV-Mindcare for production deployment, with special focus on Raspberry Pi.

---

## Table of Contents

1. [Database Optimization](#database-optimization)
2. [Sensor Polling Configuration](#sensor-polling-configuration)
3. [Memory Management](#memory-management)
4. [CPU Optimization](#cpu-optimization)
5. [Raspberry Pi Specific](#raspberry-pi-specific)
6. [Network Performance](#network-performance)
7. [Benchmarking](#benchmarking)

---

## Database Optimization

### Enable WAL Mode

Write-Ahead Logging (WAL) improves concurrency and performance:

```python
import sqlite3

conn = sqlite3.connect('backend/cv_mindcare.db')
conn.execute('PRAGMA journal_mode=WAL')
conn.execute('PRAGMA synchronous=NORMAL')
conn.execute('PRAGMA cache_size=10000')  # 10MB cache
conn.execute('PRAGMA temp_store=MEMORY')
conn.close()
```

### Automatic Cleanup

Schedule old data deletion to keep database small:

```python
from backend.database import get_db_connection
from datetime import datetime, timedelta

def cleanup_old_data(days_to_keep=30):
    """Delete sensor data older than specified days."""
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Delete old sensor data
    cursor.execute(
        "DELETE FROM sensor_data WHERE timestamp < ?",
        (cutoff_date.isoformat(),)
    )
    
    # Delete old air quality data
    cursor.execute(
        "DELETE FROM air_quality WHERE timestamp < ?",
        (cutoff_date.isoformat(),)
    )
    
    conn.commit()
    conn.close()
    
    print(f"Deleted data older than {days_to_keep} days")

# Run daily via cron or systemd timer
# 0 2 * * * python -c "from cleanup import cleanup_old_data; cleanup_old_data(30)"
```

### Database Vacuum

Reclaim space after deletions:

```bash
# Manual vacuum
sqlite3 backend/cv_mindcare.db "VACUUM;"

# Enable auto-vacuum
sqlite3 backend/cv_mindcare.db "PRAGMA auto_vacuum = FULL; VACUUM;"
```

### Indexes

Ensure all important indexes exist:

```sql
-- Sensor data indexes
CREATE INDEX IF NOT EXISTS idx_sensor_timestamp ON sensor_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_type ON sensor_data(sensor_type);
CREATE INDEX IF NOT EXISTS idx_sensor_type_time ON sensor_data(sensor_type, timestamp);

-- Air quality indexes
CREATE INDEX IF NOT EXISTS idx_air_quality_timestamp ON air_quality(timestamp);
CREATE INDEX IF NOT EXISTS idx_air_quality_level ON air_quality(air_quality_level);

-- Face detection indexes
CREATE INDEX IF NOT EXISTS idx_face_timestamp ON face_detection(timestamp);

-- Sound analysis indexes
CREATE INDEX IF NOT EXISTS idx_sound_timestamp ON sound_analysis(timestamp);
```

---

## Sensor Polling Configuration

### Optimal Intervals

Balance between data freshness and resource usage:

```python
config = {
    # General polling interval (seconds)
    "polling_interval": 5.0,  # Default: 5s
    
    # Per-sensor configuration
    "camera": {
        "enabled": True,
        "resolution": (640, 480),  # Lower for Raspberry Pi
        "fps": 10,  # Capture rate
    },
    
    "microphone": {
        "enabled": True,
        "duration": 1.0,  # Recording duration
        "sample_rate": 44100,  # Can reduce to 22050 for lower CPU
    },
    
    "air_quality": {
        "enabled": True,
        "warmup_time": 60,  # MQ-135 warmup time
    }
}
```

### Adaptive Polling

Adjust polling based on system load:

```python
import psutil

def get_adaptive_interval():
    """Adjust polling interval based on CPU usage."""
    cpu_percent = psutil.cpu_percent(interval=1)
    
    if cpu_percent > 80:
        return 10.0  # Slow down
    elif cpu_percent > 50:
        return 7.0
    else:
        return 5.0  # Normal

# Update sensor manager config dynamically
from backend.sensors.sensor_manager import SensorManager

manager = SensorManager()
manager.update_config({"polling_interval": get_adaptive_interval()})
```

---

## Memory Management

### Monitor Memory Usage

```python
import psutil
import logging

logger = logging.getLogger(__name__)

def log_memory_usage():
    """Log current memory usage."""
    mem = psutil.virtual_memory()
    logger.info(f"Memory: {mem.percent}% used ({mem.used / 1024**3:.2f} GB / {mem.total / 1024**3:.2f} GB)")
    
    if mem.percent > 85:
        logger.warning("High memory usage detected!")
        
# Call periodically
import schedule
schedule.every(5).minutes.do(log_memory_usage)
```

### Limit In-Memory Buffers

```python
# In sensor manager
class SensorManager:
    MAX_BUFFER_SIZE = 100  # Keep only last 100 readings in memory
    
    def __init__(self):
        self._data_buffer = []
    
    def add_reading(self, reading):
        self._data_buffer.append(reading)
        
        # Trim buffer if too large
        if len(self._data_buffer) > self.MAX_BUFFER_SIZE:
            self._data_buffer = self._data_buffer[-self.MAX_BUFFER_SIZE:]
```

### Garbage Collection

```python
import gc

# Force garbage collection periodically
def cleanup_memory():
    gc.collect()
    logger.info("Garbage collection completed")

# Run every hour
schedule.every(1).hours.do(cleanup_memory)
```

---

## CPU Optimization

### Multiprocessing for Heavy Tasks

```python
from multiprocessing import Pool
import numpy as np

def process_camera_frame(frame):
    """Process camera frame in separate process."""
    # Heavy image processing here
    return analyzed_data

# Use process pool
with Pool(processes=2) as pool:
    results = pool.map(process_camera_frame, frames)
```

### Reduce Image Resolution

For Raspberry Pi:

```python
config = {
    "camera": {
        "resolution": (640, 480),  # Instead of (1920, 1080)
        "downscale": True,
    }
}
```

### Optimize NumPy Operations

```python
# Use in-place operations
import numpy as np

# Bad: Creates new array
result = array * 2

# Good: Modifies in place
array *= 2

# Use NumPy's optimized functions
mean = np.mean(array)  # Instead of manual calculation
```

---

## Raspberry Pi Specific

### System Configuration

```bash
# /boot/config.txt optimizations

# Increase GPU memory for camera
gpu_mem=128

# Overclock (Pi 4/5 only, use with cooling)
over_voltage=2
arm_freq=1800

# Disable unnecessary features
dtparam=audio=off  # If not using audio through GPIO
```

### Service Configuration

Create systemd service with resource limits:

```ini
# /etc/systemd/system/cv-mindcare.service
[Unit]
Description=CV-Mindcare Wellness Monitor
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/CV-Mindcare
ExecStart=/home/YOUR_USERNAME/CV-Mindcare/.venv/bin/uvicorn backend.app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

# Resource limits
CPUQuota=80%
MemoryLimit=1G
MemoryHigh=800M

# Environment
Environment="PYTHONUNBUFFERED=1"
Environment="LOG_LEVEL=INFO"

[Install]
WantedBy=multi-user.target
```

### Temperature Monitoring

```python
import subprocess

def get_cpu_temperature():
    """Get Raspberry Pi CPU temperature."""
    try:
        temp = subprocess.check_output(['vcgencmd', 'measure_temp'])
        temp = float(temp.decode('utf-8').split('=')[1].split("'")[0])
        return temp
    except:
        return None

def check_thermal_throttling():
    """Check if Pi is thermally throttled."""
    temp = get_cpu_temperature()
    
    if temp and temp > 80:
        logger.warning(f"High CPU temperature: {temp}°C")
        # Reduce sensor polling
        return True
    
    return False
```

### Use Lite OS

```bash
# Install Raspberry Pi OS Lite (no GUI)
# Download from: https://www.raspberrypi.com/software/operating-systems/

# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
sudo systemctl disable triggerhappy
```

---

## Network Performance

### WebSocket Throttling

Limit broadcast frequency:

```python
class ConnectionManager:
    def __init__(self, throttle_ms=100):
        self.throttle_ms = throttle_ms
        self._last_broadcast = 0
    
    async def broadcast_throttled(self, message):
        """Broadcast with rate limiting."""
        now = time.time() * 1000
        
        if now - self._last_broadcast < self.throttle_ms:
            return  # Skip this broadcast
        
        await self.broadcast(message)
        self._last_broadcast = now
```

### Gzip Compression

Enable for API responses:

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### Connection Pooling

```python
import httpx

# Reuse HTTP connections
client = httpx.AsyncClient(
    timeout=30.0,
    limits=httpx.Limits(max_connections=10)
)
```

---

## Benchmarking

### Performance Test Script

```python
import time
import statistics
from typing import List

def benchmark_sensor_reading(sensor, iterations=100) -> dict:
    """Benchmark sensor reading performance."""
    times: List[float] = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        sensor.read()
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)  # Convert to ms
    
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
        "min": min(times),
        "max": max(times),
        "iterations": iterations
    }

# Run benchmarks
from backend.sensors.camera_sensor import CameraSensor
from backend.sensors.microphone_sensor import MicrophoneSensor

camera = CameraSensor()
camera.start()

results = benchmark_sensor_reading(camera, iterations=50)
print(f"Camera sensor: {results['mean']:.2f}ms ± {results['stdev']:.2f}ms")

camera.stop()
```

### System Metrics

```python
import psutil
import time

def collect_system_metrics(duration_seconds=60):
    """Collect system metrics over time."""
    metrics = {
        "cpu": [],
        "memory": [],
        "temperature": []
    }
    
    start = time.time()
    while time.time() - start < duration_seconds:
        metrics["cpu"].append(psutil.cpu_percent(interval=1))
        metrics["memory"].append(psutil.virtual_memory().percent)
        
        # Raspberry Pi only
        try:
            temp = get_cpu_temperature()
            if temp:
                metrics["temperature"].append(temp)
        except:
            pass
        
        time.sleep(1)
    
    return {
        key: {
            "mean": statistics.mean(values),
            "max": max(values),
            "min": min(values)
        }
        for key, values in metrics.items() if values
    }

# Run and report
metrics = collect_system_metrics(60)
print(f"CPU: {metrics['cpu']['mean']:.1f}% (max: {metrics['cpu']['max']:.1f}%)")
print(f"Memory: {metrics['memory']['mean']:.1f}% (max: {metrics['memory']['max']:.1f}%)")
```

---

## Performance Targets

### Raspberry Pi 5

- **CPU Usage**: < 50% average
- **Memory Usage**: < 1GB
- **Temperature**: < 70°C
- **Sensor Read Time**: < 100ms
- **API Response Time**: < 50ms
- **WebSocket Latency**: < 100ms

### Desktop/Server

- **CPU Usage**: < 25% average
- **Memory Usage**: < 500MB
- **Sensor Read Time**: < 50ms
- **API Response Time**: < 20ms
- **WebSocket Latency**: < 50ms

---

## Monitoring Tools

```bash
# CPU and memory
htop

# Temperature (Raspberry Pi)
watch -n 1 vcgencmd measure_temp

# Network
iftop

# Disk I/O
iotop

# Process monitoring
pidstat 1

# System load
uptime
```

---

## Production Checklist

- [ ] Enable WAL mode on database
- [ ] Set up automatic data cleanup
- [ ] Configure optimal sensor polling intervals
- [ ] Set resource limits in systemd service
- [ ] Enable gzip compression
- [ ] Implement WebSocket throttling
- [ ] Set up monitoring and alerting
- [ ] Test under load
- [ ] Benchmark on target hardware
- [ ] Document actual performance metrics

---

**Last Updated**: December 2024  
**Version**: 1.0.0
