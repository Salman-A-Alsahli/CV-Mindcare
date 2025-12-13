# Development Backlog

## Future Features and Improvements

**Target:** v0.2.0 Feature Complete, v1.0.0 Production Ready  
**Hardware:** Development continues with mock mode (hardware validation deferred to Phase 11)

---

## 📋 Executive Summary

With Phases 1-4 complete (architecture, sensors, camera, microphone), we have a solid foundation of **125 passing tests** and working sensor infrastructure with automatic mock mode. The following phases can be completed **without physical hardware** thanks to our robust mock mode implementation.

**Current State:**
- ✅ Phase 1: Architecture Consolidation (100%)
- ✅ Phase 2: Sensor Infrastructure (100%)
- ✅ Phase 3: Camera Implementation (100%)
- ✅ Phase 4: Microphone Implementation (100%)
- 🚧 Phase 5+: Integration & Features (0%)

**Estimated Timeline:**
- Phase 5-8: 10-14 days (core features)
- Phase 9-10: 3-4 days (CI/CD + docs)
- Phase 11: Hardware validation (when available)

---

## 🎯 Phase 5: Sensor Manager & Orchestration

**Duration:** 2-3 days  
**Goal:** Create unified sensor management system for coordinated data collection  
**Priority:** High (required for production deployment)

### Features to Implement

#### 5.1 SensorManager Class
Create `backend/sensors/sensor_manager.py`:
- **Centralized Control:** Manage all sensors (camera, microphone, future sensors)
- **Automatic Polling:** Configurable intervals (1-10 Hz) per sensor
- **Thread Safety:** Use threading.Lock for concurrent access
- **Health Monitoring:** Track sensor status, detect failures, auto-recover
- **Graceful Shutdown:** Clean stop for all sensors

```python
class SensorManager:
    def __init__(self, config: Dict):
        self.camera = CameraSensor(config.get('camera', {}))
        self.microphone = MicrophoneSensor(config.get('microphone', {}))
        self.polling_interval = config.get('polling_interval', 5.0)
        self.running = False
        
    def start_all(self) -> bool:
        """Start all sensors and begin polling."""
        
    def stop_all(self) -> bool:
        """Stop all sensors gracefully."""
        
    def get_all_status(self) -> Dict:
        """Get status of all sensors."""
        
    def read_all(self) -> Dict:
        """Read data from all active sensors."""
```

#### 5.2 API Endpoints
Add to `backend/app.py`:
- `GET /api/sensors/manager/status` - Overall system status
- `POST /api/sensors/manager/start` - Start all sensors
- `POST /api/sensors/manager/stop` - Stop all sensors
- `GET /api/sensors/manager/health` - Health check with diagnostics
- `PUT /api/sensors/manager/config` - Update polling configuration

#### 5.3 Background Polling
- Use `asyncio` for non-blocking polling
- Store readings in database automatically
- Handle sensor failures gracefully (continue with available sensors)
- Exponential backoff for failed sensors

#### 5.4 Testing
Create `tests/unit/test_sensor_manager.py`:
- Test initialization with various configs
- Test starting/stopping all sensors
- Test automatic polling
- Test failure recovery
- Test health monitoring
- Test concurrent access
- **Target:** 20+ tests, 100% pass rate

### Deliverables
- `backend/sensors/sensor_manager.py` (300-400 lines)
- `tests/unit/test_sensor_manager.py` (200+ lines)
- API endpoint integration
- Updated documentation

---

## 🎯 Phase 6: WebSocket Live Streaming

**Duration:** 2-3 days  
**Goal:** Real-time data streaming to clients for live monitoring  
**Priority:** High (key feature for dashboard)

### Features to Implement

#### 6.1 WebSocket Server
Create `backend/websocket_routes.py`:
- **WebSocket Endpoint:** `/ws/live` for real-time sensor data
- **Connection Manager:** Track multiple connected clients
- **Data Broadcasting:** Push sensor readings to all clients
- **Throttling:** Configurable rate limiting (1-10 Hz)
- **Authentication:** Optional token-based auth (future)

```python
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    """Stream live sensor data to WebSocket clients."""
```

#### 6.2 Message Format
Standardized JSON messages:
```json
{
  "type": "sensor_data",
  "timestamp": "2024-12-09T19:00:00Z",
  "sensors": {
    "camera": {
      "greenery_percentage": 25.5,
      "status": "ACTIVE"
    },
    "microphone": {
      "db_level": 45.0,
      "noise_classification": "Normal",
      "status": "ACTIVE"
    }
  },
  "system": {
    "cpu_percent": 35.2,
    "memory_mb": 456
  }
}
```

