"""Simple SQLite-backed session logger and historical analysis utilities.

This module creates (when required) an SQLite database file named `mindcare.db`
at the repository root and exposes functions to log session sensor readings and
to load/analyze recent session history using pandas.

Functions
- log_session_data(session_data: dict) -> int
- get_session_history(days: int = 7) -> pandas.DataFrame
- analyze_and_rank_trends(df: pandas.DataFrame) -> dict

The `session_data` dict expected keys (all optional, but recommended):
- dominant_emotion: str
- emotion_counts: dict
- avg_db: float
- noise_classification: str
- avg_green_pct: float

"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

import pandas as pd


# Place the DB at the repository root (one level above the package dir)
DB_PATH = Path(__file__).resolve().parents[1] / "mindcare.db"


def _get_conn() -> sqlite3.Connection:
    """Return a sqlite3 connection and ensure the sessions table exists."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    _ensure_table(conn)
    return conn


def _ensure_table(conn: sqlite3.Connection) -> None:
    """Create the sessions table if it does not exist."""
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            dominant_emotion TEXT,
            emotion_counts_json TEXT,
            avg_db REAL,
            noise_classification TEXT,
            avg_green_pct REAL
        )
        """
    )
    conn.commit()


def log_session_data(session_data: Dict) -> int:
    """Insert a new session row into the database.

    Args:
        session_data: dictionary containing sensor readings. Keys:
            - dominant_emotion (str)
            - emotion_counts (dict)
            - avg_db (float)
            - noise_classification (str)
            - avg_green_pct (float)

    Returns:
        The newly inserted row id.
    """
    conn = _get_conn()
    cur = conn.cursor()

    emotion_counts = session_data.get("emotion_counts") or {}
    emotion_counts_json = json.dumps(emotion_counts)

    cur.execute(
        """INSERT INTO sessions
        (dominant_emotion, emotion_counts_json, avg_db, noise_classification, avg_green_pct)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            session_data.get("dominant_emotion"),
            emotion_counts_json,
            session_data.get("avg_db"),
            session_data.get("noise_classification"),
            session_data.get("avg_green_pct"),
        ),
    )
    conn.commit()
    rowid = cur.lastrowid
    conn.close()
    return int(rowid)


def get_session_history(days: int = 7) -> pd.DataFrame:
    """Query sessions from the last `days` days and return a DataFrame.

    The returned DataFrame will have the columns from the sessions table and
    a parsed `timestamp` column (datetime dtype). If there are no rows, an
    empty DataFrame is returned.
    """
    conn = _get_conn()
    since = datetime.utcnow() - timedelta(days=days)
    query = "SELECT * FROM sessions WHERE timestamp >= ? ORDER BY timestamp ASC"
    df = pd.read_sql_query(query, conn, params=(since.isoformat(sep=" "),))
    conn.close()

    if df.empty:
        return df

    # Parse timestamp to datetime and emotion_counts JSON into dicts
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    if "emotion_counts_json" in df.columns:
        def _parse_counts(x: Optional[str]):
            try:
                return json.loads(x) if x else {}
            except Exception:
                return {}

        df["emotion_counts"] = df["emotion_counts_json"].apply(_parse_counts)

    return df


def analyze_and_rank_trends(df: pd.DataFrame) -> Dict:
    """Analyze a DataFrame of session history and return ranked statistics.

    Returns a dictionary with keys:
    - emotions_rank: {'most_common': str|None, 'least_common': str|None}
    - noisy_time_category: {'category': str|None, 'avg_db': float|None}
    - greenery_insights: {'avg_green_happy_neutral': float|None, 'avg_green_sad_angry': float|None}
    """
    if df is None or df.empty:
        return {
            "emotions_rank": {"most_common": None, "least_common": None},
            "noisy_time_category": {"category": None, "avg_db": None},
            "greenery_insights": {"avg_green_happy_neutral": None, "avg_green_sad_angry": None},
        }

    out = {}

    # Rank Emotions
    if "dominant_emotion" in df.columns:
        vc = df["dominant_emotion"].dropna().astype(str)
        if not vc.empty:
            counts = vc.value_counts()
            most = counts.idxmax()
            least = counts.idxmin()
        else:
            most = least = None
    else:
        most = least = None

    out["emotions_rank"] = {"most_common": most, "least_common": least}

    # Categorize by time of day and find category with highest avg_db
    # Define categories by hour
    def _time_category(hour: int) -> str:
        if 5 <= hour <= 11:
            return "morning"
        if 12 <= hour <= 17:
            return "afternoon"
        if 18 <= hour <= 21:
            return "evening"
        return "night"

    if "timestamp" in df.columns and "avg_db" in df.columns:
        d = df.copy()
        d = d.dropna(subset=["timestamp"]) 
        d["hour"] = d["timestamp"].dt.hour
        d["time_category"] = d["hour"].apply(_time_category)
        # Only consider numeric avg_db
        d = d[pd.to_numeric(d["avg_db"], errors="coerce").notna()]
        if not d.empty:
            grp = d.groupby("time_category")["avg_db"].mean()
            top_cat = grp.idxmax()
            top_avg = float(round(grp.max(), 2))
            noisy = {"category": top_cat, "avg_db": top_avg}
        else:
            noisy = {"category": None, "avg_db": None}
    else:
        noisy = {"category": None, "avg_db": None}

    out["noisy_time_category"] = noisy

    # Generate greenery insights for emotion groups
    # Define positive vs negative emotion sets
    positive = {"happy", "neutral"}
    negative = {"sad", "angry"}

    def _mean_green_for_emotions(df_local: pd.DataFrame, target_set: set) -> Optional[float]:
        if "dominant_emotion" not in df_local.columns or "avg_green_pct" not in df_local.columns:
            return None
        sel = df_local[~df_local["dominant_emotion"].isna()].copy()
        sel["dominant_emotion_lc"] = sel["dominant_emotion"].str.lower()
        sel = sel[sel["dominant_emotion_lc"].isin(target_set)]
        sel = sel[pd.to_numeric(sel["avg_green_pct"], errors="coerce").notna()]
        if sel.empty:
            return None
        return float(round(sel["avg_green_pct"].astype(float).mean(), 2))

    avg_pos = _mean_green_for_emotions(df, positive)
    avg_neg = _mean_green_for_emotions(df, negative)

    out["greenery_insights"] = {
        "avg_green_happy_neutral": avg_pos,
        "avg_green_sad_angry": avg_neg,
    }

    return out
