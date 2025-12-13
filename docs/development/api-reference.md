# API Documentation - CV-Mindcare

Complete reference for the CV-Mindcare REST API.

## Base URL

```
http://127.0.0.1:8000
```

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Health Check](#health-check)
  - [Sensors](#sensors)
  - [Face Detection](#face-detection)
  - [Sound Analysis](#sound-analysis)
  - [Statistics](#statistics)
  - [Live Data](#live-data)
  - [Control](#control)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Examples](#examples)

## Overview

The CV-Mindcare API is a RESTful service that:
- Collects sensor data (camera, microphone, system resources)
- Stores data in SQLite database
- Provides aggregated statistics and live readings
- Supports real-time dashboard updates

### Technology Stack
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: SQLite
- **CORS**: Enabled for localhost:3000

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible on localhost.

> **Note**: In production, consider adding API key authentication or OAuth2.

## Endpoints

### Health Check

#### GET `/`

Check if the API is online and get version information.

**Response:**
```json
{
  "status": "online",
  "version": "0.1.0",
  "name": "CV-Mindcare API"
}
```

**Status Codes:**
- `200 OK`: Server is running

---

### Sensors

#### GET `/api/sensors`

Get sensor status and recent sensor data.

**Response:**
```json
{
  "status": {
    "camera": true,
    "microphone": true,
    "system_resources": true
  },
  "recent": [
    {
      "sensor_type": "greenery",
      "value": 12.5,
      "timestamp": "2025-10-26 14:30:00"
    },
    {
      "sensor_type": "emotion_happy",
      "value": 0.75,
      "timestamp": "2025-10-26 14:29:55"
    }
  ]
}
```

**Query Parameters:**
- None

**Status Codes:**
- `200 OK`: Success

---

#### POST `/api/sensors`

Record new sensor data.

**Request Body:**
```json
{
  "sensor_type": "greenery",
  "value": 12.5,
  "timestamp": "2025-10-26 14:30:00"  // optional
}
```

**Request Fields:**
- `sensor_type` (string, required): Type of sensor (e.g., "greenery", "emotion_happy", "cpu_percent")
- `value` (float, required): Sensor reading value
- `timestamp` (string, optional): ISO format timestamp (auto-generated if not provided)

**Response:**
```json
{
  "message": "sensor data recorded"
}
```

**Status Codes:**
- `201 Created`: Data successfully recorded
- `422 Unprocessable Entity`: Invalid request body

---

### Face Detection

#### GET `/api/face`

Get the latest face detection result.

**Response:**
```json
{
  "faces_detected": 1,
  "last_detection": "2025-10-26 14:30:00"
}
```

**Fields:**
- `faces_detected` (int): Number of faces detected in last reading
- `last_detection` (string|null): Timestamp of last detection

**Status Codes:**
- `200 OK`: Success

---

#### POST `/api/face`

Record a new face detection result.

**Request Body:**
```json
{
  "faces_detected": 1,
  "timestamp": "2025-10-26 14:30:00"  // optional
}
```

**Response:**
```json
{
  "message": "face detection recorded"
}
```

**Status Codes:**
- `201 Created`: Data successfully recorded
- `422 Unprocessable Entity`: Invalid request body

---

### Sound Analysis

#### GET `/api/sound`

Get the latest sound analysis result.

**Response:**
```json
{
  "avg_db": 45.2,
  "last_sample": "2025-10-26 14:30:00"
}
```

**Fields:**
- `avg_db` (float): Average decibel level
- `last_sample` (string|null): Timestamp of last measurement

**Status Codes:**
- `200 OK`: Success

---

#### POST `/api/sound`

Record a new sound analysis result.

**Request Body:**
```json
{
  "avg_db": 45.2,
  "timestamp": "2025-10-26 14:30:00"  // optional
}
```

**Response:**
```json
{
  "message": "sound sample recorded"
}
```

**Status Codes:**
- `201 Created`: Data successfully recorded
- `422 Unprocessable Entity`: Invalid request body

---

### Statistics

#### GET `/api/stats`

Get system-wide statistics.

**Response:**
```json
{
  "uptime": 3600,
  "active_sensors": 3,
  "data_points": 1250,
  "breakdown": {
    "data_points": 1250,
    "sensor_points": 1000,
    "face_points": 150,
    "sound_points": 100
  }
}
```

**Fields:**
- `uptime` (int): System uptime in seconds (currently hardcoded to 0)
- `active_sensors` (int): Number of active sensors
- `data_points` (int): Total data points collected
- `breakdown` (object): Detailed breakdown by data type

**Status Codes:**
- `200 OK`: Success

---

### Live Data

#### GET `/api/live`

Get aggregated live data for dashboard display.

**Response:**
```json
{
  "faces_detected": 1,
  "avg_db": 45.2,
  "dominant_emotion": "happy",
  "avg_green_pct": 12.5,
  "last_updated": "2025-10-26T14:30:00.000Z",
  "emotions": {
    "happy": 0.75,
    "neutral": 0.15,
    "sad": 0.05,
    "angry": 0.03,
    "surprised": 0.02
  },
  "stats": {
    "cpu_percent": 25.5,
    "memory_percent": 45.8
  }
}
```

**Fields:**
- `faces_detected` (int): Number of faces in latest reading
- `avg_db` (float): Latest sound level
- `dominant_emotion` (string): Most common emotion
- `avg_green_pct` (float): Greenery percentage
- `last_updated` (string): ISO timestamp
- `emotions` (object): Emotion distribution (0-1 scale)
- `stats` (object): System resource usage

**Status Codes:**
- `200 OK`: Success

**Note**: This endpoint combines data from multiple sources and is optimized for dashboard refresh.

---

### Control

#### POST `/api/control/stop`

Request to stop data collection.

**Request Body:** None

**Response:**
```json
{
  "message": "data collection stop requested"
}
```

**Status Codes:**
- `200 OK`: Stop request received

**Note**: Currently a placeholder. Future implementation will gracefully stop sensor collection.

---

## Data Models

### SensorData

```python
{
  "sensor_type": str,      # Type of sensor
  "value": float,          # Numeric value
  "timestamp": str | None  # Optional ISO timestamp
}
```

### FaceDetection

```python
{
  "faces_detected": int,   # Number of faces
  "timestamp": str | None  # Optional ISO timestamp
}
```

### SoundSample

```python
{
  "avg_db": float,         # Decibel level
  "timestamp": str | None  # Optional ISO timestamp
}
```

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `422 Unprocessable Entity`: Invalid request body or parameters
- `500 Internal Server Error`: Server-side error

### Example Error

```json
{
  "detail": [
    {
      "loc": ["body", "value"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Examples

### Python Requests

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

# Health check
response = requests.get(f"{BASE_URL}/")
print(response.json())

# Post sensor data
data = {
    "sensor_type": "greenery",
    "value": 15.3
}
response = requests.post(f"{BASE_URL}/api/sensors", json=data)
print(response.json())

# Get live data
response = requests.get(f"{BASE_URL}/api/live")
live_data = response.json()
print(f"Emotion: {live_data['dominant_emotion']}")
print(f"Sound: {live_data['avg_db']} dB")
```

### JavaScript Fetch

```javascript
const BASE_URL = 'http://127.0.0.1:8000';

// Get live data
async function getLiveData() {
  const response = await fetch(`${BASE_URL}/api/live`);
  const data = await response.json();
  console.log('Dominant emotion:', data.dominant_emotion);
  console.log('CPU usage:', data.stats.cpu_percent + '%');
  return data;
}

// Post face detection
async function recordFaces(count) {
  const response = await fetch(`${BASE_URL}/api/face`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ faces_detected: count })
  });
  return await response.json();
}

// Usage
getLiveData();
recordFaces(2);
```

### cURL

```bash
# Health check
curl http://127.0.0.1:8000/

# Get sensors
curl http://127.0.0.1:8000/api/sensors

# Post sensor data
curl -X POST http://127.0.0.1:8000/api/sensors \
  -H "Content-Type: application/json" \
  -d '{"sensor_type": "greenery", "value": 12.5}'

# Get live data
curl http://127.0.0.1:8000/api/live

# Stop collection
curl -X POST http://127.0.0.1:8000/api/control/stop
```

## Rate Limiting

Currently, there is no rate limiting implemented. Consider adding rate limiting in production to prevent abuse.

## CORS Configuration

CORS is enabled for the following origins:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

To add more origins, modify `backend/app.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Database Schema

### sensor_data Table
- `id`: INTEGER PRIMARY KEY
- `sensor_type`: TEXT NOT NULL
- `value`: REAL NOT NULL
- `timestamp`: TEXT DEFAULT CURRENT_TIMESTAMP

### face_detection Table
- `id`: INTEGER PRIMARY KEY
- `faces_detected`: INTEGER NOT NULL
- `timestamp`: TEXT DEFAULT CURRENT_TIMESTAMP

### sound_analysis Table
- `id`: INTEGER PRIMARY KEY
- `avg_db`: REAL NOT NULL
- `timestamp`: TEXT DEFAULT CURRENT_TIMESTAMP

## Future Enhancements

- [ ] Add authentication (API keys or OAuth2)
- [ ] Implement pagination for historical data
- [ ] Add filtering by date range
- [ ] WebSocket support for real-time updates
- [ ] Rate limiting
- [ ] Request logging and analytics
- [ ] Data export endpoints (CSV, JSON)

---

**API Version**: 0.1.0  
**Last Updated**: October 26, 2025  
**Documentation**: https://github.com/Salman-A-Alsahli/CV-Mindcare