#### 6.3 Client Examples
Create `docs/examples/websocket_client.py`:
- Python client using `websockets` library
- JavaScript client for web dashboard
- Connection handling and reconnection logic
- Data visualization examples

#### 6.4 Testing
Create `tests/unit/test_websocket.py`:
- Test WebSocket connection
- Test message broadcasting
- Test multiple clients
- Test client disconnect handling
- Test data throttling
- **Target:** 15+ tests, 100% pass rate

### Deliverables
- `backend/websocket_routes.py` (200-300 lines)
- `docs/examples/websocket_client.py` (100+ lines)
- WebSocket integration in main app
- Updated API documentation

---

## 🎯 Phase 7: Data Visualization & Analytics

**Duration:** 3-4 days  
**Goal:** Provide aggregated data and trends for visualization  
**Priority:** Medium (enhances user experience)

### Features to Implement

#### 7.1 Aggregation Endpoints
Add to `backend/app.py`:
- `GET /api/analytics/hourly?sensor=camera&hours=24` - Hourly aggregates
- `GET /api/analytics/daily?sensor=microphone&days=30` - Daily aggregates
- `GET /api/analytics/weekly?days=90` - Weekly aggregates
- `GET /api/analytics/trends?sensor=camera&period=7d` - Trend analysis
- `GET /api/analytics/stats?sensor=all&start=...&end=...` - Statistics

#### 7.2 Analytics Engine
Create `backend/analytics.py`:
- **Data Aggregation:** Group by hour/day/week
- **Statistics Calculation:** min, max, avg, stddev, percentiles
- **Trend Detection:** Increasing/decreasing/stable patterns
- **Correlation Analysis:** Cross-sensor correlations
- **Anomaly Detection:** Flag unusual readings

```python
class AnalyticsEngine:
    def aggregate_hourly(self, sensor_type: str, hours: int) -> List[Dict]:
        """Aggregate sensor data by hour."""
        
    def calculate_trends(self, sensor_type: str, period_days: int) -> Dict:
        """Calculate trend direction and strength."""
        
    def detect_anomalies(self, sensor_type: str, threshold: float) -> List[Dict]:
        """Detect readings outside normal range."""
```

#### 7.3 Chart-Ready Responses
Format for popular charting libraries:
- Chart.js compatible format
- Plotly-friendly structure
- D3.js data arrays
- Include metadata (units, labels, colors)

Example response:
```json
{
  "labels": ["00:00", "01:00", "02:00", ...],
  "datasets": [
    {
      "label": "Greenery %",
      "data": [25.5, 28.2, 30.1, ...],
      "backgroundColor": "rgba(75, 192, 192, 0.2)"
    }
  ],
  "stats": {
    "avg": 27.3,
    "min": 15.0,
    "max": 45.0,
    "stddev": 5.2
  }
}
```

#### 7.4 Testing
Create `tests/unit/test_analytics.py`:
- Test hourly/daily/weekly aggregation
- Test statistics calculation
- Test trend detection
- Test correlation analysis
- Test anomaly detection
- Test data formatting
- **Target:** 25+ tests, 100% pass rate

### Deliverables
- `backend/analytics.py` (400-500 lines)
- 5 new API endpoints
- `tests/unit/test_analytics.py` (250+ lines)
- Example visualizations in docs

---

## 🎯 Phase 8: Enhanced Context Engine

**Duration:** 3-4 days  
**Goal:** Intelligent analysis and personalized recommendations  
**Priority:** Medium (value-add feature)

### Features to Implement

#### 8.1 Context Analysis Engine
Create `backend/context_engine.py`:
- **Pattern Detection:** Recurring environmental issues
- **Baseline Learning:** Understand user's normal conditions
- **Personalized Thresholds:** Adaptive rather than fixed
- **Recommendation System:** Actionable advice based on data
- **Quality Scoring:** Overall workspace wellness score (0-100)

```python
class ContextEngine:
    def analyze_patterns(self, user_id: str, days: int) -> Dict:
        """Detect recurring patterns in user's data."""
        
    def calculate_baselines(self, user_id: str) -> Dict:
        """Learn user's normal sensor readings."""
        
    def generate_recommendations(self, current_readings: Dict, 
                                 historical_context: Dict) -> List[str]:
        """Generate personalized recommendations."""
        
    def calculate_wellness_score(self, readings: Dict) -> float:
        """Calculate overall wellness score 0-100."""
```

