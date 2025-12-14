"""CV-Mindcare Backend API."""

from datetime import datetime
from typing import Dict, Optional

from fastapi import FastAPI, status, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import psutil

from .database import (
    init_db,
    insert_sensor_data,
    insert_face_detection,
    insert_sound_analysis,
    insert_air_quality,
    get_recent_sensor_data,
    get_latest_face_detection,
    get_latest_sound_analysis,
    get_latest_air_quality,
    get_recent_air_quality,
    get_sensor_status,
    get_system_stats,
)

app = FastAPI(
    title="CV-Mindcare API",
    description="Privacy-first wellness monitoring system",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SensorData(BaseModel):
    sensor_type: str
    value: float
    timestamp: Optional[str] = None


class FaceDetection(BaseModel):
    faces_detected: int
    timestamp: Optional[str] = None


class SoundSample(BaseModel):
    avg_db: float
    timestamp: Optional[str] = None


class AirQualityData(BaseModel):
    """Air quality measurement data."""

    ppm: float
    air_quality_level: str
    raw_value: Optional[float] = None
    timestamp: Optional[str] = None


@app.on_event("startup")
async def startup() -> None:
    init_db()


@app.get("/")
async def root() -> Dict[str, str]:
    return {
        "status": "online",
        "version": "0.3.0",
        "name": "CV-Mindcare API",
    }


@app.get("/api/health")
async def health() -> Dict[str, str]:
    """Health check endpoint for monitoring and load balancers."""
    return {"status": "ok"}


@app.get("/api/sensors")
async def get_sensors() -> Dict:
    status_map = get_sensor_status()
    recent = get_recent_sensor_data(limit=10)

    # Check air quality sensor availability
    air_quality_available = False
    try:
        from .sensors.air_quality import check_air_quality_available

        air_quality_available = check_air_quality_available()
    except Exception:
        pass

    return {
        "status": {
            "camera": status_map.get("camera", False),
            "microphone": status_map.get("microphone", False),
            "air_quality": air_quality_available,
            "system_resources": True,
        },
        "recent": recent,
    }


@app.post("/api/sensors", status_code=status.HTTP_201_CREATED)
async def post_sensor_data(payload: SensorData) -> Dict[str, str]:
    insert_sensor_data(payload.sensor_type, payload.value)
    return {"message": "sensor data recorded"}


@app.get("/api/face")
async def get_face() -> Dict[str, object]:
    latest = get_latest_face_detection()
    return {
        "faces_detected": latest["faces_detected"] if latest else 0,
        "last_detection": latest["timestamp"] if latest else None,
    }


@app.post("/api/face", status_code=status.HTTP_201_CREATED)
async def post_face_detection(payload: FaceDetection) -> Dict[str, str]:
    insert_face_detection(payload.faces_detected)
    return {"message": "face detection recorded"}


@app.get("/api/sound")
async def get_sound() -> Dict[str, object]:
    latest = get_latest_sound_analysis()
    return {
        "avg_db": latest["avg_db"] if latest else 0.0,
        "last_sample": latest["timestamp"] if latest else None,
    }


@app.post("/api/sound", status_code=status.HTTP_201_CREATED)
async def post_sound(payload: SoundSample) -> Dict[str, str]:
    insert_sound_analysis(payload.avg_db)
    return {"message": "sound sample recorded"}


@app.get("/api/stats")
async def get_stats() -> Dict[str, object]:
    stats = get_system_stats()
    sensor_status = get_sensor_status()
    return {
        "uptime": 0,
        "active_sensors": sum(1 for value in sensor_status.values() if value),
        "data_points": stats["data_points"],
        "breakdown": stats,
    }


@app.get("/api/live")
async def get_live() -> Dict[str, object]:
    face = get_latest_face_detection() or {"faces_detected": 0, "timestamp": None}
    sound = get_latest_sound_analysis() or {"avg_db": 0.0, "timestamp": None}
    recent = get_recent_sensor_data(limit=5)
    dominant_emotion = next(
        (str(record["value"]) for record in recent if record["sensor_type"].lower() == "emotion"),
        "neutral",
    )
    emotions = {"neutral": 1.0}
    for record in recent:
        if record["sensor_type"].lower().startswith("emotion_"):
            emotions[record["sensor_type"].split("_", 1)[-1]] = float(record["value"])

    system_stats = {
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory_percent": psutil.virtual_memory().percent,
    }

    return {
        "faces_detected": face["faces_detected"],
        "avg_db": sound["avg_db"],
        "dominant_emotion": dominant_emotion,
        "avg_green_pct": next(
            (record["value"] for record in recent if record["sensor_type"].lower() == "greenery"),
            0.0,
        ),
        "last_updated": datetime.utcnow().isoformat(),
        "emotions": emotions,
        "stats": system_stats,
    }


@app.post("/api/control/stop")
async def stop_collection() -> Dict[str, str]:
    return {"message": "data collection stop requested"}


# Camera Sensor Endpoints (Phase 3)


@app.get("/api/sensors/camera/status")
async def get_camera_status() -> Dict[str, object]:
    """
    Get camera sensor status.

    Returns sensor availability and configuration information.
    """
    try:
        from .sensors.camera_sensor import check_camera_available

        available = check_camera_available()
        return {
            "sensor_type": "camera",
            "available": available,
            "backend": "opencv",
            "status": "available" if available else "unavailable",
        }
    except Exception as e:
        return {
            "sensor_type": "camera",
            "available": False,
            "status": "error",
            "error": str(e),
        }


@app.get("/api/sensors/camera/capture")
async def capture_camera_data() -> Dict[str, object]:
    """
    Capture camera data with greenery detection.

    Returns greenery percentage and analysis metadata.
    Automatically falls back to mock mode if hardware unavailable.
    """
    try:
        from .sensors.camera_sensor import get_camera_reading

        data = get_camera_reading()

        # Store greenery data in database
        if not data.get("mock_mode", False):
            greenery_pct = data.get("greenery_percentage", 0.0)
            insert_sensor_data("greenery", greenery_pct)

        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Camera capture failed: {str(e)}",
        )


