# Installation Guide

Complete installation instructions for CV-Mindcare on all platforms.

## System Requirements

### Minimum Requirements
- Python 3.9 or higher
- 4GB RAM
- 2GB free disk space
- Internet connection (for initial setup)

### Recommended Requirements
- Python 3.11+
- 8GB RAM
- 10GB free disk space
- Camera and microphone (optional - works with mock data)
- MQ-135 air quality sensor (optional)

### Supported Platforms
- ✅ Linux (Ubuntu 20.04+, Debian 11+)
- ✅ macOS (10.15+)
- ✅ Windows 10/11
- ✅ Raspberry Pi OS (Raspberry Pi 4/5)

## Installation Methods

### Method 1: pip install (Recommended)

```bash
# Clone repository
git clone https://github.com/Salman-A-Alsahli/CV-Mindcare.git
cd CV-Mindcare

# Install with all features
pip install -e .[dev,ml]

# Or install specific feature sets:
pip install -e .              # Base only
pip install -e .[ml]          # With ML features
pip install -e .[dev]         # With development tools
pip install -e .[rpi]         # Raspberry Pi optimized
```

### Method 2: Legacy requirements.txt (Deprecated)

```bash
# Base installation
pip install -r requirements-base.txt

# Add ML features
pip install -r requirements-ml.txt

# Add development tools
pip install -r requirements-dev.txt
```

Note: This method is deprecated. Please use `pyproject.toml` installation.

### Method 3: Docker (Coming Soon)

```bash
docker pull cvmindcare/cv-mindcare:latest
docker run -p 8000:8000 -p 5173:5173 cvmindcare/cv-mindcare
```

## Platform-Specific Instructions

### Ubuntu/Debian

```bash
# Install system dependencies
sudo apt update
sudo apt install python3-pip python3-venv git

# Install audio libraries (for microphone sensor)
sudo apt install portaudio19-dev python3-pyaudio

# Install camera libraries (for camera sensor)
sudo apt install libopencv-dev python3-opencv

# Clone and install
git clone https://github.com/Salman-A-Alsahli/CV-Mindcare.git
cd CV-Mindcare
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev,ml]
```

### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Install audio libraries
brew install portaudio

# Clone and install
git clone https://github.com/Salman-A-Alsahli/CV-Mindcare.git
cd CV-Mindcare
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev,ml]
```

### Windows

```powershell
# Install Python from python.org (if not installed)
# Download: https://www.python.org/downloads/

# Clone repository
git clone https://github.com/Salman-A-Alsahli/CV-Mindcare.git
cd CV-Mindcare

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install
pip install -e .[dev,ml]
```

### Raspberry Pi

See [Raspberry Pi Deployment Guide](../deployment/raspberry-pi.md) for detailed instructions.

## Verification

After installation, verify everything is working:

```bash
# Check Python version
python --version  # Should be 3.9+

# Check installation
python -c "import backend; print('Backend OK')"
python -c "import frontend; print('Frontend OK')" 2>/dev/null || echo "Frontend: npm install required"

# Run tests
pytest tests/ -v

# Start backend
uvicorn backend.app:app --reload
```

Access http://localhost:8000/docs to see the API documentation.

## Troubleshooting

### Common Issues

**Import errors**
```bash
# Reinstall dependencies
pip install -e .[dev,ml] --force-reinstall
```

**Port already in use**
```bash
# Use different port
export CVMINDCARE_API_SERVER_PORT=9000
uvicorn backend.app:app --port 9000
```

**Camera not detected**
```bash
# Check camera devices (Linux)
ls /dev/video*

# Test camera
python -c "from backend.sensors.camera_sensor import check_camera_available; print(check_camera_available())"
```

**Microphone not detected**
```bash
# List audio devices
python -c "from backend.sensors.microphone_sensor import list_audio_devices; list_audio_devices()"
```

### Getting Help

- �� [Quick Start Guide](quick-start.md)
- 🔧 [Hardware Setup](hardware-setup.md)
- 🐛 [GitHub Issues](https://github.com/Salman-A-Alsahli/CV-Mindcare/issues)

## Next Steps

- [Hardware Setup Guide](hardware-setup.md) - Configure sensors
- [Web Dashboard Guide](../user-guide/web-dashboard.md) - Learn the interface
- [Development Guide](../development/contributing.md) - Start contributing