#### 8.2 Recommendation Logic
- **Low Greenery + High Noise:** "Consider adding plants and noise-canceling solutions"
- **Consistent Low Greenery:** "Add more plants or move workspace near window"
- **Consistent High Noise:** "Try noise-canceling headphones or quieter location"
- **Optimal Conditions:** "Great workspace! Current setup is ideal"
- **Degrading Trends:** "Your workspace conditions are declining over past week"

#### 8.3 Correlation Analysis
- Greenery vs mood (when emotion detection added)
- Noise vs stress levels
- Time of day patterns
- Day of week patterns
- Seasonal trends

#### 8.4 Enhanced /api/context Endpoint
Upgrade existing endpoint with:
- Personalized thresholds
- Pattern summaries
- Trend insights
- Quality score
- Top 3 recommendations
- Comparison to baseline

#### 8.5 Testing
Create `tests/unit/test_context_engine.py`:
- Test pattern detection
- Test baseline calculation
- Test recommendation generation
- Test quality scoring
- Test correlation analysis
- Test with various scenarios
- **Target:** 20+ tests, 100% pass rate

### Deliverables
- `backend/context_engine.py` (400-500 lines)
- Enhanced `/api/context` endpoint
- `tests/unit/test_context_engine.py` (200+ lines)
- Recommendation documentation

---

## 🎯 Phase 9: CI/CD Pipeline

**Duration:** 1-2 days  
**Goal:** Automated testing and quality assurance  
**Priority:** High (development efficiency)

### Features to Implement

#### 9.1 GitHub Actions Workflows
Create `.github/workflows/`:

**test.yml** - Run tests on every push/PR:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements-base.txt -r requirements-dev.txt
      - run: pytest tests/ --cov=backend --cov-report=xml
      - uses: codecov/codecov-action@v3
```

**lint.yml** - Code quality checks:
```yaml
name: Lint
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install black flake8 mypy
      - run: black --check backend/ tests/
      - run: flake8 backend/ tests/ --max-line-length=100
      - run: mypy backend/ --ignore-missing-imports
```

**security.yml** - Security scanning:
```yaml
name: Security
on: [push, pull_request]
jobs:
  codeql:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: github/codeql-action/init@v2
      - uses: github/codeql-action/analyze@v2
```

#### 9.2 Pre-commit Hooks
Create `.pre-commit-config.yaml`:
- Auto-format with black
- Lint with flake8
- Type check with mypy
- Security check with bandit

#### 9.3 Test Coverage Reporting
- Configure pytest-cov
- Upload to Codecov
- Set coverage threshold (>90%)
- Block PRs below threshold

#### 9.4 Documentation
- CONTRIBUTING.md with CI/CD guidelines
- Developer setup instructions
- CI/CD troubleshooting guide

### Deliverables
- `.github/workflows/` (3 workflow files)
- `.pre-commit-config.yaml`
- Coverage configuration
- Developer documentation

---

## 🎯 Phase 10: Documentation & Examples

**Duration:** 2 days  
**Goal:** Comprehensive documentation for users and developers  
**Priority:** Medium (onboarding)

### Features to Implement

#### 10.1 API Usage Examples
Create `docs/examples/`:

**api_examples.py** - Python client examples:
```python
# Camera sensor usage
response = requests.get("http://localhost:8000/api/sensors/camera/capture")
data = response.json()
print(f"Greenery: {data['greenery_percentage']}%")

# WebSocket streaming
import asyncio
import websockets

async def stream_data():
    uri = "ws://localhost:8000/ws/live"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")

asyncio.run(stream_data())
```

**curl_examples.sh** - Command-line examples:
```bash
# Health check
curl http://localhost:8000/api/health

# Get camera status
curl http://localhost:8000/api/sensors/camera/status

# Submit manual data
curl -X POST http://localhost:8000/api/sensors/camera/greenery \
  -H "Content-Type: application/json" \
  -d '{"greenery_percentage": 35.5}'
```

**javascript_examples.js** - Frontend examples:
```javascript
// Fetch sensor data
fetch('http://localhost:8000/api/sensors/camera/capture')
  .then(res => res.json())
  .then(data => console.log('Greenery:', data.greenery_percentage));

// WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws/live');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Live data:', data);
};
```

#### 10.2 Integration Guides
- **Home Assistant:** Integration via REST API
- **Node-RED:** Flow examples for data collection
- **Grafana:** Dashboard setup guide
- **Python Apps:** SDK/library usage

#### 10.3 Troubleshooting Guide
Create `docs/TROUBLESHOOTING.md`:
- Common errors and solutions
- Sensor debugging steps
- Performance optimization tips
- Database maintenance
- Log analysis

#### 10.4 Performance Tuning Guide
Create `docs/PERFORMANCE.md`:
- Raspberry Pi optimization
- Sensor polling configuration
- Database tuning (WAL mode, caching)
- Memory management
- CPU usage reduction

#### 10.5 API Reference
- Auto-generate OpenAPI docs
- Add detailed endpoint descriptions
- Include request/response examples
- Document error codes
- Add rate limiting info (if implemented)

### Deliverables
- `docs/examples/` (6-8 example files)
- `docs/TROUBLESHOOTING.md`
- `docs/PERFORMANCE.md`
- Enhanced API documentation
- Integration guides

---

## 🎯 Phase 11: Hardware Validation (Deferred)

**Duration:** 2-3 days (when hardware available)  
**Goal:** Test on actual Raspberry Pi 5 with camera and microphone  
**Priority:** Critical (before production deployment)

### Tasks (When Hardware Available)

#### 11.1 Hardware Setup
- Install Raspberry Pi OS Lite (64-bit)
- Configure camera module (CSI or USB)
- Configure microphone (USB or I2S)
- Install dependencies
- Run hardware test script

#### 11.2 Performance Benchmarking
- Measure startup time (<10s target)
- Monitor memory usage (<500MB target)
- Check CPU usage (<50% target)
- Test sustained operation (24h run)
- Thermal monitoring (stay below 85°C)

#### 11.3 Sensor Validation
- Test camera capture (picamera2 backend)
- Test microphone capture (ALSA backend)
- Validate greenery detection accuracy (>80%)
- Validate dB calculation accuracy
- Test automatic fallback scenarios

#### 11.4 Integration Testing
- Test all API endpoints on Pi
- Test WebSocket streaming
- Test background polling
- Test database performance
- Test sensor manager coordination

#### 11.5 Optimization
- Tune polling intervals
- Adjust resolution settings
- Optimize database queries
- Configure systemd service
- Set up log rotation

### Deliverables (When Complete)
- Performance benchmark report
- Optimization recommendations
- Production deployment checklist
- Known issues documentation
- Hardware-specific configuration

---

## 📊 Overall Progress Tracking

### Completed Phases (50%)
- ✅ Phase 1: Architecture Consolidation (100%)
- ✅ Phase 2: Sensor Infrastructure (100%)
- ✅ Phase 3: Camera Implementation (100%)
- ✅ Phase 4: Microphone Implementation (100%)

### Remaining Phases (50%)
- ⬜ Phase 5: Sensor Manager (0%)
- ⬜ Phase 6: WebSocket Streaming (0%)
- ⬜ Phase 7: Data Visualization (0%)
- ⬜ Phase 8: Context Engine (0%)
- ⬜ Phase 9: CI/CD Pipeline (0%)
- ⬜ Phase 10: Documentation (0%)
- ⬜ Phase 11: Hardware Validation (deferred)

### Test Count Goals
- Current: 125 tests passing
- After Phase 5: 145 tests
- After Phase 6: 160 tests
- After Phase 7: 185 tests
- After Phase 8: 205 tests
- After Phase 9: No new tests (infrastructure)
- After Phase 10: No new tests (documentation)
- **Target:** 205+ tests at feature complete

### Timeline Estimates
- **Phases 5-8:** 10-14 days (core features)
- **Phases 9-10:** 3-4 days (infrastructure & docs)
- **Phase 11:** 2-3 days (when hardware available)
- **Total to v0.2.0 Feature Complete:** 13-18 days
- **Total to v1.0.0 Production Ready:** 15-21 days

---

## 🚀 Getting Started with Phase 5

Ready to begin Phase 5 (Sensor Manager & Orchestration):

1. **Review Phase 5 specification above**
2. **Create `backend/sensors/sensor_manager.py`**
3. **Implement SensorManager class**
4. **Add API endpoints**
5. **Write comprehensive tests**
6. **Update documentation**

Expected outcome:
- Unified sensor control
- Automatic background polling
- Health monitoring
- 20+ new tests passing
- Production-ready sensor orchestration

**No hardware required** - all development uses mock mode!

---

## 📝 Notes

- All phases designed to work with mock mode (no hardware needed)
- Each phase is independently testable
- Incremental commits after each phase
- Code review before moving to next phase
- Raspberry Pi optimization considerations throughout
- Privacy-first architecture maintained in all features

**Ready to proceed? Let's start with Phase 5!**