@app.post("/api/sensors/camera/greenery", status_code=status.HTTP_201_CREATED)
async def post_greenery_data(greenery_percentage: float) -> Dict[str, str]:
    """
    Manually submit greenery detection data.

    Args:
        greenery_percentage: Percentage of green pixels (0-100)

    Returns:
        Confirmation message
    """
    if not 0 <= greenery_percentage <= 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Greenery percentage must be between 0 and 100",
        )

    insert_sensor_data("greenery", greenery_percentage)
    return {"message": "greenery data recorded"}


# Microphone Sensor Endpoints (Phase 4)


@app.get("/api/sensors/microphone/status")
async def get_microphone_status() -> Dict[str, object]:
    """
    Get microphone sensor status.

    Returns sensor availability and configuration information.
    """
    try:
        from .sensors.microphone_sensor import check_microphone_available

        available = check_microphone_available()
        return {
            "sensor_type": "microphone",
            "available": available,
            "backend": "sounddevice",
            "status": "available" if available else "unavailable",
        }
    except Exception as e:
        return {
            "sensor_type": "microphone",
            "available": False,
            "status": "error",
            "error": str(e),
        }


@app.get("/api/sensors/microphone/capture")
async def capture_microphone_data(duration: float = 1.0) -> Dict[str, object]:
    """
    Capture microphone data with noise level analysis.

    Args:
        duration: Sample duration in seconds (default: 1.0)

    Returns noise level analysis including dB level and classification.
    Automatically falls back to mock mode if hardware unavailable.
    """
    try:
        from .sensors.microphone_sensor import get_microphone_reading

        data = get_microphone_reading(duration=duration)

        # Store noise data in database
        if not data.get("mock_mode", False):
            db_level = data.get("db_level", 0.0)
            insert_sensor_data("noise", db_level)

        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Microphone capture failed: {str(e)}",
        )


