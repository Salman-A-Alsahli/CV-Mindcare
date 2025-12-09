"""
Unit Tests for Backend API
-------------------------
Tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_root_endpoint(self):
        """Test GET / returns correct status and version."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert data["version"] == "0.2.0"
        assert data["name"] == "CV-Mindcare API"
    
    def test_health_endpoint(self):
        """Test GET /api/health returns ok status."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestSensorsEndpoints:
    """Tests for sensor endpoints."""
    
    def test_get_sensors(self):
        """Test GET /api/sensors returns sensor status."""
        response = client.get("/api/sensors")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "recent" in data
        assert isinstance(data["recent"], list)
    
    def test_post_sensor_data(self):
        """Test POST /api/sensors creates sensor data."""
        payload = {
            "sensor_type": "test_sensor",
            "value": 42.5
        }
        response = client.post("/api/sensors", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "sensor data recorded"
    
    def test_post_sensor_data_invalid(self):
        """Test POST /api/sensors with invalid data."""
        # Missing required field
        payload = {
            "sensor_type": "test_sensor"
            # value is missing
        }
        response = client.post("/api/sensors", json=payload)
        assert response.status_code == 422


class TestFaceEndpoints:
    """Tests for face detection endpoints."""
    
    def test_get_face(self):
        """Test GET /api/face returns face detection data."""
        response = client.get("/api/face")
        assert response.status_code == 200
        data = response.json()
        assert "faces_detected" in data
        assert "last_detection" in data
        assert isinstance(data["faces_detected"], int)
    
    def test_post_face_detection(self):
        """Test POST /api/face creates face detection record."""
        payload = {
            "faces_detected": 2
        }
        response = client.post("/api/face", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "face detection recorded"
    
    def test_post_face_detection_invalid(self):
        """Test POST /api/face with invalid data."""
        payload = {
            "faces_detected": "invalid"  # Should be int
        }
        response = client.post("/api/face", json=payload)
        assert response.status_code == 422


class TestSoundEndpoints:
    """Tests for sound analysis endpoints."""
    
    def test_get_sound(self):
        """Test GET /api/sound returns sound analysis data."""
        response = client.get("/api/sound")
        assert response.status_code == 200
        data = response.json()
        assert "avg_db" in data
        assert "last_sample" in data
    
    def test_post_sound_analysis(self):
        """Test POST /api/sound creates sound record."""
        payload = {
            "avg_db": 65.5
        }
        response = client.post("/api/sound", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "sound sample recorded"


class TestStatsEndpoint:
    """Tests for statistics endpoint."""
    
    def test_get_stats(self):
        """Test GET /api/stats returns statistics."""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "uptime" in data
        assert "active_sensors" in data
        assert "data_points" in data
        assert "breakdown" in data
        assert isinstance(data["data_points"], int)


class TestLiveEndpoint:
    """Tests for live data endpoint."""
    
    def test_get_live_data(self):
        """Test GET /api/live returns aggregated live data."""
        response = client.get("/api/live")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "faces_detected" in data
        assert "avg_db" in data
        assert "dominant_emotion" in data
        assert "avg_green_pct" in data
        assert "last_updated" in data
        assert "emotions" in data
        assert "stats" in data
        
        # Check data types
        assert isinstance(data["faces_detected"], int)
        assert isinstance(data["avg_db"], (int, float))
        assert isinstance(data["dominant_emotion"], str)
        assert isinstance(data["emotions"], dict)
        assert isinstance(data["stats"], dict)
        
        # Check stats structure
        assert "cpu_percent" in data["stats"]
        assert "memory_percent" in data["stats"]


class TestControlEndpoint:
    """Tests for control endpoints."""
    
    def test_post_stop_collection(self):
        """Test POST /api/control/stop."""
        response = client.post("/api/control/stop")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "data collection stop requested"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
