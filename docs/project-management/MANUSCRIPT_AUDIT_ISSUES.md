# GitHub Issues for Manuscript Audit Discrepancies

> **Note:** This is a historical audit document. Some issues reference previous implementations (like the desktop GUI) that have since been replaced with a React-based web dashboard.

This document contains detailed GitHub issue templates for all discrepancies identified in the manuscript audit. Each issue is ready to be created in the GitHub repository.

---

## Issue #26: [DISC-001] 🔴 CRITICAL - Implement Touchscreen UI for Raspberry Pi

### Labels
- `discrepancy-critical`
- `type:feature`
- `area:frontend`
- `area:hardware`
- `manuscript-gap`
- `raspberry-pi`

### Milestone
v0.3.0 - Manuscript Alignment & Production Ready

### Description

#### 📋 Discrepancy Summary
The manuscript specifies a local touchscreen display interface for Raspberry Pi operation, but the current implementation only provides a web-based dashboard requiring external device access.

#### 📄 Manuscript Reference
- **Document:** IT492-Report_Template[1]100.docx
- **Location:** Section 3.4.1 (Non-Functional Requirements), Section 3.6 (User Interface and Feedback System)
- **Original Requirement:**
  ```
  "Usability: Touch UI with real-time data display."
  "Creating a local touchscreen dashboard to display real-time environmental conditions
  and emotional state feedback."
  "By processing data locally on the Raspberry Pi and displaying insights through a
  built-in touchscreen, the system ensures real-time feedback while maintaining user privacy."
  ```

#### ❌ Current Status
- **Implementation Status:** NOT IMPLEMENTED
- **Evidence:**
  - Current implementation: Web dashboard (React) accessible at `http://localhost:5173`
  - Desktop GUI (`launcher/main.py`) uses mouse/keyboard, not touch-optimized
  - No touchscreen-specific UI framework or configuration
  - No Raspberry Pi DSI/HDMI display setup scripts
  - No touch event handlers
  - No kiosk mode for fullscreen operation

#### 💡 Expected Implementation
Create a touchscreen-optimized local UI that runs directly on Raspberry Pi's connected display (DSI or HDMI) without requiring external device access.

**Acceptance Criteria:**
- [ ] Touchscreen framework integrated (Kivy, PyQt6, or similar)
- [ ] Touch-optimized UI with large buttons and gesture support
- [ ] Displays all sensor data: greenery %, noise dB, air quality PPM, emotion detection
- [ ] Real-time updates without refresh (WebSocket or polling)
- [ ] Fullscreen kiosk mode by default
- [ ] Raspberry Pi DSI/HDMI display auto-detection
- [ ] Touch calibration support
- [ ] Color-coded visual alerts (green/yellow/red indicators)
- [ ] Runs on boot via systemd service
- [ ] Responsive to screen rotation (landscape/portrait)
- [ ] Unit tests for UI components
- [ ] Documentation updated with touchscreen setup guide
- [ ] Code reviewed and approved

#### 🎯 Implementation Plan

##### Option A: Kivy Framework (Recommended)
**Pros:** Touch-first, cross-platform, good Raspberry Pi support  
**Cons:** Different paradigm from React

##### Option B: PyQt6 with Touch Support
**Pros:** Mature, feature-rich, good documentation  
**Cons:** Heavier weight, Qt licensing

##### Option C: Browser Kiosk Mode
**Pros:** Reuse existing React frontend  
**Cons:** Not true native touch, browser overhead

**Recommended:** Option A (Kivy) for authentic touch experience

##### Files to Create:
- `frontend/touchscreen/main_app.py` - Kivy main application
- `frontend/touchscreen/screens/dashboard_screen.py` - Main dashboard
- `frontend/touchscreen/screens/sensor_screen.py` - Individual sensor views
- `frontend/touchscreen/widgets/sensor_card.py` - Touch-friendly sensor cards
- `frontend/touchscreen/widgets/alert_widget.py` - Visual alert indicators
- `frontend/touchscreen/services/api_client.py` - Backend API client
- `frontend/touchscreen/config/display_config.py` - Display settings
- `setup/setup-touchscreen.sh` - Installation script
- `setup/cv-mindcare-touchscreen.service` - systemd service
- `tests/touchscreen/test_ui.py` - UI component tests
- `docs/deployment/touchscreen-setup.md` - Setup documentation