@app.post("/api/sensors/microphone/noise", status_code=status.HTTP_201_CREATED)
async def post_noise_data(db_level: float) -> Dict[str, str]:
    """
    Manually submit noise level data.

    Args:
        db_level: Noise level in dB (0-100 normalized)

    Returns:
        Confirmation message
    """
    if not 0 <= db_level <= 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Noise level must be between 0 and 100"
        )

    insert_sensor_data("noise", db_level)
    return {"message": "noise data recorded"}


# Air Quality Sensor Endpoints (Phase 1: MQ-135 Integration)


@app.get("/api/sensors/air_quality/status")
async def get_air_quality_status() -> Dict[str, object]:
    """
    Get air quality sensor status.

    Returns sensor availability and configuration information.
    """
    try:
        from .sensors.air_quality import check_air_quality_available

        available = check_air_quality_available()
        return {
            "sensor_type": "air_quality",
            "available": available,
            "backend": "mq135",
            "status": "available" if available else "unavailable",
        }
    except Exception as e:
        return {
            "sensor_type": "air_quality",
            "available": False,
            "status": "error",
            "error": str(e),
        }


@app.get("/api/sensors/air_quality/capture")
async def capture_air_quality_data() -> Dict[str, object]:
    """
    Capture air quality data from MQ-135 sensor.

    Returns PPM concentration and air quality level classification.
    Automatically falls back to mock mode if hardware unavailable.
    """
    try:
        from .sensors.air_quality import get_air_quality_reading

        data = get_air_quality_reading()

        # Store air quality data in database
        if not data.get("mock_mode", False):
            ppm = data.get("ppm", 0.0)
            air_quality_level = data.get("air_quality_level", "unknown")
            raw_value = data.get("raw_value", None)
            insert_air_quality(ppm, air_quality_level, raw_value)

        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Air quality capture failed: {str(e)}",
        )


@app.post("/api/sensors/air_quality/data", status_code=status.HTTP_201_CREATED)
async def post_air_quality_data(payload: AirQualityData) -> Dict[str, str]:
    """
    Manually submit air quality measurement data.

    Args:
        payload: Air quality data with PPM and level classification

    Returns:
        Confirmation message
    """
    # Validate air quality level
    valid_levels = ["excellent", "good", "moderate", "poor", "hazardous"]
    if payload.air_quality_level.lower() not in valid_levels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid air quality level. Must be one of: {valid_levels}",
        )

    if payload.ppm < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="PPM must be non-negative"
        )

    insert_air_quality(payload.ppm, payload.air_quality_level, payload.raw_value)
    return {"message": "air quality data recorded"}


@app.get("/api/air_quality")
async def get_air_quality() -> Dict[str, object]:
    """
    Get latest air quality measurement.

    Returns:
        Latest PPM reading, air quality level, and timestamp
    """
    latest = get_latest_air_quality()
    return {
        "ppm": latest["ppm"] if latest else 0.0,
        "air_quality_level": latest["air_quality_level"] if latest else "unknown",
        "raw_value": latest.get("raw_value") if latest else None,
        "last_measurement": latest["timestamp"] if latest else None,
    }


@app.get("/api/air_quality/recent")
async def get_recent_air_quality_data(limit: int = 10) -> Dict[str, object]:
    """
    Get recent air quality measurements.

    Args:
        limit: Maximum number of recent measurements to return (default: 10)

    Returns:
        List of recent air quality measurements
    """
    if limit < 1 or limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Limit must be between 1 and 1000"
        )

    recent = get_recent_air_quality(limit=limit)
    return {"count": len(recent), "measurements": recent}


