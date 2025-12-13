"""
Unit Tests for Database Functions
--------------------------------
Tests for database.py CRUD operations.
"""

import pytest
import os
import tempfile
from backend import database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create temp file
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Store original path
    original_path = database.DB_PATH

    # Use temp path
    database.DB_PATH = path
    database.init_db()

    yield path

    # Cleanup
    database.DB_PATH = original_path
    if os.path.exists(path):
        os.remove(path)


class TestDatabaseInitialization:
    """Tests for database initialization."""

    def test_init_db_creates_tables(self, temp_db):
        """Test that init_db creates all required tables."""
        conn = database._get_connection()
        cursor = conn.cursor()

        # Check sensor_data table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sensor_data'")
        assert cursor.fetchone() is not None

        # Check face_detection table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='face_detection'"
        )
        assert cursor.fetchone() is not None

        # Check sound_analysis table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sound_analysis'"
        )
        assert cursor.fetchone() is not None

        conn.close()


class TestSensorDataFunctions:
    """Tests for sensor data CRUD operations."""

    def test_insert_sensor_data(self, temp_db):
        """Test inserting sensor data."""
        database.insert_sensor_data("test_sensor", 42.5)

        # Verify insertion
        recent = database.get_recent_sensor_data(limit=1)
        assert len(recent) == 1
        assert recent[0]["sensor_type"] == "test_sensor"
        assert recent[0]["value"] == 42.5

    def test_get_recent_sensor_data(self, temp_db):
        """Test retrieving recent sensor data."""
        # Insert multiple records
        for i in range(5):
            database.insert_sensor_data(f"sensor_{i}", float(i))

        # Get recent with limit
        recent = database.get_recent_sensor_data(limit=3)
        assert len(recent) == 3

        # Should be in reverse chronological order
        assert recent[0]["value"] == 4.0
        assert recent[1]["value"] == 3.0
        assert recent[2]["value"] == 2.0

    def test_get_recent_sensor_data_empty(self, temp_db):
        """Test getting recent data from empty database."""
        recent = database.get_recent_sensor_data(limit=10)
        assert len(recent) == 0


class TestFaceDetectionFunctions:
    """Tests for face detection CRUD operations."""

    def test_insert_face_detection(self, temp_db):
        """Test inserting face detection data."""
        database.insert_face_detection(2)

        # Verify insertion
        latest = database.get_latest_face_detection()
        assert latest is not None
        assert latest["faces_detected"] == 2

    def test_get_latest_face_detection(self, temp_db):
        """Test getting latest face detection."""
        # Insert multiple records
        database.insert_face_detection(1)
        database.insert_face_detection(2)
        database.insert_face_detection(3)

        # Should get the latest
        latest = database.get_latest_face_detection()
        assert latest["faces_detected"] == 3

    def test_get_latest_face_detection_empty(self, temp_db):
        """Test getting latest from empty table."""
        latest = database.get_latest_face_detection()
        assert latest is None


class TestSoundAnalysisFunctions:
    """Tests for sound analysis CRUD operations."""

    def test_insert_sound_analysis(self, temp_db):
        """Test inserting sound analysis data."""
        database.insert_sound_analysis(65.5)

        # Verify insertion
        latest = database.get_latest_sound_analysis()
        assert latest is not None
        assert latest["avg_db"] == 65.5

    def test_get_latest_sound_analysis(self, temp_db):
        """Test getting latest sound analysis."""
        # Insert multiple records
        database.insert_sound_analysis(50.0)
        database.insert_sound_analysis(60.0)
        database.insert_sound_analysis(70.0)

        # Should get the latest
        latest = database.get_latest_sound_analysis()
        assert latest["avg_db"] == 70.0

    def test_get_latest_sound_analysis_empty(self, temp_db):
        """Test getting latest from empty table."""
        latest = database.get_latest_sound_analysis()
        assert latest is None


class TestStatisticsFunctions:
    """Tests for statistics and aggregation functions."""

    def test_get_sensor_status_empty(self, temp_db):
        """Test sensor status with no data."""
        status = database.get_sensor_status()
        assert isinstance(status, dict)
        assert len(status) == 0

    def test_get_sensor_status_with_data(self, temp_db):
        """Test sensor status with recent data."""
        database.insert_sensor_data("camera", 1.0)
        database.insert_sensor_data("microphone", 1.0)

        status = database.get_sensor_status()
        assert "camera" in status
        assert "microphone" in status

    def test_get_system_stats(self, temp_db):
        """Test getting system statistics."""
        # Insert test data
        database.insert_sensor_data("test", 1.0)
        database.insert_face_detection(1)
        database.insert_sound_analysis(50.0)

        stats = database.get_system_stats()
        assert stats["data_points"] == 3
        assert stats["sensor_points"] == 1
        assert stats["face_points"] == 1
        assert stats["sound_points"] == 1

    def test_get_system_stats_empty(self, temp_db):
        """Test statistics on empty database."""
        stats = database.get_system_stats()
        assert stats["data_points"] == 0
        assert stats["sensor_points"] == 0
        assert stats["face_points"] == 0
        assert stats["sound_points"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
