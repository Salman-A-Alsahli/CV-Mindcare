# Backend

This directory contains the FastAPI backend server for CV-Mindcare.

## Structure

- `app.py` - Main FastAPI application with API endpoints
- `database.py` - SQLite database schema and helper functions
- `sensors/` - Sensor modules for data collection
  - `camera.py` - Camera-based face detection and emotion analysis
  - `microphone.py` - Audio capture and sound level monitoring
  - `system_monitor.py` - System resource monitoring

## API Endpoints

### Core Endpoints
- `GET /` - Health check and API info
- `GET /api/sensors` - Get sensor status and recent data
- `POST /api/sensors` - Record new sensor data

### Data Endpoints
- `GET /api/face` - Get latest face detection data
- `POST /api/face` - Record face detection result
- `GET /api/sound` - Get latest sound analysis
- `POST /api/sound` - Record sound sample

### Statistics
- `GET /api/stats` - Get system statistics
- `GET /api/live` - Get live aggregated data (emotions, stats, latest readings)

### Control
- `POST /api/control/stop` - Stop data collection

## Database Schema

### Tables
1. **sensor_data** - General sensor readings
   - id, sensor_type, value, timestamp

2. **face_detection** - Face detection results
   - id, faces_detected, timestamp

3. **sound_analysis** - Sound level measurements
   - id, avg_db, timestamp

## Running the Backend

```bash
# From project root with venv activated
cd backend
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Or use the launcher application which manages the backend process automatically.

## Dependencies

- fastapi - Web framework
- uvicorn - ASGI server
- psutil - System resource monitoring
- sqlite3 - Database (built-in)