@app.get("/api/context")
async def get_context(days: int = 30) -> Dict[str, object]:
    """Get context payload combining current readings with historical summary.

    Args:
        days: Number of days of history to analyze (default: 30)

    Returns:
        Dict containing current_readings and historical_summary
    """
    # Get current live data
    live_data = await get_live()

    # Get historical data from database
    recent_data = get_recent_sensor_data(limit=100)

    # Calculate basic statistics from recent data
    emotions = {}
    noise_levels = []
    greenery_levels = []

    for record in recent_data:
        sensor_type = record.get("sensor_type", "").lower()
        value = record.get("value", 0)

        if "emotion" in sensor_type:
            emotion_name = sensor_type.replace("emotion_", "").replace("emotion", "neutral")
            emotions[emotion_name] = emotions.get(emotion_name, 0) + 1
        elif sensor_type == "noise" or sensor_type == "sound":
            noise_levels.append(value)
        elif sensor_type == "greenery":
            greenery_levels.append(value)

    # Determine most frequent emotion
    most_frequent_emotion = max(emotions.items(), key=lambda x: x[1])[0] if emotions else "neutral"

    # Calculate average noise level
    avg_noise = (
        sum(noise_levels) / len(noise_levels) if noise_levels else live_data.get("avg_db", 0)
    )

    # Categorize noise time (simplified - would need timestamp analysis for full implementation)
    noise_category = "quiet" if avg_noise < 50 else "moderate" if avg_noise < 70 else "loud"

    historical_summary = {
        "most_frequent_emotion": most_frequent_emotion,
        "noisiest_time_of_day": noise_category,
        "avg_noise_level": round(avg_noise, 2),
        "avg_greenery": (
            round(sum(greenery_levels) / len(greenery_levels), 2) if greenery_levels else 0.0
        ),
        "data_points": len(recent_data),
    }

    return {
        "current_readings": {
            "dominant_emotion": live_data.get("dominant_emotion"),
            "avg_db": live_data.get("avg_db"),
            "avg_green_pct": live_data.get("avg_green_pct"),
            "faces_detected": live_data.get("faces_detected"),
            "last_updated": live_data.get("last_updated"),
        },
        "historical_summary": historical_summary,
    }


# Sensor Manager Endpoints (Phase 5)
_sensor_manager = None


def get_sensor_manager():
    """Get or create the global sensor manager instance."""
    global _sensor_manager
    if _sensor_manager is None:
        from .sensors.sensor_manager import SensorManager

        _sensor_manager = SensorManager(
            config={
                "polling_interval": 5.0,
                "auto_start": False,  # Manual start via API
                "auto_recover": True,
                "max_retries": 3,
            }
        )
    return _sensor_manager


@app.get("/api/sensors/manager/status")
async def get_manager_status() -> Dict[str, object]:
    """
    Get sensor manager status.

    Returns:
        Status of manager and all managed sensors
    """
    try:
        manager = get_sensor_manager()
        return manager.get_all_status()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get manager status: {str(e)}",
        )


@app.post("/api/sensors/manager/start", status_code=status.HTTP_200_OK)
async def start_manager() -> Dict[str, object]:
    """
    Start sensor manager and all sensors.

    Returns:
        Status after starting
    """
    try:
        manager = get_sensor_manager()
        success = manager.start_all()

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start any sensors",
            )

        return {"message": "Sensor manager started", "status": manager.get_all_status()}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start manager: {str(e)}",
        )


@app.post("/api/sensors/manager/stop", status_code=status.HTTP_200_OK)
async def stop_manager() -> Dict[str, object]:
    """
    Stop sensor manager and all sensors.

    Returns:
        Status after stopping
    """
    try:
        manager = get_sensor_manager()
        success = manager.stop_all()

        return {
            "message": "Sensor manager stopped",
            "success": success,
            "status": manager.get_all_status(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop manager: {str(e)}",
        )


@app.get("/api/sensors/manager/health")
async def get_manager_health() -> Dict[str, object]:
    """
    Get sensor manager health metrics.

    Returns:
        Detailed health information with scores and diagnostics
    """
    try:
        manager = get_sensor_manager()
        return manager.get_health()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get manager health: {str(e)}",
        )


class ManagerConfig(BaseModel):
    """Configuration model for sensor manager."""

    polling_interval: Optional[float] = None
    auto_recover: Optional[bool] = None
    max_retries: Optional[int] = None


