# Launcher

This directory contains the desktop launcher application for CV-Mindcare.

## Structure

- `launcher.py` - Main GUI application using customtkinter
- `system_check.py` - System requirements verification module
- `process_manager.py` - Backend process lifecycle management (to be implemented)

## Features

### System Check Tool
The launcher performs comprehensive system checks before starting:

- **Hardware Checks**
  - CPU cores (minimum 2 required)
  - RAM (minimum 4GB required)
  - Disk space (minimum 1GB free)
  - Camera availability
  - Microphone availability

- **Software Checks**
  - Required Python packages installed
  - Dependencies verification

### GUI Components
- Title and branding
- System status display
- Re-run system check button
- Start dashboard button (enabled after successful checks)

## Usage

```bash
# From project root with venv activated
python -m launcher.launcher
```

Or:

```bash
cd launcher
python launcher.py
```

## System Requirements

### Minimum Requirements
- Python 3.9+
- 2+ CPU cores
- 4GB RAM
- 1GB free disk space
- Webcam (optional)
- Microphone (optional)

### Required Packages
- customtkinter - GUI framework
- opencv-python - Camera access
- fastapi - Backend framework
- uvicorn - ASGI server
- sounddevice - Audio capture
- numpy - Numerical operations
- pytest - Testing framework

## Development

### Adding New System Checks
Edit `system_check.py` and add methods to the `SystemChecker` class:

```python
def check_new_requirement(self) -> Tuple[bool, str]:
    # Implementation
    return status, message
```

Then call it from `run_all_checks()`.

### Process Management (TODO)
The `process_manager.py` module will handle:
- Starting the backend server
- Monitoring backend health
- Capturing logs
- Opening the web browser
- Clean shutdown

## Dependencies

- customtkinter - Modern GUI toolkit
- psutil - System monitoring
- opencv-python - Camera checks
- sounddevice - Microphone checks
