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
            "INSERT INTO sensor_data (sensor_type, value) VALUES (?, ?)",
            (sensor_type, value)
        )
        conn.commit()


def insert_face_detection(faces_detected: int) -> None:
    with closing(_get_connection()) as conn:
        conn.execute(
            "INSERT INTO face_detection (faces_detected) VALUES (?)",
            (faces_detected,)
        )
        conn.commit()


def insert_sound_analysis(avg_db: float) -> None:
    with closing(_get_connection()) as conn:
        conn.execute(
            "INSERT INTO sound_analysis (avg_db) VALUES (?)",
            (avg_db,)
        )
        conn.commit()


def get_recent_sensor_data(limit: int = 10) -> List[Dict[str, Any]]:
    with closing(_get_connection()) as conn:
        rows = conn.execute(
            "SELECT sensor_type, value, timestamp FROM sensor_data ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(row) for row in rows]


def get_latest_face_detection() -> Optional[Dict[str, Any]]:
    with closing(_get_connection()) as conn:
        row = conn.execute(
            "SELECT faces_detected, timestamp FROM face_detection ORDER BY timestamp DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None


def get_latest_sound_analysis() -> Optional[Dict[str, Any]]:
    with closing(_get_connection()) as conn:
        row = conn.execute(
            "SELECT avg_db, timestamp FROM sound_analysis ORDER BY timestamp DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None


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

    return {
        "data_points": sensor_points + face_points + sound_points,
        "sensor_points": sensor_points,
        "face_points": face_points,
        "sound_points": sound_points
    }


# Ensure database exists when module is imported
init_db()
