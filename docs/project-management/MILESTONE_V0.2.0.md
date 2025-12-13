# CV-Mindcare v0.2.0 - Enhanced Monitoring Milestone

**Status:** 🚧 In Progress  
**Start Date:** October 26, 2025  
**Target Completion:** November 9, 2025 (2 weeks)  
**Previous Milestone:** v0.1.0 Foundation (✅ Complete)

---

## 🎯 Milestone Overview

The **v0.2.0 Enhanced Monitoring** milestone focuses on implementing real-time sensor data collection and AI-powered analysis features. This milestone transforms CV-Mindcare from a foundation application into an active monitoring system with live emotion detection, sound analysis, and data visualization.

### Key Objectives

1. **Real-time Sensor Collection** - Implement live camera and microphone data capture
2. **AI-Powered Analysis** - Integrate DeepFace for emotion detection and audio FFT analysis
3. **Live Data Streaming** - Add WebSocket support for real-time dashboard updates
4. **Data Visualization** - Create charts and graphs for trend analysis
5. **Enhanced Testing** - Comprehensive test coverage for all new features

---

## 📋 Issues & Tasks

### Issue #10: Real-time Sensor Data Collection
**Priority:** High  
**Estimated Effort:** 3 days  
**Status:** 📝 Planned

#### Description
Implement sensor modules for real-time data collection from camera and microphone hardware.

#### Requirements

**Camera Sensor (`backend/sensors/camera.py`)**
- OpenCV-based camera capture
- Configurable camera index (0, 1, etc.)
- Frame capture with resolution control
- Greenery detection using HSV color space analysis
- Error handling for missing/busy camera

**Microphone Sensor (`backend/sensors/microphone.py`)**
- sounddevice-based audio capture
- Configurable sample rate and duration
- Real-time amplitude (dB) calculation
- Noise classification (Quiet, Normal, Loud, Stress Zone)
- Buffer management for continuous capture

**Sensor Base Class (`backend/sensors/base.py`)**
- Abstract sensor interface
- Common error handling
- Status reporting (available, active, error)
- Configuration management

#### API Endpoints
```python
POST /sensors/camera/capture
GET  /sensors/camera/status
POST /sensors/microphone/capture
GET  /sensors/microphone/status
GET  /sensors/status  # All sensors
```

#### Acceptance Criteria
- [ ] Camera captures frames at 30 FPS
- [ ] Microphone samples audio at 44.1 kHz
- [ ] Greenery detection accuracy >80%
- [ ] Noise level calculation within ±5 dB
- [ ] Graceful degradation when hardware unavailable
- [ ] Unit tests with mocked hardware
- [ ] Integration tests with real hardware

#### Dependencies
- opencv-python==4.8.1
- sounddevice==0.4.6
- numpy==1.26.0

---

### Issue #11: DeepFace Integration for Emotion Detection
**Priority:** High  
**Estimated Effort:** 4 days  
**Status:** 📝 Planned

#### Description
Integrate DeepFace library for real-time facial emotion detection from webcam feed.

#### Requirements

**Face Detection Module (`backend/sensors/face_detection.py`)**
- DeepFace wrapper for emotion analysis
- Support for multiple models (VGG-Face, Facenet, OpenFace, ArcFace)
- Real-time emotion classification (angry, disgust, fear, happy, sad, surprise, neutral)
- Confidence scoring for each emotion
- Face bounding box detection
- Multi-face detection support

**Emotion Analysis Engine**
- Frame preprocessing (resize, normalize)
- Emotion classification with confidence threshold
- Dominant emotion selection
- Emotion history tracking (last 10 frames)
- Emotion smoothing to reduce jitter

#### API Endpoints
```python
POST /face/analyze       # Analyze single frame
POST /face/analyze/stream  # Start continuous analysis
DELETE /face/analyze/stream  # Stop continuous analysis
GET  /face/emotions/latest  # Get most recent emotion
GET  /face/emotions/history?limit=100  # Historical emotions
GET  /face/models  # List available DeepFace models
```

#### Data Models
```python
class EmotionResult(BaseModel):
    timestamp: datetime
    dominant_emotion: str  # angry, disgust, fear, happy, sad, surprise, neutral
    emotions: Dict[str, float]  # All emotion scores
    confidence: float  # 0.0 - 1.0
    face_detected: bool
    face_coordinates: Optional[Dict[str, int]]  # x, y, w, h
```

