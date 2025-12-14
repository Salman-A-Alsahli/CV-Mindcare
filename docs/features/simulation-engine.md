# Simulation Engine

The CV-Mindcare Simulation Engine provides a robust, scenario-based data generation system for testing and development without requiring physical hardware.

## Overview

The Simulation Engine replaces the basic mock mode with an intelligent, scenario-driven simulation system that generates realistic, time-varying sensor data patterns.

### Key Features

- **Scenario-Based Generation**: Pre-configured scenarios simulate different environmental conditions
- **Time-Series Evolution**: Data evolves naturally over time, not just random static values
- **Correlated Data**: Multi-sensor data maintains realistic correlations
- **Real-Time Control**: Start, stop, and switch scenarios via API or UI
- **Visual Feedback**: Clear indicators when simulation mode is active

## Scenarios

### Calm Flow (calm)
Simulates ideal workspace conditions:
- **Greenery**: 60-90% (high nature presence)
- **Noise**: 20-40 dB (quiet environment)
- **Emotions**: Positive (Happy: 60-90%, Neutral: 10-30%)

### High Stress (stress)
Simulates stressful environment:
- **Greenery**: 5-20% (low nature presence)
- **Noise**: 70-95 dB (very noisy)
- **Emotions**: Negative (Angry: 30-50%, Sad: 20-40%)

### Dynamic
Fluctuates between calm and stress states:
- **Pattern**: Sinusoidal transitions every 2 minutes
- **Greenery**: Varies from 10-85%
- **Noise**: Inversely correlated with greenery
- **Emotions**: Smooth blend between positive and negative

### Custom
User-defined parameters for testing specific scenarios.

## Quick Start

### Via Web Dashboard

1. Open the dashboard at http://localhost:5173
2. Locate the "Simulation Engine" panel
3. Select a scenario (Calm Flow, High Stress, or Dynamic)
4. Toggle the switch to "Simulation" or click "Start Simulation"
5. Watch the yellow pulsing indicator confirm simulation is active
6. View real-time simulated data in the sensor cards and charts

### Via API

```bash
# Start simulation with calm scenario
curl -X POST http://localhost:8000/api/simulation/start \
  -H "Content-Type: application/json" \
  -d '{"scenario": "calm"}'

# Check status
curl http://localhost:8000/api/simulation/status | jq

# Stop simulation
curl -X POST http://localhost:8000/api/simulation/stop
```

### Via Python

```python
from backend.services.simulation_controller import SimulationController

controller = SimulationController()
controller.start("calm")
data = controller.generate_sensor_data()
print(data)
controller.stop()
```

## API Reference

See the [full API documentation](../development/api-reference.md#simulation-endpoints) for detailed endpoint specifications.

## Best Practices

- **Development**: Use simulation mode to develop UI without hardware
- **Testing**: Test with "High Stress" scenario to verify alert systems
- **Clarity**: Always ensure simulation mode indicators are visible
- **Documentation**: Document any simulation testing in reports

## Related Documentation

- [Architecture Overview](../development/architecture.md)
- [API Reference](../development/api-reference.md)
- [Testing Guide](../development/testing.md)