@app.put("/api/sensors/manager/config", status_code=status.HTTP_200_OK)
async def update_manager_config(config: ManagerConfig) -> Dict[str, object]:
    """
    Update sensor manager configuration.

    Args:
        config: New configuration values

    Returns:
        Updated configuration and status
    """
    try:
        manager = get_sensor_manager()
        config_dict = config.model_dump(exclude_none=True)

        success = manager.update_config(config_dict)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update configuration"
            )

        return {
            "message": "Configuration updated",
            "config": config_dict,
            "status": manager.get_all_status(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update config: {str(e)}",
        )


# WebSocket Endpoints (Phase 6)


@app.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time sensor data streaming.

    Endpoint: ws://localhost:8000/ws/live

    Features:
    - Real-time sensor data push (camera, microphone)
    - Configurable data rate (1-10 Hz)
    - System resource monitoring
    - Automatic reconnection support

    Message Types:
    - sensor_data: Periodic sensor readings with timestamp
    - status: Connection and system status updates
    - error: Error notifications

    Client Commands:
    - set_rate: Update streaming rate in Hz

    Example:
        Send: {"command": "set_rate", "rate": 2.0}
        Receive: {"type": "sensor_data", "timestamp": "...", "sensors": {...}}
    """
    from .websocket_routes import websocket_endpoint

    manager = get_sensor_manager()
    await websocket_endpoint(websocket, sensor_manager=manager)


@app.get("/api/websocket/status")
async def get_websocket_status() -> Dict[str, object]:
    """
    Get WebSocket connection manager status.

    Returns:
        Number of active connections and status
    """
    from .websocket_routes import manager as ws_manager

    return ws_manager.get_status()


# ============================================================================
# Analytics Endpoints (Phase 7)
# ============================================================================

# Global analytics instance
_analytics = None


def get_analytics():
    """Get or create analytics instance."""
    global _analytics
    if _analytics is None:
        from .analytics import Analytics

        _analytics = Analytics()
    return _analytics


@app.get("/api/analytics/aggregate/{data_type}")
async def get_aggregated_data(
    data_type: str, period: str = "hourly", days: int = 7, limit: int = 100
) -> Dict[str, object]:
    """
    Get aggregated sensor data by time period.

    Args:
        data_type: Type of data ('greenery' or 'noise')
        period: Aggregation period ('hourly', 'daily', 'weekly', 'monthly')
        days: Number of days to include (default: 7)
        limit: Maximum number of aggregated points (default: 100)

    Returns:
        List of aggregated data points with timestamp and statistics
    """
    valid_types = ["greenery", "noise"]
    if data_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data_type. Must be one of: {valid_types}",
        )

    valid_periods = ["hourly", "daily", "weekly", "monthly"]
    if period not in valid_periods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid period. Must be one of: {valid_periods}",
        )

    try:
        from .analytics import AggregationPeriod
        from datetime import datetime, timedelta

        period_enum = AggregationPeriod(period)
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        analytics = get_analytics()
        data = analytics.get_aggregated_data(
            data_type=data_type,
            period=period_enum,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )

        return {
            "data_type": data_type,
            "period": period,
            "days": days,
            "count": len(data),
            "data": data,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Aggregation failed: {str(e)}",
        )


@app.get("/api/analytics/statistics/{data_type}")
async def get_data_statistics(data_type: str, days: int = 7) -> Dict[str, object]:
    """
    Get comprehensive statistics for sensor data.

    Args:
        data_type: Type of data ('greenery' or 'noise')
        days: Number of days to analyze (default: 7)

    Returns:
        Dictionary with statistical metrics (avg, min, max, stddev, median, mode, range)
    """
    valid_types = ["greenery", "noise"]
    if data_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data_type. Must be one of: {valid_types}",
        )

    try:
        from datetime import datetime, timedelta

        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        analytics = get_analytics()
        stats = analytics.calculate_statistics(
            data_type=data_type, start_time=start_time, end_time=end_time
        )

        return {"data_type": data_type, "days": days, "statistics": stats}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Statistics calculation failed: {str(e)}",
        )


@app.get("/api/analytics/trends/{data_type}")
async def get_trend_analysis(
    data_type: str, period: str = "daily", days: int = 7
) -> Dict[str, object]:
    """
    Detect trends in sensor data over time.

    Args:
        data_type: Type of data ('greenery' or 'noise')
        period: Aggregation period for analysis ('hourly', 'daily', 'weekly')
        days: Number of days to analyze (default: 7)

    Returns:
        Trend analysis with direction, slope, confidence, and change percentage
    """
    valid_types = ["greenery", "noise"]
    if data_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data_type. Must be one of: {valid_types}",
        )

    valid_periods = ["hourly", "daily", "weekly"]
    if period not in valid_periods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid period. Must be one of: {valid_periods}",
        )

    try:
        from .analytics import AggregationPeriod

        period_enum = AggregationPeriod(period)

        analytics = get_analytics()
        trends = analytics.detect_trends(data_type=data_type, period=period_enum, days=days)

        return {"data_type": data_type, "period": period, "days": days, "trends": trends}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trend detection failed: {str(e)}",
        )


@app.get("/api/analytics/anomalies/{data_type}")
async def get_anomaly_detection(
    data_type: str, days: int = 7, threshold: float = 2.0
) -> Dict[str, object]:
    """
    Detect anomalous data points that deviate significantly from normal.

    Args:
        data_type: Type of data ('greenery' or 'noise')
        days: Number of days to analyze (default: 7)
        threshold: Number of standard deviations for anomaly threshold (default: 2.0)

    Returns:
        List of anomalous data points with z-scores and severity
    """
    valid_types = ["greenery", "noise"]
    if data_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data_type. Must be one of: {valid_types}",
        )

    try:
        analytics = get_analytics()
        anomalies = analytics.detect_anomalies(
            data_type=data_type, days=days, threshold_stddev=threshold
        )

        return {
            "data_type": data_type,
            "days": days,
            "threshold_stddev": threshold,
            "count": len(anomalies),
            "anomalies": anomalies,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Anomaly detection failed: {str(e)}",
        )


@app.get("/api/analytics/correlation")
async def get_correlation_analysis(days: int = 7) -> Dict[str, object]:
    """
    Calculate correlation between greenery and noise levels.

    Args:
        days: Number of days to analyze (default: 7)

    Returns:
        Correlation coefficient, strength, and interpretation
    """
    try:
        analytics = get_analytics()
        correlation = analytics.get_correlation(days=days)

        return {"days": days, "correlation": correlation}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Correlation analysis failed: {str(e)}",
        )


# ============================================================================
# Context Engine Endpoints (Phase 8)
# ============================================================================

# Global context engine instance
_context_engine = None


def get_context_engine():
    """Get or create context engine instance."""
    global _context_engine
    if _context_engine is None:
        from .context_engine import ContextEngine

        _context_engine = ContextEngine()
    return _context_engine


@app.get("/api/context/wellness_score")
async def get_wellness_score(days: int = 1) -> Dict[str, object]:
    """
    Get overall wellness score based on sensor data.

    Args:
        days: Number of days to analyze (default: 1)

    Returns:
        Wellness score (0-100) with rating, components, and message
    """
    if days < 1 or days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Days must be between 1 and 365"
        )

    try:
        context_engine = get_context_engine()
        score_data = context_engine.calculate_wellness_score(days=days)
        return score_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Wellness score calculation failed: {str(e)}",
        )


@app.get("/api/context/recommendations")
async def get_recommendations(days: int = 7, limit: int = 10, priority: Optional[str] = None) -> Dict[str, object]:
    """
    Get personalized wellness recommendations.

    Args:
        days: Number of days of data to analyze (default: 7)
        limit: Maximum number of recommendations (default: 10)
        priority: Filter by priority level (high/medium/low, optional)

    Returns:
        List of recommendations with actions and impact
    """
    if days < 1 or days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Days must be between 1 and 365"
        )
    
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Limit must be between 1 and 100"
        )
    
    if priority and priority not in ["high", "medium", "low"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Priority must be one of: high, medium, low",
        )

    try:
        context_engine = get_context_engine()
        recommendations = context_engine.generate_recommendations(
            days=days, limit=limit, priority_filter=priority
        )
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendations generation failed: {str(e)}",
        )


@app.get("/api/context/patterns")
async def get_patterns(days: int = 14, pattern_type: str = "all") -> Dict[str, object]:
    """
    Detect patterns in sensor data.

    Args:
        days: Number of days to analyze (default: 14)
        pattern_type: Type of patterns to detect (all/recurring/time_based/trends)

    Returns:
        List of detected patterns with descriptions and recommendations
    """
    if days < 1 or days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Days must be between 1 and 365"
        )
    
    valid_types = ["all", "recurring", "time_based", "trends"]
    if pattern_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid pattern_type. Must be one of: {valid_types}",
        )

    try:
        context_engine = get_context_engine()
        patterns = context_engine.detect_patterns(days=days, pattern_type=pattern_type)
        return patterns
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pattern detection failed: {str(e)}",
        )


class FeedbackData(BaseModel):
    """Model for recommendation feedback."""
    
    recommendation_id: str
    helpful: bool
    implemented: bool = False
    comment: Optional[str] = None


@app.post("/api/context/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(feedback: FeedbackData) -> Dict[str, str]:
    """
    Submit feedback on a recommendation.

    Args:
        feedback: Feedback data including recommendation ID and user input

    Returns:
        Confirmation message
    """
    try:
        context_engine = get_context_engine()
        result = context_engine.submit_feedback(
            recommendation_id=feedback.recommendation_id,
            helpful=feedback.helpful,
            implemented=feedback.implemented,
            comment=feedback.comment,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feedback submission failed: {str(e)}",
        )


@app.get("/api/context/baselines")
async def get_baselines() -> Dict[str, object]:
    """
    Get personalized baseline values for the user.

    Returns:
        Baseline values with confidence levels and recommendations
    """
    try:
        context_engine = get_context_engine()
        baselines = context_engine.get_baselines()
        return baselines
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Baseline retrieval failed: {str(e)}",
        )


# ============================================================================
# Simulation Engine Endpoints
# ============================================================================

class SimulationStartRequest(BaseModel):
    """Request model for starting simulation."""
    scenario: str = "calm"


@app.get("/api/simulation/status")
async def get_simulation_status() -> Dict[str, object]:
    """
    Get current simulation status.
    
    Returns:
        Simulation status information including active scenario
    """
    try:
        manager = get_sensor_manager()
        return manager.get_simulation_status()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get simulation status: {str(e)}",
        )


@app.get("/api/simulation/scenarios")
async def get_simulation_scenarios() -> Dict[str, object]:
    """
    Get list of available simulation scenarios.
    
    Returns:
        List of scenarios with descriptions and parameters
    """
    try:
        manager = get_sensor_manager()
        scenarios = manager.get_simulation_scenarios()
        return {
            "scenarios": scenarios,
            "count": len(scenarios),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get simulation scenarios: {str(e)}",
        )


@app.post("/api/simulation/start", status_code=status.HTTP_200_OK)
async def start_simulation(request: SimulationStartRequest) -> Dict[str, object]:
    """
    Start simulation mode with specified scenario.
    
    Stops real sensors and switches to simulated data generation.
    
    Args:
        request: Contains scenario name ("calm", "stress", "dynamic", "custom")
        
    Returns:
        Success message and simulation status
    """
    try:
        manager = get_sensor_manager()
        
        # Validate scenario
        valid_scenarios = ["calm", "stress", "dynamic", "custom"]
        if request.scenario.lower() not in valid_scenarios:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid scenario. Must be one of: {', '.join(valid_scenarios)}",
            )
        
        # Start simulation
        success = manager.start_simulation(request.scenario)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start simulation",
            )
        
        return {
            "message": f"Simulation started with scenario: {request.scenario}",
            "status": manager.get_simulation_status(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation start failed: {str(e)}",
        )


@app.post("/api/simulation/stop", status_code=status.HTTP_200_OK)
async def stop_simulation() -> Dict[str, object]:
    """
    Stop simulation mode and revert to live sensor data.
    
    Returns:
        Success message
    """
    try:
        manager = get_sensor_manager()
        success = manager.stop_simulation()
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to stop simulation",
            )
        
        return {
            "message": "Simulation stopped successfully",
            "status": manager.get_simulation_status(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation stop failed: {str(e)}",
        )


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