#### Acceptance Criteria
- [ ] Emotion detection latency <200ms per frame
- [ ] Accuracy >70% on standard emotion datasets
- [ ] Support for at least 3 DeepFace models
- [ ] Handles no-face scenarios gracefully
- [ ] Confidence threshold configurable
- [ ] Database logging of all detections
- [ ] Unit tests with sample images
- [ ] Integration tests with live camera

#### Dependencies
- deepface==0.0.79
- tensorflow==2.13.0 (or tensorflow-cpu for CPU-only)
- keras==2.13.1

---

### Issue #12: Sound Analysis with FFT
**Priority:** High  
**Estimated Effort:** 3 days  
**Status:** 📝 Planned

#### Description
Implement audio analysis using FFT for frequency analysis and noise classification.

#### Requirements

**Sound Analysis Module (`backend/sensors/sound_analysis.py`)**
- FFT-based frequency analysis
- Dominant frequency detection
- Amplitude analysis (peak, average, RMS)
- Noise classification algorithm
- Sound pattern recognition (speech, music, noise)
- Spectral analysis (low, mid, high frequency bands)

**Audio Processing**
- Real-time FFT computation
- Windowing functions (Hanning, Hamming)
- Frequency binning (0-500 Hz, 500-2000 Hz, 2000-10000 Hz)
- dB scale conversion
- Rolling average for smoothing

#### API Endpoints
```python
POST /sound/analyze       # Analyze audio buffer
POST /sound/analyze/stream  # Start continuous analysis
DELETE /sound/analyze/stream  # Stop continuous analysis
GET  /sound/latest        # Latest analysis
GET  /sound/history?limit=100  # Historical data
GET  /sound/spectrum      # Current frequency spectrum
```

#### Data Models
```python
class SoundAnalysis(BaseModel):
    timestamp: datetime
    avg_db: float
    peak_db: float
    rms_db: float
    dominant_frequency: float  # Hz
    classification: str  # Quiet, Normal, Loud, Stress Zone
    spectrum: Dict[str, float]  # Frequency bands
    pattern: Optional[str]  # speech, music, noise
```

#### Acceptance Criteria
- [ ] FFT computation <50ms for 1-second buffer
- [ ] Frequency resolution 10 Hz
- [ ] dB calculation accuracy ±3 dB
- [ ] Noise classification matches manual assessment >85%
- [ ] Pattern recognition accuracy >70%
- [ ] Real-time processing at 10 Hz sample rate
- [ ] Unit tests with synthetic audio
- [ ] Integration tests with real audio

#### Dependencies
- scipy==1.11.3 (for FFT)
- librosa==0.10.1 (optional, for advanced audio)

---

### Issue #13: WebSocket for Live Updates
**Priority:** Medium  
**Estimated Effort:** 2 days  
**Status:** 📝 Planned

#### Description
Add WebSocket support for real-time data streaming to frontend dashboard.

#### Requirements

**WebSocket Server (`backend/websocket.py`)**
- FastAPI WebSocket endpoint
- Connection pool management
- Broadcast messaging to all clients
- Heartbeat/ping-pong for connection health
- Authentication (future: JWT tokens)
- Error handling and reconnection logic

**Data Streaming**
- Real-time sensor data broadcast
- Emotion updates broadcast
- Sound analysis broadcast
- Configurable update frequency (1-60 Hz)
- Data compression for efficiency

#### WebSocket Endpoints
```python
WS /ws/live  # Live data stream (all sensors)
WS /ws/emotions  # Emotion-only stream
WS /ws/sound  # Sound-only stream
```

#### Message Format
```python
{
    "type": "sensor_update",  # sensor_update, emotion_update, sound_update
    "timestamp": "2025-10-26T10:30:00Z",
    "data": {
        "camera": {...},
        "microphone": {...},
        "emotion": {...},
        "sound": {...}
    }
}
```

#### Acceptance Criteria
- [ ] Support 100+ concurrent WebSocket connections
- [ ] Message delivery latency <50ms
- [ ] Automatic reconnection on disconnect
- [ ] Graceful handling of slow clients
- [ ] Heartbeat every 30 seconds
- [ ] Unit tests with WebSocket test client
- [ ] Load testing with 100 clients

#### Dependencies
- websockets==11.0.3

---

### Issue #14: Data Visualization
**Priority:** Medium  
**Estimated Effort:** 3 days  
**Status:** 📝 Planned

