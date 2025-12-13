# CV-Mindcare Integrations

CV-Mindcare can be integrated with various home automation and monitoring platforms.

---

## Available Integrations

### 🏠 Home Assistant
Full integration with Home Assistant using RESTful sensors, automations, and dashboards.

**Status**: ✅ Complete  
**Guide**: [home-assistant.md](home-assistant.md)

**Features**:
- Real-time sensor data as HA entities
- Automations for alerts and notifications
- Dashboard cards for visualization
- Long-term statistics tracking

---

### 📊 Grafana (Coming Soon)
Visualize sensor data with professional dashboards.

**Status**: 📅 Planned  
**Use Case**: Advanced data visualization and analysis

---

### 🔄 Node-RED (Coming Soon)
Create custom automation flows with visual programming.

**Status**: 📅 Planned  
**Use Case**: Complex automation workflows

---

### 📱 MQTT (Coming Soon)
Publish sensor data to MQTT topics for IoT integration.

**Status**: 📅 Planned  
**Use Case**: IoT platforms, multiple subscribers

---

## Quick Start

### Prerequisites

1. CV-Mindcare API running and accessible
2. Note your API server's IP address
3. Ensure network connectivity

### Test API Connection

```bash
# Test from integration platform
curl http://YOUR_IP:8000/api/health

# Should return: {"status": "ok"}
```

### Choose Your Integration

- **Home Automation**: Start with [Home Assistant](home-assistant.md)
- **Data Visualization**: Use built-in API or wait for Grafana guide
- **Custom Integration**: Use [API Examples](../examples/)

---

## API Endpoints for Integration

### Sensor Data

```
GET /api/sensors/camera/capture          - Greenery percentage
GET /api/sensors/microphone/capture      - Noise level (dB)
GET /api/sensors/air_quality/capture     - Air quality (PPM)
GET /api/sensors/manager/status          - All sensors status
```

### Analytics

```
GET /api/analytics/aggregated            - Hourly/daily aggregates
GET /api/analytics/statistics            - Statistical analysis
GET /api/analytics/trends                - Trend detection
GET /api/analytics/correlation           - Cross-sensor correlation
```

### WebSocket

```
WS /ws/live                              - Real-time streaming
```

---

## Authentication

Currently, CV-Mindcare API has no authentication. For production:

1. Use network isolation (internal network only)
2. Add reverse proxy with authentication (nginx, Caddy)
3. Use VPN for remote access
4. Implement API keys (future feature)

---

## Examples

See [docs/examples/](../examples/) for code samples:
- Python client
- JavaScript/Node.js
- cURL commands
- WebSocket streaming

---

## Need Help?

- **Documentation**: [docs/](../README.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- **GitHub Issues**: [Report a problem](https://github.com/Salman-A-Alsahli/CV-Mindcare/issues)

---

**Last Updated**: December 2024  
**Version**: 1.0.0
