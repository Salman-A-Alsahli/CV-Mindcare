# CV Mindcare

CV Mindcare is a privacy-first local utility that observes a few environmental signals (sound level, presence of greenery via camera, and brief facial affect sampling) and provides human-readable observations, trend analysis, and practical suggestions to improve wellbeing in a workspace or room.

This repository now includes a lightweight local database and a context-aware assistant that uses historical data to provide personalized recommendations.

## Architecture

The data flow has been upgraded from a simple pipeline to a context-rich loop that supports long-term personalization:

1. Real-time Sensing
   - The application captures live data: dominant emotion (from face analysis), ambient noise (dB), and greenery percentage from the camera view.

2. Database Logging
   - Each live reading is immediately logged to an on-disk SQLite database (`mindcare.db`) as a historical record.

3. Historical Analysis
   - The system queries recent sessions and computes trends and statistics (most frequent emotions, noisy times of day, correlations between greenery and mood).

4. Context Creation
   - A combined JSON payload is created that merges the `current_readings` with a `historical_summary` describing detected trends.

5. Context-Aware Inference
   - The rich payload is passed to the local assistant, which compares the current reading to historical patterns and returns both immediate advice and longer-term recommendations.

This loop allows the assistant to become more personalized and useful over time as more sessions are logged.

## Project structure

```
CV-Mindcare/
├── backend/              # FastAPI backend server
│   ├── app.py           # Main API application
│   ├── database.py      # SQLite database operations
│   ├── models.py        # Pydantic data models
│   └── sensors/         # Sensor implementations
│       ├── base.py      # Abstract sensor interface
│       ├── camera.py    # Camera/greenery detection
│       ├── microphone.py# Audio/noise sampling
│       └── ...
├── launcher/            # Desktop GUI application
│   ├── launcher.py      # Main GUI
│   ├── config.py        # Configuration management
│   └── ...
├── tests/               # Test suite
├── docs/                # Documentation
└── requirements-*.txt   # Modular dependencies
```



## Technology stack

### Core (requirements-base.txt)
- **Python 3.9+** - Programming language
- **FastAPI** - Modern web framework for building APIs
- **SQLite 3** - Local database for storing sensor data
- **CustomTkinter** - Modern GUI framework for the desktop launcher
- **numpy/pandas** - Data processing and analysis

### ML/AI Features (requirements-ml.txt - Optional)
- **DeepFace** - Facial emotion detection
- **OpenCV** - Camera capture and image processing
- **sounddevice** - Microphone audio capture
- **PyTorch** - Deep learning framework

### Development (requirements-dev.txt - Optional)
- **pytest** - Testing framework
- **black/flake8** - Code formatting and linting
- **PyInstaller** - Executable packaging



## API Endpoints

The backend provides a RESTful API for sensor data and monitoring:

- `GET /` - API status and version
- `GET /api/health` - Health check for monitoring
- `GET /api/sensors` - Get sensor status and recent readings
- `POST /api/sensors` - Submit sensor data
- `GET /api/face` - Get face detection history
- `POST /api/face` - Submit face detection results
- `GET /api/sound` - Get sound analysis history
- `POST /api/sound` - Submit sound analysis data
- `GET /api/stats` - System statistics
- `GET /api/live` - Current live readings
- `GET /api/context` - Context payload with historical analysis

For detailed API documentation, start the server and visit `http://localhost:8000/docs`

## Contributing

If you'd like to contribute, please open an issue or submit a pull request. For sensor changes, include notes on how you tested with mocked inputs or sample recordings/frames.

## License

MIT — see the `LICENSE` file for details.

---

## Installation for v0.2.0

### Base Installation (Recommended for most users)

```powershell
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install core dependencies (~500MB)
pip install -r requirements-base.txt
```

### Full Installation (with ML features)

If you want emotion detection and AI features:

```powershell
# Install base + ML dependencies (~2.5GB total)
pip install -r requirements-base.txt -r requirements-ml.txt
```

### Development Installation

For contributors who want to run tests and development tools:

```powershell
# Install all dependencies including dev tools
pip install -r requirements-base.txt -r requirements-dev.txt
```

## Running the Application

### Start the Backend Server

```powershell
# From project root
cd backend
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

### Start the Desktop Launcher

```powershell
# From project root
python -m launcher.launcher
```

The launcher will automatically start the backend server and provide a GUI interface.

## Current Status (v0.2.0)

- ✅ Desktop launcher with system tray
- ✅ FastAPI REST API backend
- ✅ SQLite database
- ✅ Configuration management
- 🚧 Camera sensor (in development)
- 🚧 Microphone sensor (in development)
- 🚧 Emotion detection (planned)
- 📅 Web dashboard (planned for v0.3.0)