#### Description
Create charts and graphs for sensor data visualization and trend analysis.

#### Requirements

**Visualization Endpoints (`backend/visualization.py`)**
- Time-series data for plotting
- Aggregated statistics (hourly, daily)
- Emotion distribution charts
- Noise level trends
- Greenery percentage over time
- Correlation analysis

**Chart Data Endpoints**
```python
GET /visualization/emotions/timeseries?start=<iso>&end=<iso>
GET /visualization/emotions/distribution
GET /visualization/sound/timeseries?start=<iso>&end=<iso>
GET /visualization/sound/spectrum/latest
GET /visualization/greenery/timeseries?start=<iso>&end=<iso>
GET /visualization/correlations  # Emotion vs. noise, emotion vs. greenery
```

**Chart Types**
- Line charts: Time-series data (sensor readings over time)
- Bar charts: Emotion distribution (count per emotion)
- Area charts: Sound spectrum (frequency bands)
- Scatter plots: Correlation analysis
- Heatmaps: Emotion patterns by hour of day

#### Data Models
```python
class TimeSeriesData(BaseModel):
    timestamps: List[datetime]
    values: List[float]
    label: str

class DistributionData(BaseModel):
    labels: List[str]
    counts: List[int]
    percentages: List[float]

class CorrelationData(BaseModel):
    x_label: str
    y_label: str
    x_values: List[float]
    y_values: List[float]
    correlation: float  # Pearson correlation coefficient
```

#### Acceptance Criteria
- [ ] Time-series data generation <100ms for 1000 points
- [ ] Support for 10,000+ data points
- [ ] Aggregation functions (avg, min, max, median)
- [ ] Correlation calculation accuracy
- [ ] Chart data caching for performance
- [ ] Unit tests for data aggregation
- [ ] Integration tests with database

---

### Issue #15: Enhanced Testing
**Priority:** High  
**Estimated Effort:** 2 days  
**Status:** 📝 Planned

#### Description
Add comprehensive tests for all new v0.2.0 features with >85% code coverage.

#### Requirements

**Unit Tests**
- **test_sensors.py** (200+ lines)
  - Camera sensor tests with mocked OpenCV
  - Microphone sensor tests with synthetic audio
  - Sensor base class tests
  - Error handling tests
  
- **test_face_detection.py** (150+ lines)
  - DeepFace wrapper tests with sample images
  - Emotion classification tests
  - Multi-face detection tests
  - Model loading tests
  
- **test_sound_analysis.py** (150+ lines)
  - FFT computation tests
  - Noise classification tests
  - Pattern recognition tests
  - Spectral analysis tests
  
- **test_websocket.py** (100+ lines)
  - WebSocket connection tests
  - Message broadcasting tests
  - Heartbeat tests
  - Error handling tests
  
- **test_visualization.py** (100+ lines)
  - Time-series generation tests
  - Aggregation tests
  - Correlation calculation tests
  - Chart data validation tests

**Integration Tests**
- **test_sensor_integration.py** (200+ lines)
  - End-to-end sensor data flow
  - Database logging integration
  - API endpoint integration
  - WebSocket streaming integration

**Performance Tests**
- **test_performance.py** (100+ lines)
  - Sensor data capture throughput
  - Emotion detection latency
  - Sound analysis latency
  - WebSocket message delivery latency
  - Database query performance

