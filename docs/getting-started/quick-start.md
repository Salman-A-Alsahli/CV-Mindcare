# Quick Start Guide

Get CV-Mindcare up and running in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- Git
- (Optional) Camera and microphone for real sensor data

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Salman-A-Alsahli/CV-Mindcare.git
cd CV-Mindcare
```

### 2. Install Dependencies

**Option A: Base Installation (Recommended for Quick Start - ~2 minutes)**
```bash
pip install -e .
```

This installs all core features:
- ✅ Camera greenery detection
- ✅ Noise analysis  
- ✅ Air quality monitoring
- ✅ Web dashboard
- ✅ Real-time analytics

**Option B: With Optional ML Features (emotion detection - requires ~40 minutes)**
```bash
pip install -e .[ml]
```

**Option C: Development Tools**
```bash
pip install -e .[dev]
```

**Option D: Everything (ML + Development)**
```bash
pip install -e .[dev,ml]
```

### 3. Start the Application

**Web Dashboard (Recommended)**
```bash
# Setup frontend (one-time)
./setup-frontend.sh

# Start both backend and dashboard
./start-dashboard.sh

# Open your browser to:
# - Backend API: http://localhost:8000
# - Dashboard: http://localhost:5173
```

**Desktop GUI**
```bash
python launcher/main.py
```

**API Only**
```bash
uvicorn backend.app:app --reload
# Access API docs at http://localhost:8000/docs
```

## First Steps

### 1. Check Sensor Status
```bash
curl http://localhost:8000/api/sensors
```

### 2. Start Sensors
```bash
curl -X POST http://localhost:8000/api/sensors/manager/start
```

### 3. Get Live Data
```bash
curl http://localhost:8000/api/live
```

**Tip**: For better readability, pipe curl output through `jq`:
```bash
curl http://localhost:8000/api/sensors/manager/status | jq
```

Or add a newline to separate output from the prompt:
```bash
curl -w '\n' http://localhost:8000/api/sensors/manager/start
```

## What's Next?

- 📖 [Installation Guide](installation.md) - Detailed setup instructions
- 🔧 [Hardware Setup](hardware-setup.md) - Configure camera, mic, and MQ-135
- 📊 [Web Dashboard Guide](../user-guide/web-dashboard.md) - Learn the interface
- 🛠️ [Development Guide](../development/contributing.md) - Start contributing

## Troubleshooting

**Sensors not working?**
- Don't worry! CV-Mindcare works in mock mode without hardware
- Check sensor status: `curl http://localhost:8000/api/sensors/manager/status`

**Port already in use?**
- Change port in `config/api.yaml` or use environment variable:
  ```bash
  export CVMINDCARE_API_SERVER_PORT=9000
  ```

**Need help?**
- Check [GitHub Issues](https://github.com/Salman-A-Alsahli/CV-Mindcare/issues)
- See [full documentation](../README.md)
