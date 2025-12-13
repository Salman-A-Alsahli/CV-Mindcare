# Integration Guide: Home Assistant

Complete guide to integrate CV-Mindcare with Home Assistant for home automation.

---

## Overview

CV-Mindcare can be integrated with Home Assistant as a RESTful sensor, providing:
- Real-time greenery percentage
- Noise level monitoring  
- Air quality measurements
- Wellness score tracking

---

## Prerequisites

- Home Assistant installed and running
- CV-Mindcare API accessible from Home Assistant server
- Network connectivity between systems

---

## Quick Setup

Add to `configuration.yaml`:

```yaml
sensor:
  - platform: rest
    name: "Workspace Greenery"
    resource: "http://YOUR_IP:8000/api/sensors/camera/capture"
    value_template: "{{ value_json.greenery_percentage }}"
    unit_of_measurement: "%"
    scan_interval: 60
```

Replace `YOUR_IP` with CV-Mindcare server IP address.

See full integration guide at: [docs/integrations/home-assistant.md](home-assistant.md)

---

**Last Updated**: December 2024
