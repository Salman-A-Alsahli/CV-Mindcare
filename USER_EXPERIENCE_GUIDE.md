# CV-Mindcare v0.2.0 - User Experience Guide

**Last Updated:** December 9, 2024  
**Version:** 0.2.0 Feature Complete  
**Purpose:** Complete guide for users to get started and maximize value from CV-Mindcare

---

## 🌟 Welcome to CV-Mindcare

CV-Mindcare is your **personal wellness assistant** that monitors your workspace environment and provides actionable recommendations to improve your mental wellbeing and productivity - all while keeping your data 100% private on your local machine.

### What Makes CV-Mindcare Special?

✅ **Privacy-First:** All processing happens locally - zero cloud dependencies  
✅ **Smart Monitoring:** Camera (greenery detection) and microphone (noise analysis)  
✅ **AI-Powered Insights:** Personalized recommendations based on your patterns  
✅ **Easy to Use:** Desktop GUI + REST API + WebSocket streaming  
✅ **Production Ready:** Tested, documented, and optimized for Raspberry Pi 5  

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Installation

```bash
# Clone the repository
git clone https://github.com/Salman-A-Alsahli/CV-Mindcare.git
cd CV-Mindcare

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\Activate.ps1

# Activate (Linux/Mac)
source .venv/bin/activate

# Install core dependencies (~500MB)
pip install -r requirements-base.txt
```

### Step 2: Start the Application

**Option A: Desktop GUI (Recommended)**
```bash
python -m launcher.launcher
```

**Option B: Backend Only**
```bash
cd backend
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

### Step 3: Access the Application

- **Desktop GUI:** Opens automatically
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

### Step 4: Start Monitoring

1. Click "Start Sensors" in the GUI (or use API)
2. Sensors automatically collect data (works without hardware via mock mode)
3. View real-time data and recommendations

---

## 📊 Key Features & How to Use Them

### 1. Sensor Monitoring

**What it does:** Continuously monitors your workspace environment

**Available Sensors:**
- 🎥 **Camera:** Detects greenery percentage in your view (plants, nature)
- 🎤 **Microphone:** Measures ambient noise levels (dB) and classifies them
- 🔄 **Automatic Fallback:** Works with mock data if hardware isn't available

**How to use:**
```bash
# Via API
curl -X POST http://localhost:8000/api/sensors/manager/start

# Check status
curl http://localhost:8000/api/sensors/manager/status

# Get health metrics
curl http://localhost:8000/api/sensors/manager/health
```

### 2. Real-Time WebSocket Streaming

**What it does:** Streams live sensor data to your applications

**How to use:**
```bash
# Connect with Python client
python docs/examples/websocket_client.py --rate 5.0

# Or use JavaScript
# See docs/examples/api_examples.js
```

**Use cases:**
- Live dashboards
- Home automation integrations
- Real-time alerts

### 3. Analytics & Trends

**What it does:** Analyzes historical data to identify patterns and trends

**Available Analytics:**
- 📈 **Time-series aggregation** (hourly/daily/weekly/monthly)
- 📊 **Statistical analysis** (avg, min, max, stddev, median, etc.)
- 🔍 **Trend detection** (is your environment improving or degrading?)
- ⚠️ **Anomaly detection** (unusual spikes or patterns)
- 🔗 **Correlation analysis** (how greenery affects noise, etc.)

**How to use:**
```bash
# Get statistics for past 7 days
curl "http://localhost:8000/api/analytics/statistics/greenery?days=7"

# Detect trends
curl "http://localhost:8000/api/analytics/trends/noise?period=daily&days=30"

# Find anomalies
curl "http://localhost:8000/api/analytics/anomalies/greenery?days=7"
```

### 4. AI-Powered Recommendations

**What it does:** Provides personalized suggestions based on your workspace patterns

**Features:**
- 🎯 **Smart recommendations** with priority levels
- 💯 **Wellness score** (0-100) with component breakdown
- 🔄 **Pattern detection** (recurring issues, time-based patterns)
- 📊 **Personalized baselines** (learns your norms over time)
- 💬 **Feedback loop** (track what works for you)

**How to use:**
```bash
# Get personalized recommendations
curl "http://localhost:8000/api/context/recommendations?days=7&limit=5"