#### Test Coverage Goals
- **backend/sensors/**: >90%
- **backend/face_detection.py**: >85%
- **backend/sound_analysis.py**: >85%
- **backend/websocket.py**: >80%
- **backend/visualization.py**: >85%
- **Overall**: >85%

#### Acceptance Criteria
- [ ] All new modules have unit tests
- [ ] Integration tests cover critical paths
- [ ] Performance tests validate latency requirements
- [ ] Code coverage >85% overall
- [ ] No failing tests in CI/CD pipeline
- [ ] Test execution time <5 minutes

---

### Issue #16: Documentation Updates
**Priority:** Medium  
**Estimated Effort:** 2 days  
**Status:** 📝 Planned

#### Description
Update all documentation to reflect v0.2.0 features and requirements.

#### Requirements

**API.md Updates**
- Add new endpoint documentation
- Update data models
- Add WebSocket protocol documentation
- Include code examples for all languages
- Document error responses

**INSTALLATION.md Updates**
- Add hardware requirements (camera, microphone)
- Update dependency list
- Add DeepFace installation guide
- Include troubleshooting for TensorFlow
- Add sensor calibration instructions

**DEVELOPMENT.md Updates**
- Add sensor development guide
- Document testing with hardware
- Include performance benchmarking guide
- Add WebSocket testing examples
- Update architecture diagrams

**New Documentation**
- **SENSOR_GUIDE.md** (300+ lines)
  - Sensor configuration
  - Calibration procedures
  - Troubleshooting common issues
  - Hardware compatibility list
  
- **EMOTION_DETECTION_GUIDE.md** (200+ lines)
  - Model selection guide
  - Performance optimization
  - Accuracy tuning
  - Privacy considerations

**README.md Updates**
- Add v0.2.0 features list
- Update quick start examples
- Include sensor requirements
- Add visualization screenshots

#### Acceptance Criteria
- [ ] All new endpoints documented in API.md
- [ ] Hardware requirements clearly stated
- [ ] Sensor calibration guide complete
- [ ] Code examples tested and working
- [ ] Screenshots/diagrams updated
- [ ] Troubleshooting section expanded
- [ ] No broken links or outdated info

---

## 🔧 Technical Architecture

### System Components

```
┌──────────────────────────────────────────────────────────┐
│                    Frontend (Future)                      │
│  - React Dashboard with WebSocket connection              │
│  - Real-time charts (Recharts)                           │
│  - Live emotion display                                   │
└───────────────────────┬──────────────────────────────────┘
                        │ WebSocket + REST API
┌───────────────────────┴──────────────────────────────────┐
│                 FastAPI Backend (v0.2.0)                  │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │   Sensors   │  │ Face Detection│  │ Sound Analysis  │ │
│  │  - Camera   │  │  - DeepFace   │  │  - FFT          │ │
│  │  - Mic      │  │  - Emotions   │  │  - Noise Level  │ │
│  └─────────────┘  └──────────────┘  └─────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐│
│  │           WebSocket Server (Real-time)               ││
│  └──────────────────────────────────────────────────────┘│
│  ┌──────────────────────────────────────────────────────┐│
│  │         REST API Endpoints (CRUD + Analytics)        ││
│  └──────────────────────────────────────────────────────┘│
└────────────────────────┬──────────────────────────────────┘
                         │
┌────────────────────────┴──────────────────────────────────┐
│               SQLite Database (Enhanced)                   │
│  - sensor_data table (camera, microphone)                 │
│  - face_detections table (emotions, confidence)           │
│  - sound_analysis table (FFT, spectrum, classification)   │
│  - sessions table (aggregated data)                       │
└────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                Hardware (User's Machine)                   │
│  - Webcam (OpenCV)                                        │
│  - Microphone (sounddevice)                              │
└──────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Sensor Capture**
   - Camera: Capture frame → Analyze greenery → Store
   - Microphone: Capture audio → Calculate dB → Classify

2. **AI Analysis**
   - Face Detection: Frame → DeepFace → Emotions → Database
   - Sound Analysis: Audio → FFT → Spectrum → Database

3. **Real-time Streaming**
   - Sensor data → WebSocket broadcast → Frontend updates
   - Configurable update rate (1-60 Hz)

4. **Data Visualization**
   - Database query → Aggregation → Chart data → API response

### Database Schema Updates

```sql
-- New: sensor_data table
CREATE TABLE sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    sensor_type TEXT NOT NULL,  -- camera, microphone
    raw_data BLOB,
    processed_data TEXT,  -- JSON
    metadata TEXT  -- JSON
);

-- Enhanced: face_detections table
CREATE TABLE face_detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    dominant_emotion TEXT NOT NULL,
    emotions TEXT NOT NULL,  -- JSON: all emotion scores
    confidence REAL NOT NULL,
    face_detected INTEGER NOT NULL,
    face_coordinates TEXT,  -- JSON: {x, y, w, h}
    model_used TEXT NOT NULL
);

-- Enhanced: sound_analysis table
CREATE TABLE sound_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    avg_db REAL NOT NULL,
    peak_db REAL NOT NULL,
    rms_db REAL NOT NULL,
    dominant_frequency REAL NOT NULL,
    classification TEXT NOT NULL,
    spectrum TEXT NOT NULL,  -- JSON: frequency bands
    pattern TEXT  -- speech, music, noise
);
```

---

## 📊 Success Metrics

### Performance Targets
- **Camera Frame Rate:** ≥30 FPS
- **Emotion Detection Latency:** <200ms per frame
- **Sound Analysis Latency:** <50ms per buffer
- **WebSocket Message Latency:** <50ms
- **API Response Time:** <100ms (95th percentile)

### Quality Targets
- **Emotion Detection Accuracy:** >70% on standard datasets
- **Noise Classification Accuracy:** >85%
- **Greenery Detection Accuracy:** >80%
- **Code Coverage:** >85%
- **Zero Critical Bugs:** No P0/P1 bugs in production

### User Experience Targets
- **Hardware Detection:** Automatic with clear error messages
- **Sensor Calibration:** <5 minutes setup time
- **Live Updates:** <100ms perceived latency
- **Data Visualization:** Interactive charts with <500ms load time

---

## 🗓️ Development Timeline

### Week 1 (Oct 26 - Nov 1)
- **Day 1-2:** Issue #10 - Real-time Sensor Collection
- **Day 3-5:** Issue #11 - DeepFace Integration
- **Day 6-7:** Issue #12 - Sound Analysis

### Week 2 (Nov 2 - Nov 9)
- **Day 1-2:** Issue #13 - WebSocket Implementation
- **Day 3-4:** Issue #14 - Data Visualization
- **Day 5-6:** Issue #15 - Testing & Coverage
- **Day 7:** Issue #16 - Documentation & Release

---

## 🔗 Dependencies

### New Python Packages
```
# Computer Vision & AI
opencv-python==4.8.1
deepface==0.0.79
tensorflow==2.13.0
keras==2.13.1

# Audio Processing
sounddevice==0.4.6
scipy==1.11.3
librosa==0.10.1

# WebSocket
websockets==11.0.3

# Existing (from v0.1.0)
fastapi==0.104+
uvicorn[standard]==0.24+
sqlalchemy==2.0+
pydantic==2.4+
```

### Hardware Requirements
- **Webcam:** USB or built-in camera (720p minimum)
- **Microphone:** USB or built-in microphone
- **CPU:** Intel i5 or equivalent (for DeepFace)
- **RAM:** 8 GB minimum (16 GB recommended with TensorFlow)
- **Storage:** 5 GB for models and data

---

## 🚀 Release Criteria

### Must Have (Blocking)
- ✅ All 7 issues closed
- ✅ All tests passing
- ✅ Code coverage >85%
- ✅ Documentation complete
- ✅ No P0/P1 bugs
- ✅ Performance targets met

### Should Have (Non-blocking)
- ✅ Sensor calibration guide
- ✅ WebSocket load testing
- ✅ Visualization examples
- ✅ Migration guide from v0.1.0

### Nice to Have (Future)
- ⏳ GPU acceleration for DeepFace
- ⏳ Multiple camera support
- ⏳ Audio pattern library
- ⏳ Export to video feature

---

## 📝 Notes

### Design Decisions
1. **DeepFace Over Custom Models:** Using DeepFace provides production-ready emotion detection with multiple model options. Custom models would require training data and infrastructure.

2. **FFT for Sound Analysis:** FFT provides comprehensive frequency analysis suitable for noise classification and pattern recognition. More advanced ML models considered for v0.3.0.

3. **WebSocket Over Server-Sent Events:** WebSocket provides bidirectional communication, enabling future features like control commands from frontend.

4. **SQLite for v0.2.0:** Sufficient for single-user desktop application. PostgreSQL migration planned for multi-user v1.0.0.

### Security Considerations
1. **Webcam Access:** User permission required, clear indicators when active
2. **Microphone Access:** User permission required, audio data processing local only
3. **Data Storage:** All data stored locally, no cloud transmission
4. **WebSocket Auth:** Basic authentication in v0.2.0, JWT tokens in v0.3.0

### Privacy Considerations
1. **Local Processing:** All AI inference runs locally, no external API calls
2. **Data Retention:** Configurable data retention period (default 30 days)
3. **Export/Delete:** User can export or delete all collected data
4. **Transparency:** Clear logging of what data is collected and when

---

## 🔄 Next Milestone Preview

### v0.3.0 - Web Dashboard (Planned)
- Complete React frontend implementation
- Real-time WebSocket integration
- Interactive Recharts visualizations
- Historical data export (CSV, JSON)
- User settings and preferences
- Advanced analytics and insights

---

**Milestone Created:** October 26, 2025  
**Last Updated:** October 26, 2025  
**Version:** 1.0
