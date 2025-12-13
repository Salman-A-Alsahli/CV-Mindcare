"""
Integration Tests for Air Quality Sensor with API and Database
---------------------------------------------------------------
Tests end-to-end integration of MQ-135 sensor with API endpoints and database.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend.database import (
    init_db,
    insert_air_quality,
    get_latest_air_quality,
    get_recent_air_quality
)
import tempfile
import os


@pytest.fixture
def test_db():
    """Create temporary test database."""
    # Use temporary database for tests
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    # Monkey-patch the database path
    import backend.database as db_module
    original_db_path = db_module.DB_PATH
    db_module.DB_PATH = temp_db.name
    
    # Initialize database
    init_db()
    
    yield temp_db.name
    
    # Cleanup
    db_module.DB_PATH = original_db_path
    try:
        os.unlink(temp_db.name)
    except Exception:
        pass


@pytest.fixture
def client(test_db):
    """Create test client."""
    return TestClient(app)


class TestAirQualityAPIIntegration:
    """Integration tests for air quality API endpoints."""
    
    def test_air_quality_status_endpoint(self, client):
        """Test air quality sensor status endpoint."""
        response = client.get("/api/sensors/air_quality/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['sensor_type'] == 'air_quality'
        assert 'available' in data
        assert 'backend' in data
        assert 'status' in data
    
    def test_air_quality_capture_endpoint(self, client):
        """Test air quality sensor capture endpoint."""
        response = client.get("/api/sensors/air_quality/capture")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have all required fields
        assert 'timestamp' in data
        assert 'ppm' in data
        assert 'air_quality_level' in data
        assert 'sensor_type' in data
        
        # PPM should be valid
        assert data['ppm'] >= 0
        
        # Air quality level should be valid
        valid_levels = ['excellent', 'good', 'moderate', 'poor', 'hazardous']
        assert data['air_quality_level'] in valid_levels
    
    def test_post_air_quality_data(self, client):
        """Test posting air quality data manually."""
        payload = {
            "ppm": 75.5,
            "air_quality_level": "good",
            "raw_value": 250.0
        }
        
        response = client.post("/api/sensors/air_quality/data", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data['message'] == 'air quality data recorded'
    
    def test_post_air_quality_invalid_level(self, client):
        """Test posting air quality data with invalid level."""
        payload = {
            "ppm": 75.5,
            "air_quality_level": "invalid_level",
            "raw_value": 250.0
        }
        
        response = client.post("/api/sensors/air_quality/data", json=payload)
        
        assert response.status_code == 400
    
    def test_post_air_quality_negative_ppm(self, client):
        """Test posting air quality data with negative PPM."""
        payload = {
            "ppm": -10.0,
            "air_quality_level": "good"
        }
        
        response = client.post("/api/sensors/air_quality/data", json=payload)
        
        assert response.status_code == 400
    
    def test_get_latest_air_quality(self, client):
        """Test getting latest air quality measurement."""
        # First, post some data
        payload = {
            "ppm": 125.0,
            "air_quality_level": "moderate",
            "raw_value": 400.0
        }
        client.post("/api/sensors/air_quality/data", json=payload)
        
        # Now get the latest
        response = client.get("/api/air_quality")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['ppm'] == 125.0
        assert data['air_quality_level'] == 'moderate'
        assert 'last_measurement' in data
    
    def test_get_recent_air_quality(self, client):
        """Test getting recent air quality measurements."""
        # Post multiple measurements
        for i in range(5):
            payload = {
                "ppm": 50.0 + i * 10,
                "air_quality_level": "good"
            }
            client.post("/api/sensors/air_quality/data", json=payload)
        
        # Get recent measurements
        response = client.get("/api/air_quality/recent?limit=3")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['count'] == 3
        assert len(data['measurements']) == 3
    
    def test_get_recent_air_quality_invalid_limit(self, client):
        """Test getting recent air quality with invalid limit."""
        response = client.get("/api/air_quality/recent?limit=2000")
        
        assert response.status_code == 400


class TestAirQualityDatabaseIntegration:
    """Integration tests for air quality database operations."""
    
    def test_insert_and_retrieve_air_quality(self, test_db):
        """Test inserting and retrieving air quality data."""
        # Insert data
        insert_air_quality(ppm=85.5, air_quality_level='good', raw_value=275.0)
        
        # Retrieve latest
        latest = get_latest_air_quality()
        
        assert latest is not None
        assert latest['ppm'] == 85.5
        assert latest['air_quality_level'] == 'good'
        assert latest['raw_value'] == 275.0
        assert 'timestamp' in latest
    
    def test_get_recent_air_quality_data(self, test_db):
        """Test retrieving recent air quality measurements."""
        # Insert multiple measurements
        for i in range(10):
            insert_air_quality(ppm=50.0 + i * 5, air_quality_level='good')
        
        # Retrieve recent (default 10)
        recent = get_recent_air_quality()
        
        assert len(recent) == 10
        
        # Most recent should be first
        assert recent[0]['ppm'] == 95.0  # Last inserted
        assert recent[-1]['ppm'] == 50.0  # First inserted
    
    def test_get_recent_with_limit(self, test_db):
        """Test retrieving limited recent air quality measurements."""
        # Insert multiple measurements
        for i in range(20):
            insert_air_quality(ppm=50.0 + i, air_quality_level='good')
        
        # Retrieve with limit
        recent = get_recent_air_quality(limit=5)
        
        assert len(recent) == 5


class TestEndToEndAirQualityFlow:
    """End-to-end integration tests for air quality sensor."""
    
    def test_complete_air_quality_workflow(self, client):
        """Test complete workflow: capture -> store -> retrieve."""
        # Step 1: Check sensor status
        status_response = client.get("/api/sensors/air_quality/status")
        assert status_response.status_code == 200
        
        # Step 2: Capture data (will use mock mode)
        capture_response = client.get("/api/sensors/air_quality/capture")
        assert capture_response.status_code == 200
        capture_data = capture_response.json()
        
        # Step 3: Verify data was stored (if not mock mode)
        if not capture_data.get('mock_mode', False):
            latest_response = client.get("/api/air_quality")
            assert latest_response.status_code == 200
            latest_data = latest_response.json()
            
            # Should match captured data
            assert latest_data['ppm'] == capture_data['ppm']
            assert latest_data['air_quality_level'] == capture_data['air_quality_level']
    
    def test_air_quality_in_sensors_list(self, client):
        """Test that air quality sensor appears in sensors list."""
        response = client.get("/api/sensors")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'status' in data
        assert 'air_quality' in data['status']
    
    def test_sensor_manager_includes_air_quality(self, client):
        """Test that sensor manager includes air quality sensor."""
        response = client.get("/api/sensors/manager/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'sensors' in data
        assert 'air_quality' in data['sensors']
        
        # Check air quality sensor status
        aq_status = data['sensors']['air_quality']
        assert 'status' in aq_status
        assert 'name' in aq_status
        assert aq_status['name'] == 'MQ-135 Air Quality Sensor'


class TestAirQualityDataValidation:
    """Tests for air quality data validation."""
    
    def test_all_air_quality_levels(self, client):
        """Test posting data with all valid air quality levels."""
        levels = ['excellent', 'good', 'moderate', 'poor', 'hazardous']
        
        for level in levels:
            payload = {
                "ppm": 100.0,
                "air_quality_level": level
            }
            
            response = client.post("/api/sensors/air_quality/data", json=payload)
            assert response.status_code == 201
    
    def test_air_quality_ppm_boundary_values(self, client):
        """Test PPM boundary values."""
        # Test zero PPM
        payload = {"ppm": 0.0, "air_quality_level": "excellent"}
        response = client.post("/api/sensors/air_quality/data", json=payload)
        assert response.status_code == 201
        
        # Test high PPM
        payload = {"ppm": 500.0, "air_quality_level": "hazardous"}
        response = client.post("/api/sensors/air_quality/data", json=payload)
        assert response.status_code == 201