# Calculate your wellness score
curl "http://localhost:8000/api/context/wellness_score?days=1"

# Detect patterns
curl "http://localhost:8000/api/context/patterns?days=14&type=all"

# Submit feedback
curl -X POST "http://localhost:8000/api/context/feedback" \
  -H "Content-Type: application/json" \
  -d '{"recommendation_id": "rec_001", "helpful": true}'
```

---

## 🎯 Common Use Cases

### Use Case 1: Daily Wellness Check

**Goal:** Start your day with a wellness assessment

**Steps:**
1. Start sensors in the morning
2. Let it collect data for 30 minutes
3. Check your wellness score: `GET /api/context/wellness_score?days=1`
4. Review recommendations: `GET /api/context/recommendations?days=1`
5. Implement suggested improvements

**Expected outcome:** Personalized action plan for the day

### Use Case 2: Optimize Your Workspace

**Goal:** Improve your environment based on data

**Steps:**
1. Collect baseline data for 7 days
2. Get your baselines: `GET /api/context/baselines`
3. Identify improvement areas (low greenery, high noise)
4. Make changes (add plants, noise-cancelling, etc.)
5. Track improvements with trends: `GET /api/analytics/trends/greenery?period=daily`

**Expected outcome:** Measurable workspace improvements

### Use Case 3: Home Automation Integration

**Goal:** Integrate with Home Assistant, Node-RED, or Grafana

**Steps:**
1. Follow integration guide (see `docs/integrations/`)
2. Set up REST sensors for polling
3. Configure WebSocket for real-time updates
4. Create automations based on thresholds
5. Build dashboards for visualization

**Expected outcome:** Automated wellness monitoring in your smart home

### Use Case 4: Research & Data Collection

**Goal:** Collect and analyze wellness data over time

**Steps:**
1. Enable continuous monitoring
2. Export data from SQLite database
3. Analyze with Python/pandas
4. Generate reports and visualizations
5. Track long-term patterns

**Expected outcome:** Data-driven insights into your wellbeing

---

## 🔧 Configuration & Customization

### Sensor Configuration

```python
# Configure camera sensor
camera_config = {
    'backend': 'opencv',  # or 'picamera2' for Raspberry Pi
    'resolution': (640, 480),
    'hsv_lower': [35, 40, 40],
    'hsv_upper': [85, 255, 255]
}

# Configure microphone sensor
mic_config = {
    'backend': 'sounddevice',  # or 'alsa' for Raspberry Pi
    'sample_rate': 44100,
    'duration': 1.0,
    'db_reference': -60
}
```

### Sensor Manager Configuration

```bash
# Update polling interval and auto-recovery
curl -X PUT "http://localhost:8000/api/sensors/manager/config" \
  -H "Content-Type: application/json" \
  -d '{
    "polling_interval": 2.0,
    "auto_recover": true,
    "max_retries": 3
  }'
