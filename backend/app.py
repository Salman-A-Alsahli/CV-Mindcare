"""CV-Mindcare Backend API."""

from datetime import datetime
from typing import Dict, Optional

from fastapi import FastAPI, status
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
    version="0.1.0",
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
        "version": "0.1.0",
        "name": "CV-Mindcare API",
    }


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


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)