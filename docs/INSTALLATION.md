# Installation Guide - CV-Mindcare

Welcome to CV-Mindcare! This guide will help you install and set up the system on your Windows computer.

## Table of Contents
- [Prerequisites](#prerequisites)
- [System Requirements](#system-requirements)
- [Installation Steps](#installation-steps)
- [First Run](#first-run)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

## Prerequisites

### Required Software
1. **Python 3.9 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   - Verify installation:
     ```powershell
     python --version
     ```

2. **Git** (optional, for developers)
   - Download from [git-scm.com](https://git-scm.com/)

### Hardware Requirements
- **Webcam** (optional, for face detection and greenery analysis)
- **Microphone** (optional, for sound level monitoring)
- **2+ CPU cores**
- **4GB RAM** minimum
- **1GB free disk space**

## System Requirements

### Minimum Requirements
- Windows 10 or Windows 11
- Python 3.9+
- 2 CPU cores
- 4GB RAM
- 1GB disk space
- Internet connection (for initial setup only)

### Recommended Requirements
- Windows 11
- Python 3.11+
- 4+ CPU cores
- 8GB+ RAM
- 2GB+ disk space
- Webcam and microphone

## Installation Steps

### Method 1: Using Git (Recommended for Developers)

1. **Clone the Repository**
   ```powershell
   cd C:\Users\YourName\Documents
   git clone https://github.com/Salman-A-Alsahli/CV-Mindcare.git
   cd CV-Mindcare
   ```

2. **Create Virtual Environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   
   > **Note**: If you get an execution policy error, run:
   > ```powershell
   > Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   > ```

3. **Install Dependencies**
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
   
   This will install:
   - FastAPI and Uvicorn (backend server)
   - CustomTkinter (GUI framework)
   - OpenCV (camera processing)
   - SoundDevice (audio monitoring)
   - psutil (system monitoring)
   - SQLite (built-in database)
   - Development tools (pytest, black, flake8)

4. **Verify Installation**
   ```powershell
   python -c "import customtkinter, cv2, fastapi, sounddevice; print('All dependencies installed!')"
   ```

### Method 2: Manual Download

1. **Download the Repository**
   - Go to https://github.com/Salman-A-Alsahli/CV-Mindcare
   - Click "Code" → "Download ZIP"
   - Extract to `C:\Users\YourName\Documents\CV-Mindcare`

2. **Follow Steps 2-4 from Method 1 above**

### Method 3: Windows Executable (Coming Soon)
A standalone Windows executable will be available for download that requires no Python installation.

## First Run

### Starting the Launcher

1. **Activate Virtual Environment** (if not already active)
   ```powershell
   cd C:\Users\YourName\Documents\CV-Mindcare
   .\venv\Scripts\Activate.ps1
   ```

2. **Launch the Application**
   ```powershell
   python -m launcher.launcher
   ```
   
   Or simply:
   ```powershell
   python launcher/launcher.py
   ```

### Using the Launcher

1. **System Check**
   - The launcher automatically runs system checks on startup
   - Green checkmarks (✓) indicate passed checks
   - Red crosses (✗) indicate issues that need resolution

2. **Start Dashboard**
   - Once all checks pass, click "Start Dashboard"
   - The backend server will start automatically
   - Your default browser will open the dashboard
   - The launcher window shows system logs

3. **Monitor Your Environment**
   - The dashboard displays:
     - Dominant emotion detected
     - Ambient noise level (dB)
     - Greenery percentage in camera view
     - System resource usage (CPU, memory)
     - Emotion distribution chart

4. **Stop the System**
   - Click "Stop System" in the launcher
   - Or close the launcher window (automatically stops backend)

## Troubleshooting

### Common Issues

#### 1. Camera Not Detected
**Problem**: System check shows "Camera: Not Found"

**Solutions**:
- Check if camera is connected and enabled
- Grant camera permissions:
  - Windows Settings → Privacy → Camera
  - Enable "Let apps access your camera"
- Try different camera index in settings
- Test camera in another app (Camera app)

#### 2. Microphone Not Detected
**Problem**: System check shows "Microphone: Not Found"

**Solutions**:
- Check if microphone is connected
- Grant microphone permissions:
  - Windows Settings → Privacy → Microphone
  - Enable "Let apps access your microphone"
- Test microphone in another app (Voice Recorder)

#### 3. Module Import Errors
**Problem**: `ModuleNotFoundError: No module named 'X'`

**Solutions**:
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or install specific missing package
pip install package-name
```

#### 4. Backend Won't Start
**Problem**: "Failed to start backend" or port already in use

**Solutions**:
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process using the port (replace PID with actual process ID)
taskkill /PID <PID> /F

# Restart the launcher
```

#### 5. Execution Policy Error
**Problem**: Cannot run PowerShell scripts

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 6. Dashboard Not Loading
**Problem**: Browser opens but shows "Cannot connect"

**Solutions**:
- Wait 10-15 seconds for backend to start
- Check launcher logs for errors
- Try accessing http://127.0.0.1:8000 directly
- Check firewall settings (allow Python)

### Getting Help

If you encounter issues:

1. **Check Logs**: The launcher displays system logs in the bottom panel
2. **GitHub Issues**: [Report issues](https://github.com/Salman-A-Alsahli/CV-Mindcare/issues)
3. **Documentation**: Check `docs/` folder for detailed docs

## Uninstallation

### Remove the Application

1. **Stop the Application** (if running)

2. **Delete the Directory**
   ```powershell
   cd ..
   Remove-Item -Recurse -Force CV-Mindcare
   ```

3. **Remove Virtual Environment** (already deleted with directory)

### Keep Your Data

The SQLite database (`backend/cv_mindcare.db`) stores your sensor history. If you want to keep this data:

```powershell
# Backup before uninstalling
copy backend\cv_mindcare.db C:\Users\YourName\Documents\mindcare_backup.db
```

## Next Steps

- Read the [User Guide](USER_GUIDE.md) for detailed usage instructions
- Check [API Documentation](API.md) for developer reference
- See [Development Guide](DEVELOPMENT.md) for contributing
- Review [FAQ](FAQ.md) for frequently asked questions

## Updates

To update to the latest version:

```powershell
cd CV-Mindcare
git pull origin master
pip install -r requirements.txt --upgrade
```

---

**Version**: 0.1.0  
**Last Updated**: October 26, 2025  
**Support**: https://github.com/Salman-A-Alsahli/CV-Mindcare/issues
