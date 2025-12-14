"""Tests for SimulationController."""

import pytest
from backend.services.simulation_controller import SimulationController, SimulationScenario


class TestSimulationController:
    """Test SimulationController functionality."""

    def test_initialization(self):
        """Test controller initializes correctly."""
        controller = SimulationController()
        assert controller is not None
        assert not controller.active
        assert controller.current_scenario == SimulationScenario.CALM_FLOW

    def test_start_simulation(self):
        """Test starting simulation."""
        controller = SimulationController()
        success = controller.start("calm")
        assert success
        assert controller.active
        assert controller.start_time is not None

    def test_stop_simulation(self):
        """Test stopping simulation."""
        controller = SimulationController()
        controller.start("calm")
        success = controller.stop()
        assert success
        assert not controller.active
        assert controller.start_time is None

    def test_set_scenario(self):
        """Test setting different scenarios."""
        controller = SimulationController()
        
        controller.set_scenario("calm")
        assert controller.current_scenario == SimulationScenario.CALM_FLOW
        
        controller.set_scenario("stress")
        assert controller.current_scenario == SimulationScenario.HIGH_STRESS
        
        controller.set_scenario("dynamic")
        assert controller.current_scenario == SimulationScenario.DYNAMIC
        
        controller.set_scenario("custom")
        assert controller.current_scenario == SimulationScenario.CUSTOM

    def test_invalid_scenario(self):
        """Test invalid scenario raises error."""
        controller = SimulationController()
        with pytest.raises(ValueError):
            controller.set_scenario("invalid")

    def test_get_status(self):
        """Test getting status."""
        controller = SimulationController()
        status = controller.get_status()
        assert "active" in status
        assert "scenario" in status
        assert status["active"] is False

        controller.start("calm")
        status = controller.get_status()
        assert status["active"] is True
        assert status["scenario"] == "calm"
        assert status["uptime"] is not None

    def test_get_available_scenarios(self):
        """Test getting available scenarios."""
        controller = SimulationController()
        scenarios = controller.get_available_scenarios()
        assert len(scenarios) == 4
        assert all("id" in s for s in scenarios)
        assert all("name" in s for s in scenarios)
        assert all("description" in s for s in scenarios)

    def test_generate_camera_data_calm(self):
        """Test camera data generation for calm scenario."""
        controller = SimulationController()
        controller.start("calm")
        data = controller.generate_camera_data()
        
        assert "greenery_percentage" in data
        assert "sensor_type" in data
        assert data["sensor_type"] == "camera"
        assert data["simulation_mode"] is True
        assert 55 <= data["greenery_percentage"] <= 95  # 60-90 ± 2% variation

    def test_generate_camera_data_stress(self):
        """Test camera data generation for stress scenario."""
        controller = SimulationController()
        controller.start("stress")
        data = controller.generate_camera_data()
        
        assert "greenery_percentage" in data
        assert 0 <= data["greenery_percentage"] <= 25  # 5-20 ± 2% variation

    def test_generate_microphone_data_calm(self):
        """Test microphone data generation for calm scenario."""
        controller = SimulationController()
        controller.start("calm")
        data = controller.generate_microphone_data()
        
        assert "db_level" in data
        assert "noise_classification" in data
        assert "sensor_type" in data
        assert data["sensor_type"] == "microphone"
        assert 15 <= data["db_level"] <= 45  # 20-40 ± 3 dB variation

    def test_generate_microphone_data_stress(self):
        """Test microphone data generation for stress scenario."""
        controller = SimulationController()
        controller.start("stress")
        data = controller.generate_microphone_data()
        
        assert "db_level" in data
        assert 65 <= data["db_level"] <= 100  # 70-95 ± 3 dB variation

    def test_generate_emotion_data_calm(self):
        """Test emotion data generation for calm scenario."""
        controller = SimulationController()
        controller.start("calm")
        data = controller.generate_emotion_data()
        
        assert "emotions" in data
        assert "dominant_emotion" in data
        assert "sensor_type" in data
        assert data["sensor_type"] == "emotion"
        
        emotions = data["emotions"]
        assert "happy" in emotions
        assert "sad" in emotions
        assert "angry" in emotions
        
        # Check probabilities sum to ~1.0
        total = sum(emotions.values())
        assert 0.99 <= total <= 1.01

    def test_generate_emotion_data_stress(self):
        """Test emotion data generation for stress scenario."""
        controller = SimulationController()
        controller.start("stress")
        data = controller.generate_emotion_data()
        
        emotions = data["emotions"]
        # In stress scenario, negative emotions should be higher
        negative_sum = emotions.get("sad", 0) + emotions.get("angry", 0)
        assert negative_sum > emotions.get("happy", 0)

    def test_generate_sensor_data(self):
        """Test complete sensor data generation."""
        controller = SimulationController()
        controller.start("calm")
        data = controller.generate_sensor_data()
        
        assert "camera" in data
        assert "microphone" in data
        assert "emotion" in data
        assert "timestamp" in data
        assert "scenario" in data
        assert data["scenario"] == "calm"

    def test_dynamic_scenario_transitions(self):
        """Test dynamic scenario changes over time."""
        controller = SimulationController()
        controller.start("dynamic")
        
        # Generate multiple data points
        for _ in range(5):
            data = controller.generate_sensor_data()
            assert data["scenario"] == "dynamic"
            # Values should be within reasonable ranges
            assert 0 <= data["camera"]["greenery_percentage"] <= 100
            assert 0 <= data["microphone"]["db_level"] <= 100

    def test_custom_parameters(self):
        """Test custom scenario parameters."""
        controller = SimulationController()
        controller.set_custom_parameters({
            "greenery_range": (30, 50),
            "noise_range": (40, 60),
        })
        controller.start("custom")
        
        data = controller.generate_camera_data()
        # Should be within custom range ± variation
        assert 25 <= data["greenery_percentage"] <= 55
