"""
Integration Tests
---------------
Tests for API-Database integration.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend import database

client = TestClient(app)


@pytest.mark.integration
class TestAPIDatabaseIntegration:
    """Tests for API and database integration."""

    def test_post_sensor_and_retrieve(self):
        """Test posting sensor data via API and retrieving it."""
        # Post data via API
        payload = {"sensor_type": "integration_test", "value": 99.9}
        response = client.post("/api/sensors", json=payload)
        assert response.status_code == 201

        # Retrieve via API
        response = client.get("/api/sensors")
        assert response.status_code == 200
        data = response.json()

        # Verify data is in recent
        recent = data["recent"]
        matching = [r for r in recent if r["sensor_type"] == "integration_test"]
        assert len(matching) > 0
        assert matching[0]["value"] == 99.9

    def test_post_face_and_get_latest(self):
        """Test posting face detection and getting latest."""
        # Post via API
        payload = {"faces_detected": 3}
        response = client.post("/api/face", json=payload)
        assert response.status_code == 201

        # Get via API
        response = client.get("/api/face")
        assert response.status_code == 200
        data = response.json()
        assert data["faces_detected"] == 3

    def test_post_sound_and_get_latest(self):
        """Test posting sound data and getting latest."""
        # Post via API
        payload = {"avg_db": 75.5}
        response = client.post("/api/sound", json=payload)
        assert response.status_code == 201

        # Get via API
        response = client.get("/api/sound")
        assert response.status_code == 200
        data = response.json()
        assert data["avg_db"] == 75.5

    def test_live_endpoint_integration(self):
        """Test that live endpoint pulls from database correctly."""
        # Add some test data
        database.insert_sensor_data("emotion", 1.0)
        database.insert_sensor_data("greenery", 15.5)
        database.insert_face_detection(2)
        database.insert_sound_analysis(60.0)

        # Get live data
        response = client.get("/api/live")
        assert response.status_code == 200
        data = response.json()

        # Verify it includes data from database
        assert data["faces_detected"] >= 0
        assert data["avg_db"] >= 0
        assert "emotions" in data
        assert "stats" in data


@pytest.mark.integration
class TestEndToEndFlow:
    """End-to-end workflow tests."""

    def test_complete_sensor_workflow(self):
        """Test complete workflow from sensor post to live display."""
        # 1. Post sensor data
        client.post("/api/sensors", json={"sensor_type": "test_workflow", "value": 100.0})

        # 2. Post face detection
        client.post("/api/face", json={"faces_detected": 1})

        # 3. Post sound analysis
        client.post("/api/sound", json={"avg_db": 55.0})

        # 4. Get stats - should reflect all data
        response = client.get("/api/stats")
        stats = response.json()
        assert stats["data_points"] > 0

        # 5. Get live data - should include everything
        response = client.get("/api/live")
        live = response.json()
        assert "faces_detected" in live
        assert "avg_db" in live
        assert "emotions" in live
        assert "stats" in live


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