##### Files to Modify:
- `pyproject.toml` - Add Kivy dependencies to `[touchscreen]` extra
- `backend/app.py` - Ensure CORS allows local touchscreen access
- `README.md` - Add touchscreen deployment option

##### Code Skeleton:

```python
# frontend/touchscreen/main_app.py
"""
CV-Mindcare Touchscreen UI
Touch-optimized interface for Raspberry Pi local display
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.config import Config
import requests

# Configure for touchscreen
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'window_state', 'maximized')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

class DashboardScreen(Screen):
    """Main dashboard with all sensor readings."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_url = "http://localhost:8000"
        
        # Schedule updates every 2 seconds
        Clock.schedule_interval(self.update_sensors, 2.0)
    
    def update_sensors(self, dt):
        """Fetch latest sensor data from API."""
        try:
            response = requests.get(f"{self.api_url}/api/live", timeout=1)
            if response.ok:
                data = response.json()
                self.update_ui(data)
        except Exception as e:
            print(f"Error updating sensors: {e}")
    
    def update_ui(self, data):
        """Update UI with sensor data."""
        # Update greenery percentage
        self.ids.greenery_label.text = f"{data['avg_green_pct']:.1f}%"
        
        # Update noise level
        self.ids.noise_label.text = f"{data['avg_db']:.1f} dB"
        
        # Update emotion
        self.ids.emotion_label.text = data['dominant_emotion'].title()
        
        # Update alert colors
        self.update_alert_indicators(data)
    
    def update_alert_indicators(self, data):
        """Update color-coded alert indicators."""
        # Greenery: < 20% = red, 20-40% = yellow, > 40% = green
        greenery = data['avg_green_pct']
        self.ids.greenery_indicator.background_color = (
            (0, 1, 0, 1) if greenery > 40 else
            (1, 1, 0, 1) if greenery > 20 else
            (1, 0, 0, 1)
        )
        
        # Noise: < 50 dB = green, 50-70 = yellow, > 70 = red
        noise = data['avg_db']
        self.ids.noise_indicator.background_color = (
            (0, 1, 0, 1) if noise < 50 else
            (1, 1, 0, 1) if noise < 70 else
            (1, 0, 0, 1)
        )

class CVMindcareTouchApp(App):
    """Main touchscreen application."""
    
    def build(self):
        sm = ScreenManager()
        sm.add_widget(DashboardScreen(name='dashboard'))
        return sm

if __name__ == '__main__':
    CVMindcareTouchApp().run()
```

```ini
# setup/cv-mindcare-touchscreen.service
[Unit]
Description=CV-Mindcare Touchscreen UI
After=network.target cv-mindcare-backend.service
Wants=cv-mindcare-backend.service

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/CV-Mindcare
Environment="DISPLAY=:0"
Environment="KIVY_BCM_DISPMANX_ID=0"
ExecStart=/usr/bin/python3 frontend/touchscreen/main_app.py
Restart=always
RestartSec=10

[Install]
WantedBy=graphical.target
```

```bash
# setup/setup-touchscreen.sh
#!/bin/bash
# Setup touchscreen UI on Raspberry Pi

echo "Installing touchscreen dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3-kivy \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev

# Install Python dependencies
pip install kivy requests

# Configure display
echo "Configuring display..."
# Enable Raspberry Pi DSI display if connected
if [ -f /sys/class/graphics/fb0 ]; then
    echo "Display detected on fb0"
fi

# Install systemd service
echo "Installing systemd service..."
sudo cp setup/cv-mindcare-touchscreen.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cv-mindcare-touchscreen
sudo systemctl start cv-mindcare-touchscreen

echo "Touchscreen UI setup complete!"
echo "UI will start automatically on boot."
```

#### 🔗 Dependencies
- Blocks: None (can be implemented independently)
- Depends on: Working backend API (already exists)

#### 📊 Impact Assessment
- **User Impact:** HIGH - Enables standalone Raspberry Pi operation as specified
- **System Impact:** HIGH - Fulfills core manuscript requirement
- **Technical Debt Impact:** DECREASES (aligns with original specification)

#### ⏱️ Estimated Effort
- **Time Estimate:** 16-24 hours
- **Complexity:** HIGH
- **Skill Level:** Mid to Senior
- **Breakdown:**
  - Kivy setup and learning: 4 hours
  - Dashboard screen implementation: 6 hours
  - Sensor cards and widgets: 4 hours
  - API integration: 2 hours
  - Display configuration: 2 hours
  - systemd service setup: 2 hours
  - Testing and refinement: 4 hours
  - Documentation: 2 hours

