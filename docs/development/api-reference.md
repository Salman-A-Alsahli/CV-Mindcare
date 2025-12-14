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
  - [Sensor Manager](#sensor-manager)
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

### Sensor Manager

The Sensor Manager provides centralized control and monitoring for all sensors (camera, microphone, air quality). It handles automatic polling, health monitoring, and graceful error recovery.

#### GET `/api/sensors/manager/status`

Get the current status of the sensor manager and all managed sensors.

**Response:**
```json
{
  "manager": {
    "status": "running",
    "running": true,
    "polling_interval": 5.0,
    "uptime": 123.45
  },
  "sensors": {
    "camera": {
      "name": "Camera Sensor",
      "type": "camera",
      "status": "active",
      "active": true,
      "mock_mode": false,
      "error_message": null,
      "config": {},
      "uptime_seconds": 120.5,
      "error_count": 0,
      "retry_count": 0,
      "last_read": "2025-12-14T11:30:00.000000"
    },
    "microphone": {
      "name": "Microphone Sensor",
      "type": "microphone",
      "status": "active",
      "active": true,
      "mock_mode": false,
      "error_message": null,
      "config": {},
      "uptime_seconds": 120.5,
      "error_count": 0,
      "retry_count": 0,
      "last_read": "2025-12-14T11:30:00.000000"
    },
    "air_quality": {
      "name": "MQ-135 Air Quality Sensor",
      "type": "air_quality",
      "status": "active",
      "active": true,
      "mock_mode": false,
      "error_message": null,
      "config": {},
      "uptime_seconds": 120.5,
      "error_count": 0,
      "retry_count": 0,
      "last_read": "2025-12-14T11:30:00.000000"
    }
  },
  "timestamp": "2025-12-14T11:30:00.000000"
}
```

**Fields:**
- `manager.status` (string): Manager state (stopped/starting/running/stopping/error)
- `manager.running` (boolean): Whether manager is actively running
- `manager.polling_interval` (float): Seconds between sensor reads
- `manager.uptime` (float|null): Manager uptime in seconds
- `sensors.{name}.status` (string): Sensor status (active/mock_mode/error/unavailable)
- `sensors.{name}.mock_mode` (boolean): Whether sensor is using mock data
- `sensors.{name}.error_count` (int): Number of consecutive errors
- `sensors.{name}.retry_count` (int): Number of restart attempts
- `sensors.{name}.last_read` (string|null): Timestamp of last successful read

**Status Codes:**
- `200 OK`: Success
- `500 Internal Server Error`: Failed to get status

---

#### POST `/api/sensors/manager/start`

Start the sensor manager and all sensors. Begins automatic polling at the configured interval.

**Request Body:** None

**Response:**
```json
{
  "message": "Sensor manager started",
  "status": {
    "manager": {
      "status": "running",
      "running": true,
      "polling_interval": 5.0,
      "uptime": 0.001
    },
    "sensors": {
      "camera": {
        "name": "Camera Sensor",
        "status": "active",
        "mock_mode": false,
        "error_count": 0
      },
      "microphone": {
        "name": "Microphone Sensor",
        "status": "active",
        "mock_mode": false,
        "error_count": 0
      },
      "air_quality": {
        "name": "MQ-135 Air Quality Sensor",
        "status": "active",
        "mock_mode": false,
        "error_count": 0
      }
    },
    "timestamp": "2025-12-14T11:30:00.000000"
  }
}
```

**Status Codes:**
- `200 OK`: Manager started successfully (at least one sensor started)
- `500 Internal Server Error`: Failed to start any sensors

**Note**: Sensors automatically fall back to mock mode if hardware is unavailable. The manager will still start successfully in this case.

---

#### POST `/api/sensors/manager/stop`

Stop the sensor manager and all sensors. Stops automatic polling gracefully.

**Request Body:** None

**Response:**
```json
{
  "message": "Sensor manager stopped",
  "success": true,
  "status": {
    "manager": {
      "status": "stopped",
      "running": false,
      "polling_interval": 5.0,
      "uptime": null
    },
    "sensors": {
      "camera": {
        "name": "Camera Sensor",
        "status": "inactive",
        "active": false
      },
      "microphone": {
        "name": "Microphone Sensor",
        "status": "inactive",
        "active": false
      },
      "air_quality": {
        "name": "MQ-135 Air Quality Sensor",
        "status": "inactive",
        "active": false
      }
    },
    "timestamp": "2025-12-14T11:35:00.000000"
  }
}
```

**Status Codes:**
- `200 OK`: Manager stopped successfully
- `500 Internal Server Error`: Failed to stop manager

---

#### GET `/api/sensors/manager/health`

Get detailed health metrics for the sensor manager and all sensors.

**Response:**
```json
{
  "health_score": 100,
  "status": "healthy",
  "issues": [],
  "timestamp": "2025-12-14T11:30:00.000000",
  "manager": {
    "status": "running",
    "running": true,
    "polling_interval": 5.0,
    "uptime": 300.5
  },
  "sensors": {
    "camera": {
      "name": "Camera Sensor",
      "status": "active",
      "error_count": 0,
      "retry_count": 0
    },
    "microphone": {
      "name": "Microphone Sensor",
      "status": "active",
      "error_count": 0,
      "retry_count": 0
    },
    "air_quality": {
      "name": "MQ-135 Air Quality Sensor",
      "status": "active",
      "error_count": 0,
      "retry_count": 0
    }
  }
}
```

**Fields:**
- `health_score` (int): Overall health score (0-100)
  - 100: All sensors active, no errors
  - 80-99: Degraded (some sensors in mock mode or minor errors)
  - 50-79: Degraded (multiple sensors with issues)
  - 0-49: Unhealthy (manager not running or major sensor failures)
- `status` (string): Health status (healthy/degraded/unhealthy)
- `issues` (array): List of detected problems
- `timestamp` (string): ISO format timestamp

**Status Codes:**
- `200 OK`: Success
- `500 Internal Server Error`: Failed to get health metrics

---

#### PUT `/api/sensors/manager/config`

Update sensor manager configuration. Changes take effect on next restart.

**Request Body:**
```json
{
  "polling_interval": 3.0,
  "auto_recover": true,
  "max_retries": 5
}
```

**Request Fields (all optional):**
- `polling_interval` (float): Seconds between sensor reads (1.0-60.0 recommended)
- `auto_recover` (boolean): Automatically restart failed sensors
- `max_retries` (int): Maximum restart attempts per sensor

**Response:**
```json
{
  "message": "Configuration updated",
  "config": {
    "polling_interval": 3.0,
    "auto_recover": true,
    "max_retries": 5
  },
  "status": {
    "manager": {
      "status": "running",
      "polling_interval": 3.0
    },
    "sensors": {
      "camera": { "status": "active" },
      "microphone": { "status": "active" },
      "air_quality": { "status": "active" }
    }
  }
}
```

**Status Codes:**
- `200 OK`: Configuration updated successfully
- `400 Bad Request`: Invalid configuration values
- `422 Unprocessable Entity`: Invalid request body
- `500 Internal Server Error`: Failed to update configuration

**Note**: Configuration changes require manager restart to take full effect. Current polling will continue at old interval until restart.

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

### ManagerConfig

```python
{
  "polling_interval": float | None,  # Seconds between reads (1.0-60.0)
  "auto_recover": bool | None,       # Auto-restart failed sensors
  "max_retries": int | None          # Max restart attempts
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

# Sensor Manager - Start all sensors
response = requests.post(f"{BASE_URL}/api/sensors/manager/start")
result = response.json()
print(f"Manager status: {result['status']['manager']['status']}")

# Sensor Manager - Get health metrics
response = requests.get(f"{BASE_URL}/api/sensors/manager/health")
health = response.json()
print(f"Health score: {health['health_score']}/100 ({health['status']})")

# Sensor Manager - Update configuration
config = {
    "polling_interval": 3.0,
    "auto_recover": True,
    "max_retries": 5
}
response = requests.put(f"{BASE_URL}/api/sensors/manager/config", json=config)
print(response.json())

# Sensor Manager - Stop all sensors
response = requests.post(f"{BASE_URL}/api/sensors/manager/stop")
print(response.json())
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

// Sensor Manager - Start sensors
async function startSensors() {
  const response = await fetch(`${BASE_URL}/api/sensors/manager/start`, {
    method: 'POST'
  });
  const result = await response.json();
  console.log('Manager started:', result.status.manager.status);
  return result;
}

// Sensor Manager - Get status
async function getSensorStatus() {
  const response = await fetch(`${BASE_URL}/api/sensors/manager/status`);
  const status = await response.json();
  console.log('Manager running:', status.manager.running);
  console.log('Sensors:', Object.keys(status.sensors));
  return status;
}

// Sensor Manager - Get health
async function getHealth() {
  const response = await fetch(`${BASE_URL}/api/sensors/manager/health`);
  const health = await response.json();
  console.log(`Health: ${health.health_score}/100 (${health.status})`);
  if (health.issues.length > 0) {
    console.log('Issues:', health.issues);
  }
  return health;
}

// Sensor Manager - Update config
async function updateConfig(config) {
  const response = await fetch(`${BASE_URL}/api/sensors/manager/config`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  });
  return await response.json();
}

// Sensor Manager - Stop sensors
async function stopSensors() {
  const response = await fetch(`${BASE_URL}/api/sensors/manager/stop`, {
    method: 'POST'
  });
  return await response.json();
}

// Usage
getLiveData();
recordFaces(2);

// Sensor Manager workflow
async function manageSensors() {
  await startSensors();
  await getSensorStatus();
  const health = await getHealth();
  
  if (health.health_score < 80) {
    await updateConfig({ auto_recover: true, max_retries: 5 });
  }
  
  // Later...
  await stopSensors();
}

manageSensors();
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

# Sensor Manager - Get status
curl http://127.0.0.1:8000/api/sensors/manager/status

# Sensor Manager - Start sensors
curl -X POST http://127.0.0.1:8000/api/sensors/manager/start

# Sensor Manager - Stop sensors
curl -X POST http://127.0.0.1:8000/api/sensors/manager/stop

# Sensor Manager - Get health metrics
curl http://127.0.0.1:8000/api/sensors/manager/health

# Sensor Manager - Update configuration
curl -X PUT http://127.0.0.1:8000/api/sensors/manager/config \
  -H "Content-Type: application/json" \
  -d '{"polling_interval": 3.0, "auto_recover": true}'

# Pretty print with jq (recommended for readability)
curl http://127.0.0.1:8000/api/sensors/manager/status | jq

# Add newline for better terminal output
curl -w '\n' http://127.0.0.1:8000/api/sensors/manager/status
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
