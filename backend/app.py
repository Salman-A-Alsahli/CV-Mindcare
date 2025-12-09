"""CV-Mindcare Backend API."""

from datetime import datetime
from typing import Dict, Optional

from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import psutil

from .database import (
    init_db,
    insert_sensor_data,
    insert_face_detection,
    insert_sound_analysis,
    get_recent_sensor_data,
    get_latest_face_detection,
    get_latest_sound_analysis,
    get_sensor_status,
    get_system_stats,
)

app = FastAPI(
    title="CV-Mindcare API",
    description="Backend API for CV-Mindcare system",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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


@app.on_event("startup")
async def startup() -> None:
    init_db()


@app.get("/")
async def root() -> Dict[str, str]:
    return {
        "status": "online",
        "version": "0.2.0",
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
    return {
        "status": {
            "camera": status_map.get("camera", False),
            "microphone": status_map.get("microphone", False),
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
        if not data.get('mock_mode', False):
            greenery_pct = data.get('greenery_percentage', 0.0)
            insert_sensor_data("greenery", greenery_pct)
        
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Camera capture failed: {str(e)}"
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
            detail="Greenery percentage must be between 0 and 100"
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
        if not data.get('mock_mode', False):
            db_level = data.get('db_level', 0.0)
            insert_sensor_data("noise", db_level)
        
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Microphone capture failed: {str(e)}"
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Noise level must be between 0 and 100"
        )
    
    insert_sensor_data("noise", db_level)
    return {"message": "noise data recorded"}


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
    avg_noise = sum(noise_levels) / len(noise_levels) if noise_levels else live_data.get("avg_db", 0)
    
    # Categorize noise time (simplified - would need timestamp analysis for full implementation)
    noise_category = "quiet" if avg_noise < 50 else "moderate" if avg_noise < 70 else "loud"
    
    historical_summary = {
        "most_frequent_emotion": most_frequent_emotion,
        "noisiest_time_of_day": noise_category,
        "avg_noise_level": round(avg_noise, 2),
        "avg_greenery": round(sum(greenery_levels) / len(greenery_levels), 2) if greenery_levels else 0.0,
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
        _sensor_manager = SensorManager(config={
            'polling_interval': 5.0,
            'auto_start': False,  # Manual start via API
            'auto_recover': True,
            'max_retries': 3
        })
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
            detail=f"Failed to get manager status: {str(e)}"
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
                detail="Failed to start any sensors"
            )
        
        return {
            "message": "Sensor manager started",
            "status": manager.get_all_status()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start manager: {str(e)}"
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
            "status": manager.get_all_status()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop manager: {str(e)}"
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
            detail=f"Failed to get manager health: {str(e)}"
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update configuration"
            )
        
        return {
            "message": "Configuration updated",
            "config": config_dict,
            "status": manager.get_all_status()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update config: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)