#### 📚 Additional Context
**Hardware Requirements:**
- Raspberry Pi 5 (or 4)
- Official Raspberry Pi Touchscreen (7-inch DSI) OR
- HDMI touchscreen monitor
- Touch calibration tools

**Reference Implementation:**
- Kivy Dashboard Example: https://github.com/kivy/kivy/tree/master/examples/demo/showcase
- Raspberry Pi Touchscreen Guide: https://www.raspberrypi.com/documentation/accessories/display.html

**Alternative Consideration:**
If Kivy proves too complex, consider chromium-browser in kiosk mode with React frontend:
```bash
chromium-browser --kiosk --touch-events=enabled http://localhost:5173
```

#### 🔍 Related Issues
- Related to #27 (Alert System) - Touchscreen should display visual alerts
- Related to #30 (Raspberry Pi Deployment) - Part of complete RPi package

---

## Issue #27: [DISC-002] 🔴 CRITICAL - Implement Real-time Alert System

### Labels
- `discrepancy-critical`
- `type:feature`
- `area:backend`
- `area:frontend`
- `manuscript-gap`
- `health-safety`

### Milestone
v0.3.0 - Manuscript Alignment & Production Ready

### Description

#### 📋 Discrepancy Summary
The manuscript specifies an alert system that triggers notifications when sensor thresholds are exceeded, but no alert triggering or notification mechanism currently exists.

#### 📄 Manuscript Reference
- **Document:** IT492-Report_Template[1]100.docx
- **Location:** Section 3.4.1 (Functional Requirements FR-005), Section 3.6 (User Interface)
- **Original Requirement:**
  ```
  "The system shall trigger alerts when air or noise thresholds are exceeded."
  "Including alert mechanisms (e.g., color-coded indicators, wellness prompts)
  for abnormal readings or stress detection."
  ```

#### ❌ Current Status
- **Implementation Status:** NOT IMPLEMENTED
- **Evidence:**
  - Air quality classification exists (excellent/good/poor/hazardous) but passive
  - Noise level detection exists but no threshold checking
  - No alert triggering logic found in sensor modules
  - No notification system (visual, audio, or database logging)
  - No alert configuration or threshold management
  - No alert history tracking

#### 💡 Expected Implementation
Implement a comprehensive alert system that:
1. Monitors sensor readings against configurable thresholds
2. Triggers alerts when thresholds are exceeded
3. Provides visual, audio, and logged notifications
4. Tracks alert history
5. Supports alert acknowledgment and snoozing

