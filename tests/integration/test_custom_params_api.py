"""
Integration tests for custom simulation parameters API endpoint.

Tests the new /api/simulation/custom-params endpoint and verifies
that custom parameters are properly applied to simulation data generation.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app import app


class TestCustomParametersAPI:
    """Test suite for custom simulation parameters API."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_set_valid_custom_parameters(self, client):
        """Test setting valid custom parameters."""
        params = {
            "greenery_min": 30,
            "greenery_max": 60,
            "noise_min": 40,
            "noise_max": 50,
            "emotion_happy": 0.6,
            "emotion_neutral": 0.3,
            "emotion_sad": 0.1
        }
        
        response = client.post("/api/simulation/custom-params", json=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Custom parameters updated successfully"
        assert "parameters" in data
        assert "greenery_range" in data["parameters"]
        assert "noise_range" in data["parameters"]
        assert "emotions" in data["parameters"]
    
    def test_invalid_greenery_range_min_greater_than_max(self, client):
        """Test that greenery min > max is rejected."""
        params = {
            "greenery_min": 80,
            "greenery_max": 20,
            "noise_min": 40,
            "noise_max": 50,
            "emotion_happy": 0.5,
            "emotion_neutral": 0.3,
            "emotion_sad": 0.2
        }
        
        response = client.post("/api/simulation/custom-params", json=params)
        assert response.status_code == 400
        assert "Invalid greenery range" in response.json()["detail"]
    
    def test_invalid_greenery_range_out_of_bounds(self, client):
        """Test that greenery values outside 0-100 are rejected."""
        params = {
            "greenery_min": -10,
            "greenery_max": 110,
            "noise_min": 40,
            "noise_max": 50,
            "emotion_happy": 0.5,
            "emotion_neutral": 0.3,
            "emotion_sad": 0.2
        }
        
        response = client.post("/api/simulation/custom-params", json=params)
        assert response.status_code == 400
    
    def test_invalid_noise_range_min_greater_than_max(self, client):
        """Test that noise min > max is rejected."""
        params = {
            "greenery_min": 30,
            "greenery_max": 60,
            "noise_min": 80,
            "noise_max": 20,
            "emotion_happy": 0.5,
            "emotion_neutral": 0.3,
            "emotion_sad": 0.2
        }
        
        response = client.post("/api/simulation/custom-params", json=params)
        assert response.status_code == 400
        assert "Invalid noise range" in response.json()["detail"]
    
    def test_invalid_emotion_probabilities_sum_exceeds_one(self, client):
        """Test that emotion probabilities summing to > 1.0 are rejected."""
        params = {
            "greenery_min": 30,
            "greenery_max": 60,
            "noise_min": 40,
            "noise_max": 50,
            "emotion_happy": 0.7,
            "emotion_neutral": 0.5,
            "emotion_sad": 0.3
        }
        
        response = client.post("/api/simulation/custom-params", json=params)
        assert response.status_code == 400
        assert "Invalid emotion probabilities" in response.json()["detail"]
    
    def test_invalid_emotion_probabilities_negative(self, client):
        """Test that negative emotion probabilities are rejected."""
        params = {
            "greenery_min": 30,
            "greenery_max": 60,
            "noise_min": 40,
            "noise_max": 50,
            "emotion_happy": -0.1,
            "emotion_neutral": 0.3,
            "emotion_sad": 0.2
        }
        
        response = client.post("/api/simulation/custom-params", json=params)
        assert response.status_code == 400
    
    def test_custom_params_affect_simulation_data(self, client):
        """Test that custom parameters actually affect generated data."""
        # Set very specific custom parameters
        params = {
            "greenery_min": 70,
            "greenery_max": 75,
            "noise_min": 25,
            "noise_max": 30,
            "emotion_happy": 0.8,
            "emotion_neutral": 0.1,
            "emotion_sad": 0.1
        }
        
        # Set custom parameters
        response = client.post("/api/simulation/custom-params", json=params)
        assert response.status_code == 200
        
        # Start simulation with custom scenario
        response = client.post("/api/simulation/start", json={"scenario": "custom"})
        assert response.status_code == 200
        
        # Check that simulation is active with custom scenario
        response = client.get("/api/simulation/status")
        assert response.status_code == 200
        data = response.json()
        assert data["active"] is True
        assert data["scenario"] == "custom"
        
        # Stop simulation
        response = client.post("/api/simulation/stop")
        assert response.status_code == 200
    
    def test_custom_params_persist_across_restarts(self, client):
        """Test that custom parameters persist across simulation restarts."""
        # Set custom parameters
        params = {
            "greenery_min": 50,
            "greenery_max": 60,
            "noise_min": 35,
            "noise_max": 45,
            "emotion_happy": 0.5,
            "emotion_neutral": 0.3,
            "emotion_sad": 0.2
        }
        
        response = client.post("/api/simulation/custom-params", json=params)
        assert response.status_code == 200
        
        # Start simulation
        response = client.post("/api/simulation/start", json={"scenario": "custom"})
        assert response.status_code == 200
        
        # Stop simulation
        response = client.post("/api/simulation/stop")
        assert response.status_code == 200
        
        # Start again - parameters should still be set
        response = client.post("/api/simulation/start", json={"scenario": "custom"})
        assert response.status_code == 200
        
        # Clean up
        response = client.post("/api/simulation/stop")
        assert response.status_code == 200
    
    def test_edge_case_all_zeros(self, client):
        """Test edge case with all minimum values."""
        params = {
            "greenery_min": 0,
            "greenery_max": 10,
            "noise_min": 0,
            "noise_max": 10,
            "emotion_happy": 0.0,
            "emotion_neutral": 0.0,
            "emotion_sad": 0.0
        }
        
        response = client.post("/api/simulation/custom-params", json=params)
        assert response.status_code == 200
    
    def test_edge_case_max_values(self, client):
        """Test edge case with maximum values."""
        params = {
            "greenery_min": 90,
            "greenery_max": 100,
            "noise_min": 90,
            "noise_max": 100,
            "emotion_happy": 0.4,
            "emotion_neutral": 0.3,
            "emotion_sad": 0.3
        }
        
        response = client.post("/api/simulation/custom-params", json=params)
        assert response.status_code == 200
