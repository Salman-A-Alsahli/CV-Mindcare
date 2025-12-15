# Web Dashboard Guide

Learn how to use the CV-Mindcare React web dashboard.

## Overview

The web dashboard provides a modern, real-time interface for monitoring your wellness environment.

## Getting Started

### Start the Dashboard

```bash
# One-time setup
./setup-frontend.sh

# Start both backend and dashboard
./start-dashboard.sh

# Access at http://localhost:5173
```

## Dashboard Features

### 1. Live Monitoring

**Real-Time Metrics**:
- **Greenery %**: Live camera-based nature detection
- **Noise Level**: Current dB reading with classification
- **Air Quality**: PPM concentration with quality level
- **Wellness Score**: AI-calculated overall score

Updates automatically via WebSocket connection.

### 2. Interactive Charts

**View Options**:
- Hourly view (last 24 hours)
- Daily view (last 7 days)
- Weekly view (last 4 weeks)

**Chart Types**:
- Line charts for trends
- Bar charts for comparisons
- Gauge displays for current values

### 3. AI Recommendations

**Smart Suggestions**:
- Actionable wellness tips
- Pattern-based insights
- Personalized recommendations based on history

### 4. Sensor Controls

**Actions**:
- Start/stop all sensors
- View sensor status
- Check health metrics
- Configure sensor settings

## Navigation

### Top Bar
- **Logo/Home**: Return to main dashboard
- **Status Indicators**: Sensor connection status
- **Settings**: Access configuration
- **Dark Mode Toggle**: Switch themes

### Main View
- **Metrics Cards**: Current sensor readings
- **Charts Section**: Historical data visualization
- **Recommendations**: AI insights panel
- **Controls**: Sensor management buttons

### Footer
- **Version Info**: Current app version
- **API Status**: Backend connection
- **Links**: Documentation and support

## Tips & Tricks

### Keyboard Shortcuts
- `Ctrl/Cmd + R`: Refresh data
- `D`: Toggle dark mode
- `S`: Start/stop sensors

### Performance
- Charts auto-downsample for large datasets
- WebSocket connection reconnects automatically
- Lazy loading for historical data

### Customization
- Modify `config/api.yaml` for polling intervals
- Adjust chart refresh rates in settings
- Configure sensor thresholds

## Troubleshooting

**Dashboard not loading?**
```bash
# Check if frontend is running
lsof -i :5173

# Restart frontend
cd frontend && npm run dev
```

**No live data?**
```bash
# Check WebSocket connection
# Look for "Connected to sensors" message

# Verify backend is running
curl http://localhost:8000/api/health
```

**Charts not updating?**
- Check browser console for errors
- Verify WebSocket connection is active
- Ensure sensors are started

## Next Steps

- [Features Guide](features.md) - All features explained
- [API Reference](../development/api-reference.md) - Direct API access
