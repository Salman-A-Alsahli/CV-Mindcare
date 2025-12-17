"""
CV-Mindcare Database
-------------------
SQLite database schema and helper functions for sensor data storage.
"""

import sqlite3
import os
from contextlib import closing
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "cv_mindcare.db")

# Schema definition
SCHEMA = """
CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_type TEXT NOT NULL,
    value REAL NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS face_detection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    faces_detected INTEGER NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sound_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    avg_db REAL NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS air_quality (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ppm REAL NOT NULL,
    air_quality_level TEXT NOT NULL,
    raw_value REAL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp ON sensor_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_data_type ON sensor_data(sensor_type);
CREATE INDEX IF NOT EXISTS idx_air_quality_timestamp ON air_quality(timestamp);
CREATE INDEX IF NOT EXISTS idx_air_quality_level ON air_quality(air_quality_level);
"""


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database and create tables."""
    with closing(_get_connection()) as conn:
        conn.executescript(SCHEMA)
        conn.commit()


# Helper functions


def insert_sensor_data(sensor_type: str, value: float) -> None:
    with closing(_get_connection()) as conn:
        conn.execute(
            "INSERT INTO sensor_data (sensor_type, value) VALUES (?, ?)", (sensor_type, value)
        )
        conn.commit()


def insert_face_detection(faces_detected: int) -> None:
    with closing(_get_connection()) as conn:
        conn.execute("INSERT INTO face_detection (faces_detected) VALUES (?)", (faces_detected,))
        conn.commit()


def insert_sound_analysis(avg_db: float) -> None:
    with closing(_get_connection()) as conn:
        conn.execute("INSERT INTO sound_analysis (avg_db) VALUES (?)", (avg_db,))
        conn.commit()


def get_recent_sensor_data(limit: int = 10) -> List[Dict[str, Any]]:
    with closing(_get_connection()) as conn:
        rows = conn.execute(
            "SELECT sensor_type, value, timestamp FROM sensor_data ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_latest_face_detection() -> Optional[Dict[str, Any]]:
    with closing(_get_connection()) as conn:
        row = conn.execute(
            "SELECT faces_detected, timestamp FROM face_detection ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None


def get_latest_sound_analysis() -> Optional[Dict[str, Any]]:
    with closing(_get_connection()) as conn:
        row = conn.execute(
            "SELECT avg_db, timestamp FROM sound_analysis ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None


def insert_air_quality(
    ppm: float, air_quality_level: str, raw_value: Optional[float] = None
) -> None:
    """Insert air quality measurement into database."""
    with closing(_get_connection()) as conn:
        conn.execute(
            "INSERT INTO air_quality (ppm, air_quality_level, raw_value) VALUES (?, ?, ?)",
            (ppm, air_quality_level, raw_value),
        )
        conn.commit()


def get_latest_air_quality() -> Optional[Dict[str, Any]]:
    """Get the most recent air quality measurement."""
    with closing(_get_connection()) as conn:
        row = conn.execute(
            "SELECT ppm, air_quality_level, raw_value, timestamp FROM air_quality ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None


def get_recent_air_quality(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent air quality measurements."""
    with closing(_get_connection()) as conn:
        rows = conn.execute(
            "SELECT ppm, air_quality_level, raw_value, timestamp FROM air_quality ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_sensor_status(window_minutes: int = 10) -> Dict[str, bool]:
    cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
    with closing(_get_connection()) as conn:
        rows = conn.execute(
            "SELECT sensor_type, MAX(timestamp) AS last_seen FROM sensor_data GROUP BY sensor_type"
        ).fetchall()

    status: Dict[str, bool] = {}
    for row in rows:
        last_seen = row["last_seen"]
        try:
            last_dt = datetime.strptime(last_seen, "%Y-%m-%d %H:%M:%S")
        except (TypeError, ValueError):
            status[row["sensor_type"]] = False
            continue
        status[row["sensor_type"]] = last_dt >= cutoff
    return status


def get_system_stats() -> Dict[str, Any]:
    with closing(_get_connection()) as conn:
        sensor_points = conn.execute("SELECT COUNT(*) FROM sensor_data").fetchone()[0]
        face_points = conn.execute("SELECT COUNT(*) FROM face_detection").fetchone()[0]
        sound_points = conn.execute("SELECT COUNT(*) FROM sound_analysis").fetchone()[0]
        air_quality_points = conn.execute("SELECT COUNT(*) FROM air_quality").fetchone()[0]

    return {
        "data_points": sensor_points + face_points + sound_points + air_quality_points,
        "sensor_points": sensor_points,
        "face_points": face_points,
        "sound_points": sound_points,
        "air_quality_points": air_quality_points,
    }


class Database:
    """Database class wrapper for ContextEngine compatibility.
    
    This class provides a high-level interface for the ContextEngine to access
    sensor data from the SQLite database. It wraps the lower-level database
    functions to provide a more convenient API.
    
    Thread Safety:
        Each method creates its own database connection using the context manager
        pattern, making it safe to use from multiple threads.
    
    Methods:
        get_greenery_data: Retrieve greenery sensor measurements
        get_noise_data: Retrieve noise sensor measurements
    """

    def __init__(self, db_path: str = DB_PATH):
        """Initialize Database wrapper.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        # Ensure database exists
        init_db()

    def _get_sensor_data(self, sensor_type: str, since: Optional[datetime] = None) -> List[tuple]:
        """Get sensor data of a specific type since specified time.
        
        Args:
            sensor_type: Type of sensor data to retrieve (e.g., 'greenery', 'noise')
            since: Get data after this datetime (optional)
            
        Returns:
            List of tuples: (timestamp, value)
        """
        with closing(_get_connection()) as conn:
            if since:
                since_str = since.strftime("%Y-%m-%d %H:%M:%S")
                rows = conn.execute(
                    "SELECT timestamp, value FROM sensor_data WHERE sensor_type = ? AND timestamp >= ? ORDER BY timestamp",
                    (sensor_type, since_str)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT timestamp, value FROM sensor_data WHERE sensor_type = ? ORDER BY timestamp",
                    (sensor_type,)
                ).fetchall()
        
        return [(row[0], row[1]) for row in rows]

    def get_greenery_data(self, since: Optional[datetime] = None) -> List[tuple]:
        """Get greenery sensor data since specified time.
        
        Args:
            since: Get data after this datetime (optional)
            
        Returns:
            List of tuples: (timestamp, greenery_percentage)
        """
        return self._get_sensor_data("greenery", since)

    def get_noise_data(self, since: Optional[datetime] = None) -> List[tuple]:
        """Get noise sensor data since specified time.
        
        Args:
            since: Get data after this datetime (optional)
            
        Returns:
            List of tuples: (timestamp, noise_level)
        """
        return self._get_sensor_data("noise", since)

    def get_air_quality_data(self, since: Optional[datetime] = None) -> List[tuple]:
        """Get air quality sensor data since specified time.
        
        Args:
            since: Get data after this datetime (optional)
            
        Returns:
            List of tuples: (timestamp, ppm_value)
        """
        with closing(_get_connection()) as conn:
            if since:
                since_str = since.strftime("%Y-%m-%d %H:%M:%S")
                rows = conn.execute(
                    "SELECT timestamp, ppm FROM air_quality WHERE timestamp >= ? ORDER BY timestamp",
                    (since_str,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT timestamp, ppm FROM air_quality ORDER BY timestamp"
                ).fetchall()
        
        return [(row[0], row[1]) for row in rows]


# Ensure database exists when module is imported
init_db()
