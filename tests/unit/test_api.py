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
        assert data["version"] == "0.3.0"
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
        payload = {"sensor_type": "test_sensor", "value": 42.5}
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
        payload = {"faces_detected": 2}
        response = client.post("/api/face", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "face detection recorded"

    def test_post_face_detection_invalid(self):
        """Test POST /api/face with invalid data."""
        payload = {"faces_detected": "invalid"}  # Should be int
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
        payload = {"avg_db": 65.5}
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


class TestCameraEndpoints:
    """Tests for camera sensor endpoints (Phase 3)."""

    def test_get_camera_status(self):
        """Test GET /api/sensors/camera/status."""
        response = client.get("/api/sensors/camera/status")
        assert response.status_code == 200
        data = response.json()
        assert "sensor_type" in data
        assert data["sensor_type"] == "camera"
        assert "available" in data
        assert "status" in data

    def test_capture_camera_data(self):
        """Test GET /api/sensors/camera/capture."""
        response = client.get("/api/sensors/camera/capture")
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "sensor_type" in data
        assert data["sensor_type"] == "camera"
        assert "greenery_percentage" in data
        assert 0 <= data["greenery_percentage"] <= 100
        assert "mock_mode" in data

    def test_post_greenery_data(self):
        """Test POST /api/sensors/camera/greenery."""
        response = client.post("/api/sensors/camera/greenery?greenery_percentage=25.5")
        assert response.status_code == 201
        data = response.json()
        assert "message" in data

    def test_post_greenery_data_invalid_low(self):
        """Test POST /api/sensors/camera/greenery with invalid low value."""
        response = client.post("/api/sensors/camera/greenery?greenery_percentage=-5")
        assert response.status_code == 400

    def test_post_greenery_data_invalid_high(self):
        """Test POST /api/sensors/camera/greenery with invalid high value."""
        response = client.post("/api/sensors/camera/greenery?greenery_percentage=105")
        assert response.status_code == 400


class TestMicrophoneEndpoints:
    """Tests for microphone sensor endpoints (Phase 4)."""

    def test_get_microphone_status(self):
        """Test GET /api/sensors/microphone/status."""
        response = client.get("/api/sensors/microphone/status")
        assert response.status_code == 200
        data = response.json()
        assert "sensor_type" in data
        assert data["sensor_type"] == "microphone"
        assert "available" in data
        assert "status" in data

    def test_capture_microphone_data(self):
        """Test GET /api/sensors/microphone/capture."""
        response = client.get("/api/sensors/microphone/capture")
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "sensor_type" in data
        assert data["sensor_type"] == "microphone"
        assert "db_level" in data
        assert 0 <= data["db_level"] <= 100
        assert "noise_classification" in data
        assert "mock_mode" in data

    def test_capture_microphone_data_custom_duration(self):
        """Test GET /api/sensors/microphone/capture with custom duration."""
        response = client.get("/api/sensors/microphone/capture?duration=0.5")
        assert response.status_code == 200
        data = response.json()
        assert "sample_duration" in data
        assert data["sample_duration"] == 0.5

    def test_post_noise_data(self):
        """Test POST /api/sensors/microphone/noise."""
        response = client.post("/api/sensors/microphone/noise?db_level=45.0")
        assert response.status_code == 201
        data = response.json()
        assert "message" in data

    def test_post_noise_data_invalid_low(self):
        """Test POST /api/sensors/microphone/noise with invalid low value."""
        response = client.post("/api/sensors/microphone/noise?db_level=-5")
        assert response.status_code == 400

    def test_post_noise_data_invalid_high(self):
        """Test POST /api/sensors/microphone/noise with invalid high value."""
        response = client.post("/api/sensors/microphone/noise?db_level=105")
        assert response.status_code == 400


class TestSensorManagerEndpoints:
    """Tests for sensor manager endpoints (Phase 5)."""

    def test_get_manager_status(self):
        """Test GET /api/sensors/manager/status returns status."""
        response = client.get("/api/sensors/manager/status")
        assert response.status_code == 200
        data = response.json()
        assert "manager" in data
        assert "sensors" in data
        assert "timestamp" in data
        assert "camera" in data["sensors"]
        assert "microphone" in data["sensors"]

    def test_start_manager(self):
        """Test POST /api/sensors/manager/start starts manager."""
        response = client.post("/api/sensors/manager/start")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data

        # Stop after test
        client.post("/api/sensors/manager/stop")

    def test_stop_manager(self):
        """Test POST /api/sensors/manager/stop stops manager."""
        # Start first
        client.post("/api/sensors/manager/start")

        response = client.post("/api/sensors/manager/stop")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "success" in data
        assert "status" in data

    def test_get_manager_health(self):
        """Test GET /api/sensors/manager/health returns health info."""
        response = client.get("/api/sensors/manager/health")
        assert response.status_code == 200
        data = response.json()
        assert "health_score" in data
        assert "status" in data
        assert "issues" in data
        assert "manager" in data
        assert "sensors" in data
        assert 0 <= data["health_score"] <= 100

    def test_update_manager_config(self):
        """Test PUT /api/sensors/manager/config updates configuration."""
        payload = {"polling_interval": 3.0, "auto_recover": False}
        response = client.put("/api/sensors/manager/config", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "config" in data
        assert "status" in data
        assert data["config"]["polling_interval"] == 3.0

    def test_update_manager_config_partial(self):
        """Test PUT /api/sensors/manager/config with partial update."""
        payload = {"max_retries": 5}
        response = client.put("/api/sensors/manager/config", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["config"]["max_retries"] == 5


class TestAnalyticsAPI:
    """Test analytics API endpoints (Phase 7)."""

    def test_get_aggregated_greenery_data(self):
        """Test GET /api/analytics/aggregate/greenery returns aggregated data."""
        response = client.get("/api/analytics/aggregate/greenery?period=hourly&days=1")
        assert response.status_code == 200
        data = response.json()
        assert "data_type" in data
        assert "period" in data
        assert "days" in data
        assert "count" in data
        assert "data" in data
        assert data["data_type"] == "greenery"
        assert data["period"] == "hourly"
        assert isinstance(data["data"], list)

    def test_get_aggregated_noise_data(self):
        """Test GET /api/analytics/aggregate/noise returns aggregated data."""
        response = client.get("/api/analytics/aggregate/noise?period=daily&days=7")
        assert response.status_code == 200
        data = response.json()
        assert data["data_type"] == "noise"
        assert data["period"] == "daily"
        assert data["days"] == 7

    def test_get_aggregated_invalid_type(self):
        """Test aggregation with invalid data type returns 400."""
        response = client.get("/api/analytics/aggregate/invalid")
        assert response.status_code == 400

    def test_get_aggregated_invalid_period(self):
        """Test aggregation with invalid period returns 400."""
        response = client.get("/api/analytics/aggregate/greenery?period=invalid")
        assert response.status_code == 400

    def test_get_statistics_greenery(self):
        """Test GET /api/analytics/statistics/greenery returns statistics."""
        response = client.get("/api/analytics/statistics/greenery?days=7")
        assert response.status_code == 200
        data = response.json()
        assert "data_type" in data
        assert "days" in data
        assert "statistics" in data

        stats = data["statistics"]
        assert "count" in stats
        assert "avg" in stats
        assert "min" in stats
        assert "max" in stats
        assert "stddev" in stats
        assert "median" in stats
        assert "range" in stats

    def test_get_statistics_noise(self):
        """Test GET /api/analytics/statistics/noise returns statistics."""
        response = client.get("/api/analytics/statistics/noise?days=14")
        assert response.status_code == 200
        data = response.json()
        assert data["data_type"] == "noise"
        assert data["days"] == 14

    def test_get_statistics_invalid_type(self):
        """Test statistics with invalid data type returns 400."""
        response = client.get("/api/analytics/statistics/invalid")
        assert response.status_code == 400

    def test_get_trends(self):
        """Test GET /api/analytics/trends/greenery returns trend analysis."""
        response = client.get("/api/analytics/trends/greenery?period=daily&days=7")
        assert response.status_code == 200
        data = response.json()
        assert "data_type" in data
        assert "period" in data
        assert "days" in data
        assert "trends" in data

        trends = data["trends"]
        assert "direction" in trends
        assert "slope" in trends
        assert "confidence" in trends
        assert "change_percent" in trends
        assert trends["direction"] in ["increasing", "decreasing", "stable"]

    def test_get_trends_invalid_period(self):
        """Test trends with invalid period returns 400."""
        response = client.get("/api/analytics/trends/greenery?period=invalid")
        assert response.status_code == 400

    def test_get_anomalies(self):
        """Test GET /api/analytics/anomalies/greenery returns anomaly detection."""
        response = client.get("/api/analytics/anomalies/greenery?days=7&threshold=2.0")
        assert response.status_code == 200
        data = response.json()
        assert "data_type" in data
        assert "days" in data
        assert "threshold_stddev" in data
        assert "count" in data
        assert "anomalies" in data
        assert isinstance(data["anomalies"], list)

    def test_get_anomalies_noise(self):
        """Test anomaly detection for noise data."""
        response = client.get("/api/analytics/anomalies/noise?days=3")
        assert response.status_code == 200
        data = response.json()
        assert data["data_type"] == "noise"

    def test_get_correlation(self):
        """Test GET /api/analytics/correlation returns correlation analysis."""
        response = client.get("/api/analytics/correlation?days=7")
        assert response.status_code == 200
        data = response.json()
        assert "days" in data
        assert "correlation" in data

        corr = data["correlation"]
        assert "coefficient" in corr
        assert "strength" in corr
        assert "direction" in corr


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
