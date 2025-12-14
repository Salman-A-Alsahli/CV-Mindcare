"""Integration tests for Simulation API endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


class TestSimulationAPI:
    """Test Simulation API endpoints."""

    def test_get_simulation_status(self):
        """Test GET /api/simulation/status."""
        response = client.get("/api/simulation/status")
        assert response.status_code == 200
        data = response.json()
        assert "active" in data
        assert "scenario" in data
        assert "available" in data
        assert data["available"] is True

    def test_get_simulation_scenarios(self):
        """Test GET /api/simulation/scenarios."""
        response = client.get("/api/simulation/scenarios")
        assert response.status_code == 200
        data = response.json()
        assert "scenarios" in data
        assert "count" in data
        assert data["count"] == 4
        
        # Verify scenario structure
        for scenario in data["scenarios"]:
            assert "id" in scenario
            assert "name" in scenario
            assert "description" in scenario
            assert "greenery" in scenario
            assert "noise" in scenario
            assert "emotion" in scenario

    def test_start_simulation_calm(self):
        """Test POST /api/simulation/start with calm scenario."""
        response = client.post(
            "/api/simulation/start",
            json={"scenario": "calm"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"]["active"] is True
        assert data["status"]["scenario"] == "calm"

    def test_start_simulation_stress(self):
        """Test POST /api/simulation/start with stress scenario."""
        response = client.post(
            "/api/simulation/start",
            json={"scenario": "stress"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"]["active"] is True
        assert data["status"]["scenario"] == "stress"

    def test_start_simulation_dynamic(self):
        """Test POST /api/simulation/start with dynamic scenario."""
        response = client.post(
            "/api/simulation/start",
            json={"scenario": "dynamic"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"]["active"] is True
        assert data["status"]["scenario"] == "dynamic"

    def test_start_simulation_invalid_scenario(self):
        """Test POST /api/simulation/start with invalid scenario."""
        response = client.post(
            "/api/simulation/start",
            json={"scenario": "invalid"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_stop_simulation(self):
        """Test POST /api/simulation/stop."""
        # First start simulation
        client.post("/api/simulation/start", json={"scenario": "calm"})
        
        # Then stop it
        response = client.post("/api/simulation/stop")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"]["active"] is False

    def test_simulation_affects_manager_status(self):
        """Test that simulation mode is reflected in manager status."""
        # Start simulation
        client.post("/api/simulation/start", json={"scenario": "calm"})
        
        # Check manager status
        response = client.get("/api/sensors/manager/status")
        assert response.status_code == 200
        data = response.json()
        assert data["manager"]["simulation_mode"] is True
        
        # Stop simulation
        client.post("/api/simulation/stop")
        
        # Check manager status again
        response = client.get("/api/sensors/manager/status")
        assert response.status_code == 200
        data = response.json()
        assert data["manager"]["simulation_mode"] is False

    def test_scenario_switching(self):
        """Test switching between scenarios."""
        # Start with calm
        response = client.post("/api/simulation/start", json={"scenario": "calm"})
        assert response.json()["status"]["scenario"] == "calm"
        
        # Switch to stress
        response = client.post("/api/simulation/start", json={"scenario": "stress"})
        assert response.json()["status"]["scenario"] == "stress"
        
        # Switch to dynamic
        response = client.post("/api/simulation/start", json={"scenario": "dynamic"})
        assert response.json()["status"]["scenario"] == "dynamic"
        
        # Clean up
        client.post("/api/simulation/stop")

    def test_simulation_default_scenario(self):
        """Test that default scenario is used when not specified."""
        response = client.post("/api/simulation/start", json={})
        assert response.status_code == 200
        # Default should be 'calm'
        assert response.json()["status"]["scenario"] == "calm"
        
        # Clean up
        client.post("/api/simulation/stop")