```

### Context Engine Configuration

```python
# Adjust thresholds for recommendations
context_config = {
    'min_greenery': 15.0,  # Minimum healthy greenery %
    'max_noise': 70.0,     # Maximum acceptable noise dB
    'baseline_days': 30,   # Days to establish baseline
    'min_confidence': 0.7  # Minimum confidence for recommendations
}
```

---

## 📱 Integration Options

### Option 1: Home Assistant

**Best for:** Smart home automation enthusiasts

**Features:**
- REST sensors for polling data
- Binary sensors for threshold alerts
- Template sensors for custom calculations
- Automations for notifications
- Lovelace dashboard cards

**Guide:** `docs/integrations/home_assistant.md`

### Option 2: Node-RED

**Best for:** Visual flow-based automation

**Features:**
- HTTP request nodes for API calls
- WebSocket nodes for real-time data
- Dashboard nodes for visualization
- Function nodes for processing
- Notification flows

**Guide:** `docs/integrations/node_red.md`

### Option 3: Grafana

**Best for:** Data visualization and monitoring

**Features:**
- JSON API data source
- Time-series panels
- Stat panels and gauges
- Alert rules
- Variables and templating

**Guide:** `docs/integrations/grafana.md`

### Option 4: Custom Integration

**Best for:** Developers building custom solutions

**Available APIs:**
- REST API (45 endpoints)
- WebSocket streaming
- Python client library
- JavaScript/Node.js client

**Examples:** `docs/examples/`

---

## 🎓 Learning Path

### Beginner (Week 1)

1. **Day 1-2:** Install and explore the GUI
2. **Day 3-4:** Learn basic API endpoints (status, capture)
3. **Day 5-6:** Understand sensor data and mock mode
4. **Day 7:** Review first week's data and recommendations

### Intermediate (Week 2-4)

1. **Week 2:** Explore analytics endpoints (statistics, trends)
2. **Week 3:** Set up WebSocket streaming
3. **Week 4:** Integrate with one platform (Home Assistant/Node-RED/Grafana)

### Advanced (Month 2+)

1. Build custom dashboards
2. Create advanced automations
3. Analyze historical trends
4. Optimize your workspace based on data
5. Contribute to the project

---

## 💡 Tips & Best Practices

### For Best Results

1. **Collect Baseline Data:** Run for at least 7 days before relying on recommendations
2. **Consistent Monitoring:** Keep sensors running during work hours
3. **Act on Recommendations:** Implement suggestions and track results
4. **Provide Feedback:** Use the feedback API to improve accuracy
5. **Regular Reviews:** Check weekly trends and adjust your workspace

### Performance Optimization

1. **Adjust Polling Interval:** Lower = more data, higher = less CPU usage
2. **Use Mock Mode for Development:** Faster iteration without hardware
3. **Database Maintenance:** Periodically archive old data
4. **Monitor Resources:** Check CPU and memory usage in production

### Privacy & Security

1. **All Data is Local:** No cloud uploads or external API calls
2. **Control Your Data:** SQLite database you can access and backup
3. **Network Security:** Bind to localhost only in production
4. **Firewall Configuration:** Only expose needed ports

---

## 🆘 Getting Help

### Documentation

- **API Reference:** `docs/API_REFERENCE.md`
- **Troubleshooting:** `docs/TROUBLESHOOTING.md`
- **Integration Guides:** `docs/integrations/`
- **Examples:** `docs/examples/`

### Common Issues

**Sensors not working?**
- Check hardware connections
- Verify permissions (camera/microphone)
- Use mock mode for testing
- See troubleshooting guide

**API errors?**
- Check server is running
- Verify correct port (8000)
- Review API documentation
- Check logs for details

**Performance issues?**
- Adjust polling interval
- Monitor system resources
- Consider Raspberry Pi optimization
- Check database size

### Community & Support

- **GitHub Issues:** Report bugs and request features
- **Discussions:** Ask questions and share experiences
- **Pull Requests:** Contribute improvements
- **Documentation:** Help improve guides

---

## 🎉 What's Next?

### Short Term (This Week)

1. Complete initial setup
2. Understand basic features
3. Collect first week of data
4. Review initial recommendations

### Medium Term (This Month)

1. Set up your preferred integration
2. Create custom automations
3. Build personalized dashboards
4. Optimize your workspace

### Long Term (This Quarter)

1. Analyze quarterly trends
2. Measure workspace improvements
3. Share your experience
4. Contribute to the project

---

## 📈 Success Metrics

Track your progress with these metrics:

- ✅ **Wellness Score Improvement:** Target 10+ point increase
- ✅ **Greenery Increase:** Add plants to reach 20%+ greenery
- ✅ **Noise Reduction:** Reduce average noise by 10+ dB
- ✅ **Pattern Recognition:** Identify and address 3+ recurring issues
- ✅ **Automation Setup:** 5+ automated responses to conditions

---

## 🙏 Feedback

Your experience matters! Help us improve CV-Mindcare:

1. **Report Issues:** Found a bug? Open a GitHub issue
2. **Suggest Features:** Have an idea? Start a discussion
3. **Share Success:** Improved your workspace? Share your story
4. **Contribute:** Code, docs, or examples welcome

---

**Enjoy CV-Mindcare and here's to better wellbeing! 🌱**