**Acceptance Criteria:**
- [ ] Alert threshold configuration system (per sensor type)
- [ ] Alert detection logic in sensor manager
- [ ] Alert levels: INFO, WARNING, CRITICAL
- [ ] Visual alerts in web dashboard (color-coded banners, flashing indicators)
- [ ] Visual alerts in touchscreen UI (Issue #26)
- [ ] Audio alerts (optional, configurable beep/tone)
- [ ] Alert history database table
- [ ] API endpoints for alert management
- [ ] Alert acknowledgment functionality
- [ ] Alert snooze functionality (e.g., "Don't alert for 1 hour")
- [ ] Configurable alert cooldown (avoid alert spam)
- [ ] Alert rules: single threshold, range, rate of change
- [ ] Unit tests for alert logic
- [ ] Integration tests for alert triggering
- [ ] Documentation updated
- [ ] Code reviewed and approved

#### 🎯 Implementation Plan

##### Files to Create:
- `backend/alerts/alert_manager.py` - Core alert management system
- `backend/alerts/alert_rules.py` - Threshold and rule definitions
- `backend/alerts/alert_types.py` - Alert severity and types
- `backend/config/alert_config.json` - Default alert thresholds
- `tests/unit/test_alert_manager.py` - Alert tests
- `tests/integration/test_alert_integration.py` - End-to-end alert tests
- `docs/user-guide/alerts.md` - Alert documentation

##### Files to Modify:
- `backend/app.py` - Add alert API endpoints
- `backend/database.py` - Add alerts table schema
- `backend/sensors/sensor_manager.py` - Integrate alert checking
- `backend/sensors/air_quality.py` - Add alert hooks
- `backend/sensors/microphone_sensor.py` - Add alert hooks
- `frontend/src/components/AlertBanner.jsx` - Visual alert component
- `frontend/src/components/Dashboard.jsx` - Display active alerts

##### Database Schema:

```sql
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_type TEXT NOT NULL,
    alert_level TEXT NOT NULL,  -- 'INFO', 'WARNING', 'CRITICAL'
    alert_type TEXT NOT NULL,   -- 'THRESHOLD_EXCEEDED', 'SPIKE_DETECTED', etc.
    message TEXT NOT NULL,
    sensor_value REAL NOT NULL,
    threshold_value REAL,
    triggered_at TEXT DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TEXT,
    acknowledged_by TEXT,
    snoozed_until TEXT,
    resolved_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_alerts_triggered ON alerts(triggered_at);
CREATE INDEX IF NOT EXISTS idx_alerts_level ON alerts(alert_level);
CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged_at);
```

##### Code Skeleton:

```python
# backend/alerts/alert_manager.py
"""
Alert Management System
Monitors sensor readings and triggers alerts based on configurable thresholds.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class AlertType(Enum):
    """Types of alerts."""
    THRESHOLD_EXCEEDED = "THRESHOLD_EXCEEDED"
    SPIKE_DETECTED = "SPIKE_DETECTED"
    RAPID_CHANGE = "RAPID_CHANGE"
    SENSOR_FAILURE = "SENSOR_FAILURE"

class AlertRule:
    """Defines an alert rule with thresholds and conditions."""
    
    def __init__(
        self,
        sensor_type: str,
        alert_type: AlertType,
        alert_level: AlertLevel,
        threshold: float,
        comparison: str = ">",  # ">", "<", ">=", "<=", "==", "!=", "range"
        threshold_max: Optional[float] = None,  # For range checks
        cooldown_seconds: int = 300,  # 5 minutes default
        message_template: str = "{sensor_type} {comparison} {threshold}"
    ):
        self.sensor_type = sensor_type
        self.alert_type = alert_type
        self.alert_level = alert_level
        self.threshold = threshold
        self.comparison = comparison
        self.threshold_max = threshold_max
        self.cooldown_seconds = cooldown_seconds
        self.message_template = message_template
        self.last_triggered: Optional[datetime] = None
    
    def check(self, value: float) -> bool:
        """Check if value triggers this alert rule."""
        if self.comparison == ">":
            return value > self.threshold
        elif self.comparison == "<":
            return value < self.threshold
        elif self.comparison == ">=":
            return value >= self.threshold
        elif self.comparison == "<=":
            return value <= self.threshold
        elif self.comparison == "==":
            return abs(value - self.threshold) < 0.01
        elif self.comparison == "range":
            return not (self.threshold <= value <= self.threshold_max)
        return False
    
    def can_trigger(self) -> bool:
        """Check if alert is not in cooldown period."""
        if self.last_triggered is None:
            return True
        
        elapsed = (datetime.now() - self.last_triggered).total_seconds()
        return elapsed >= self.cooldown_seconds
    
    def format_message(self, value: float) -> str:
        """Format alert message with actual values."""
        return self.message_template.format(
            sensor_type=self.sensor_type,
            value=value,
            threshold=self.threshold,
            comparison=self.comparison
        )

class AlertManager:
    """
    Manages alert rules, detection, and notification.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize alert manager.
        
        Args:
            config_path: Path to alert configuration JSON file
        """
        self.rules: List[AlertRule] = []
        self.active_alerts: List[Dict[str, Any]] = []
        self.alert_callbacks = []
        
        if config_path:
            self.load_config(config_path)
        else:
            self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default alert rules."""
        # Air Quality Alerts
        self.add_rule(AlertRule(
            sensor_type="air_quality",
            alert_type=AlertType.THRESHOLD_EXCEEDED,
            alert_level=AlertLevel.WARNING,
            threshold=150,  # PPM
            comparison=">",
            cooldown_seconds=600,  # 10 minutes
            message_template="Air quality POOR: {value:.1f} PPM (threshold: {threshold})"
        ))
        
        self.add_rule(AlertRule(
            sensor_type="air_quality",
            alert_type=AlertType.THRESHOLD_EXCEEDED,
            alert_level=AlertLevel.CRITICAL,
            threshold=200,  # PPM
            comparison=">",
            cooldown_seconds=300,  # 5 minutes
            message_template="Air quality HAZARDOUS: {value:.1f} PPM - Take immediate action!"
        ))
        
        # Noise Level Alerts
        self.add_rule(AlertRule(
            sensor_type="noise",
            alert_type=AlertType.THRESHOLD_EXCEEDED,
            alert_level=AlertLevel.WARNING,
            threshold=70,  # dB
            comparison=">",
            cooldown_seconds=600,
            message_template="Noise level HIGH: {value:.1f} dB (threshold: {threshold})"
        ))
        
        self.add_rule(AlertRule(
            sensor_type="noise",
            alert_type=AlertType.SPIKE_DETECTED,
            alert_level=AlertLevel.INFO,
            threshold=85,  # dB
            comparison=">",
            cooldown_seconds=60,  # 1 minute
            message_template="Noise spike detected: {value:.1f} dB"
        ))
        
        # Greenery Alerts
        self.add_rule(AlertRule(
            sensor_type="greenery",
            alert_type=AlertType.THRESHOLD_EXCEEDED,
            alert_level=AlertLevel.INFO,
            threshold=20,  # percentage
            comparison="<",
            cooldown_seconds=1800,  # 30 minutes
            message_template="Low greenery detected: {value:.1f}% - Consider adding plants"
        ))
    
    def load_config(self, config_path: str):
        """Load alert rules from JSON configuration file."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            for rule_data in config.get('rules', []):
                rule = AlertRule(
                    sensor_type=rule_data['sensor_type'],
                    alert_type=AlertType(rule_data['alert_type']),
                    alert_level=AlertLevel(rule_data['alert_level']),
                    threshold=rule_data['threshold'],
                    comparison=rule_data.get('comparison', '>'),
                    threshold_max=rule_data.get('threshold_max'),
                    cooldown_seconds=rule_data.get('cooldown_seconds', 300),
                    message_template=rule_data.get('message_template', '')
                )
                self.add_rule(rule)
            
            logger.info(f"Loaded {len(self.rules)} alert rules from {config_path}")
        
        except Exception as e:
            logger.error(f"Failed to load alert config: {e}")
            self._load_default_rules()
    
    def add_rule(self, rule: AlertRule):
        """Add an alert rule."""
        self.rules.append(rule)
    
    def check_value(self, sensor_type: str, value: float) -> List[Dict[str, Any]]:
        """
        Check a sensor value against all applicable rules.
        
        Args:
            sensor_type: Type of sensor (e.g., 'air_quality', 'noise')
            value: Sensor reading value
        
        Returns:
            List of triggered alerts
        """
        triggered_alerts = []
        
        for rule in self.rules:
            if rule.sensor_type != sensor_type:
                continue
            
            if rule.check(value) and rule.can_trigger():
                alert = {
                    'sensor_type': sensor_type,
                    'alert_level': rule.alert_level.value,
                    'alert_type': rule.alert_type.value,
                    'message': rule.format_message(value),
                    'sensor_value': value,
                    'threshold_value': rule.threshold,
                    'triggered_at': datetime.now().isoformat()
                }
                
                triggered_alerts.append(alert)
                rule.last_triggered = datetime.now()
                
                # Log to database
                self._log_alert(alert)
                
                # Execute callbacks
                self._notify_alert(alert)
                
                logger.warning(
                    f"Alert triggered: {alert['alert_level']} - {alert['message']}"
                )
        
        return triggered_alerts
    
    def _log_alert(self, alert: Dict[str, Any]):
        """Log alert to database."""
        from backend.database import log_alert
        try:
            log_alert(alert)
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")
    
    def _notify_alert(self, alert: Dict[str, Any]):
        """Execute registered alert callbacks."""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    def register_callback(self, callback):
        """Register a function to be called when alert is triggered."""
        self.alert_callbacks.append(callback)
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get list of currently active (unacknowledged) alerts."""
        from backend.database import get_unacknowledged_alerts
        return get_unacknowledged_alerts()
    
    def acknowledge_alert(self, alert_id: int, acknowledged_by: str = "system"):
        """Mark alert as acknowledged."""
        from backend.database import acknowledge_alert
        acknowledge_alert(alert_id, acknowledged_by)
    
    def snooze_alert(self, alert_id: int, snooze_minutes: int = 60):
        """Snooze alert for specified duration."""
        from backend.database import snooze_alert
        snooze_until = datetime.now() + timedelta(minutes=snooze_minutes)
        snooze_alert(alert_id, snooze_until.isoformat())
```

```python
# backend/database.py additions

def log_alert(alert: Dict[str, Any]) -> None:
    """Log an alert to the database."""
    with closing(_get_connection()) as conn:
        conn.execute(
            """
            INSERT INTO alerts (
                sensor_type, alert_level, alert_type, message,
                sensor_value, threshold_value, triggered_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                alert['sensor_type'],
                alert['alert_level'],
                alert['alert_type'],
                alert['message'],
                alert['sensor_value'],
                alert.get('threshold_value'),
                alert['triggered_at']
            )
        )
        conn.commit()

def get_unacknowledged_alerts(limit: int = 50) -> List[Dict[str, Any]]:
    """Get unacknowledged alerts."""
    with closing(_get_connection()) as conn:
        rows = conn.execute(
            """
            SELECT * FROM alerts
            WHERE acknowledged_at IS NULL
            AND (snoozed_until IS NULL OR snoozed_until < CURRENT_TIMESTAMP)
            ORDER BY triggered_at DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()
        return [dict(row) for row in rows]

def acknowledge_alert(alert_id: int, acknowledged_by: str) -> None:
    """Acknowledge an alert."""
    with closing(_get_connection()) as conn:
        conn.execute(
            "UPDATE alerts SET acknowledged_at = CURRENT_TIMESTAMP, acknowledged_by = ? WHERE id = ?",
            (acknowledged_by, alert_id)
        )
        conn.commit()

def snooze_alert(alert_id: int, snooze_until: str) -> None:
    """Snooze an alert until specified time."""
    with closing(_get_connection()) as conn:
        conn.execute(
            "UPDATE alerts SET snoozed_until = ? WHERE id = ?",
            (snooze_until, alert_id)
        )
        conn.commit()
```

#### 🔗 Dependencies
- Blocks: None (can be implemented independently)
- Depends on: Existing sensor infrastructure (already implemented)

#### 📊 Impact Assessment
- **User Impact:** HIGH - Critical safety feature for health monitoring
- **System Impact:** MEDIUM - Adds new subsystem but modular
- **Technical Debt Impact:** DECREASES (fulfills manuscript requirement)

#### ⏱️ Estimated Effort
- **Time Estimate:** 12-16 hours
- **Complexity:** MEDIUM to HIGH
- **Skill Level:** Mid to Senior
- **Breakdown:**
  - Alert manager implementation: 4 hours
  - Database integration: 2 hours
  - API endpoints: 2 hours
  - Frontend visual alerts: 3 hours
  - Testing: 3 hours
  - Documentation: 2 hours

#### 📚 Additional Context
**Alert Priority Examples:**
- **CRITICAL:** Air quality > 200 PPM (hazardous)
- **WARNING:** Noise > 70 dB (uncomfortable)
- **INFO:** Greenery < 20% (suggestion)

**Future Enhancements:**
- Email/SMS notifications (requires external service)
- Push notifications (mobile app)
- Custom user-defined alert rules
- Machine learning-based anomaly alerts

#### 🔍 Related Issues
- Related to #26 (Touchscreen UI) - Visual alerts on touchscreen
- Related to #28 (Emotion Detection) - Alerts for stress/anxiety detection

---

## Issue #28: [DISC-003] 🟡 HIGH - Integrate Emotion Detection into Main System

### Labels
- `discrepancy-high`
- `type:integration`
- `area:backend`
- `area:frontend`
- `manuscript-gap`

### Milestone
v1.0.0 - Production Release

### Description

#### 📋 Discrepancy Summary
Emotion detection module (`emotion_detection.py`) exists with DeepFace integration but is not connected to the main API, database, sensor manager, or frontend dashboard.

#### 📄 Manuscript Reference
- **Document:** IT492-Report_Template[1]100.docx
- **Location:** Section 3.4.1 (Functional Requirements FR-001), Introduction
- **Original Requirement:**
  ```
  "The system shall capture real-time facial images and detect emotional states."
  "Using computer vision, the device can detect facial expressions and analyze
  emotional states such as happiness or anxiety."
  "Using a camera module to identify facial expressions indicating mental well-being."
  ```

#### ❌ Current Status
- **Implementation Status:** PARTIALLY IMPLEMENTED
- **Evidence:**
  - ✅ Module exists: `backend/sensors/emotion_detection.py`
  - ✅ DeepFace integration with 7 emotion categories
  - ❌ NOT added to sensor manager
  - ❌ NO API endpoints for emotion detection
  - ❌ NO database table for emotion records
  - ❌ NO frontend emotion display component
  - ❌ NOT integrated into wellness scoring

#### 💡 Expected Implementation
Full integration of emotion detection into the main system workflow.

**Acceptance Criteria:**
- [ ] EmotionDetector added to sensor manager
- [ ] Database table: `emotion_detections` with schema
- [ ] API endpoints created:
  - [ ] `GET /api/sensors/emotion/status`
  - [ ] `GET /api/sensors/emotion/capture`
  - [ ] `POST /api/sensors/emotion/data`
  - [ ] `GET /api/emotion` (latest detection)
  - [ ] `GET /api/emotion/recent` (history)
- [ ] Frontend emotion display component
- [ ] Emotion integrated into `/api/live` endpoint
- [ ] Emotion data included in wellness score calculation
- [ ] Emotion trends in analytics
- [ ] Optional ML feature flag (can disable if no DeepFace)
- [ ] Unit tests for emotion API endpoints
- [ ] Integration tests for emotion workflow
- [ ] Documentation updated
- [ ] Code reviewed and approved

#### 🎯 Implementation Plan

##### Files to Create:
- `tests/unit/test_emotion_api.py` - API tests
- `frontend/src/components/EmotionCard.jsx` - Emotion display component

##### Files to Modify:
- `backend/app.py` - Add emotion API endpoints
- `backend/database.py` - Add emotion_detections table
- `backend/sensors/sensor_manager.py` - Add EmotionDetector
- `backend/analytics.py` - Add emotion analytics
- `backend/context_engine.py` - Include emotion in wellness score
- `frontend/src/components/Dashboard.jsx` - Display emotion card
- `pyproject.toml` - Ensure DeepFace in `[ml]` extra

##### Database Schema:

```sql
CREATE TABLE IF NOT EXISTS emotion_detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dominant_emotion TEXT NOT NULL,
    confidence REAL NOT NULL,
    emotion_scores TEXT,  -- JSON with all emotion scores
    faces_detected INTEGER DEFAULT 1,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_emotion_timestamp ON emotion_detections(timestamp);
CREATE INDEX IF NOT EXISTS idx_emotion_dominant ON emotion_detections(dominant_emotion);
```

##### Code Additions:

```python
# backend/app.py additions

@app.get("/api/sensors/emotion/status")
async def get_emotion_status() -> Dict[str, object]:
    """Get emotion detection sensor status."""
    try:
        from .sensors.emotion_detection import DEEPFACE_AVAILABLE
        return {
            "sensor_type": "emotion_detection",
            "available": DEEPFACE_AVAILABLE,
            "backend": "deepface" if DEEPFACE_AVAILABLE else "none",
            "status": "available" if DEEPFACE_AVAILABLE else "unavailable",
            "models": ["VGG-Face", "Facenet", "DeepFace"] if DEEPFACE_AVAILABLE else []
        }
    except Exception as e:
        return {
            "sensor_type": "emotion_detection",
            "available": False,
            "status": "error",
            "error": str(e)
        }

@app.get("/api/sensors/emotion/capture")
async def capture_emotion_data() -> Dict[str, object]:
    """Capture emotion detection data."""
    try:
        from .sensors.emotion_detection import EmotionDetector
        
        detector = EmotionDetector(config={'mock_mode': False})
        detector.start()
        
        try:
            data = detector.read()
            
            # Store in database if real detection
            if not data.get('mock_mode', False):
                insert_emotion_detection(
                    dominant_emotion=data['dominant_emotion'],
                    confidence=data['confidence'],
                    emotion_scores=json.dumps(data['emotion_scores']),
                    faces_detected=data.get('faces_detected', 1)
                )
            
            return data
        finally:
            detector.stop()
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Emotion capture failed: {str(e)}"
        )

@app.get("/api/emotion")
async def get_emotion() -> Dict[str, object]:
    """Get latest emotion detection."""
    latest = get_latest_emotion_detection()
    return {
        "dominant_emotion": latest["dominant_emotion"] if latest else "neutral",
        "confidence": latest["confidence"] if latest else 0.0,
        "emotion_scores": json.loads(latest["emotion_scores"]) if latest and latest.get("emotion_scores") else {},
        "last_detection": latest["timestamp"] if latest else None
    }
```

#### 🔗 Dependencies
- Depends on: DeepFace library (optional dependency)
- Blocks: None

#### 📊 Impact Assessment
- **User Impact:** HIGH - Primary wellness monitoring feature
- **System Impact:** MEDIUM - Requires camera access, CPU intensive
- **Technical Debt Impact:** DECREASES

#### ⏱️ Estimated Effort
- **Time Estimate:** 8-12 hours
- **Complexity:** MEDIUM
- **Skill Level:** Mid

#### 📚 Additional Context
Make emotion detection optional with feature flag to support systems without camera or GPU.

---

## Issue #29: [DISC-004] 🟡 HIGH - Add Performance Validation Suite

### Labels
- `discrepancy-high`
- `type:testing`
- `area:testing`
- `manuscript-gap`

### Milestone
v1.0.0 - Production Release

### Description

#### 📋 Discrepancy Summary
Manuscript specifies performance requirements (300ms emotion detection, 85% accuracy) but no performance tests or benchmarks exist to validate compliance.

#### 📄 Manuscript Reference
- **Document:** IT492-Report_Template[1]100.docx
- **Location:** Section 3.4.2 (Non-Functional Requirements)
- **Original Requirement:**
  ```
  "Performance: Must detect face and classify emotion within 300 ms."
  "Accuracy: Emotion recognition ≥ 85%, air quality readings ±5%."
  ```

#### ❌ Current Status
- **Implementation Status:** NOT VALIDATED
- **Evidence:**
  - No performance benchmarks in test suite
  - No latency measurements
  - No accuracy validation tests
  - No continuous performance monitoring

**Acceptance Criteria:**
- [ ] Performance test suite using pytest-benchmark
- [ ] Emotion detection latency tests
- [ ] Air quality accuracy tests
- [ ] Sensor read time benchmarks
- [ ] API endpoint response time tests
- [ ] Database query performance tests
- [ ] Performance regression detection in CI
- [ ] Performance report generation
- [ ] Document actual vs. required performance
- [ ] Optimization recommendations

**Estimated Effort:** 6-8 hours

---

## Issue #30: [DISC-005] 🟡 HIGH - Complete Raspberry Pi Deployment Package

### Labels
- `discrepancy-high`
- `type:deployment`
- `area:deployment`
- `manuscript-gap`
- `raspberry-pi`

### Milestone
v1.0.0 - Production Release

### Description

#### 📋 Discrepancy Summary
While Raspberry Pi documentation exists, deployment artifacts (scripts, services, configs) are missing for production deployment.

**Acceptance Criteria:**
- [ ] `setup-rpi.sh` automated setup script
- [ ] systemd service files
- [ ] GPIO pin configuration
- [ ] Hardware detection scripts
- [ ] Kiosk mode setup
- [ ] Auto-start on boot
- [ ] Network configuration
- [ ] Performance optimization settings
- [ ] Deployment testing on real Pi 5

**Estimated Effort:** 10-12 hours

---

## Issue #31: [DISC-006] 🟢 MEDIUM - Add Use Case Integration Tests

### Labels
- `discrepancy-medium`
- `type:testing`
- `area:testing`
- `manuscript-gap`

### Milestone
v1.0.0 - Production Release

### Description

#### 📋 Discrepancy Summary
Manuscript defines specific use cases with sequence diagrams, but no integration tests validate these workflows.

**Acceptance Criteria:**
- [ ] Test use case 1: User emotion monitoring
- [ ] Test use case 2: Air quality alert flow
- [ ] Test use case 3: Noise spike detection
- [ ] Match sequence diagrams from manuscript
- [ ] End-to-end workflow validation

**Estimated Effort:** 6-8 hours

---

## Issue #32: [DISC-007] 🟢 MEDIUM - [FUTURE] Multi-user Authentication System

### Labels
- `discrepancy-medium`
- `type:feature`
- `area:backend`
- `future-enhancement`

### Milestone
Future Enhancements

### Description

#### 📋 Discrepancy Summary
Multi-user scenarios not supported. System designed for single-user deployment.

**Note:** This was marked as "out of scope" in the manuscript, so this is a future enhancement rather than a gap.

**Acceptance Criteria:**
- [ ] User registration/login
- [ ] JWT authentication
- [ ] Role-based access control
- [ ] Per-user data segregation
- [ ] Multi-user frontend

**Estimated Effort:** 20-24 hours

---

## Summary

**Total Issues Created:** 7

**By Severity:**
- 🔴 Critical: 2 (Issues #26, #27)
- 🟡 High: 3 (Issues #28, #29, #30)
- 🟢 Medium: 2 (Issues #31, #32)

**By Milestone:**
- v0.3.0: 2 issues (26, 27)
- v1.0.0: 4 issues (28, 29, 30, 31)
- Future: 1 issue (32)

**Total Estimated Effort:** 78-104 hours
