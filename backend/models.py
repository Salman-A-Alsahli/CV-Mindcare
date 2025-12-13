"""
Pydantic Models for CV-Mindcare Backend
--------------------------------------
Data validation and serialization models.
"""

from typing import Optional, Dict
from pydantic import BaseModel, Field


# Request Models


class SensorDataCreate(BaseModel):
    """Model for creating sensor data entries."""

    sensor_type: str = Field(..., description="Type of sensor (e.g., 'emotion', 'greenery')")
    value: float = Field(..., description="Sensor reading value")
    timestamp: Optional[str] = Field(
        None, description="ISO timestamp (auto-generated if not provided)"
    )


class FaceDetectionCreate(BaseModel):
    """Model for creating face detection entries."""

    faces_detected: int = Field(..., ge=0, description="Number of faces detected")
    timestamp: Optional[str] = Field(None, description="ISO timestamp")


class SoundSampleCreate(BaseModel):
    """Model for creating sound analysis entries."""

    avg_db: float = Field(..., ge=0, description="Average decibel level")
    timestamp: Optional[str] = Field(None, description="ISO timestamp")


# Response Models


class SensorDataResponse(BaseModel):
    """Model for sensor data responses."""

    sensor_type: str
    value: float
    timestamp: str


class FaceDetectionResponse(BaseModel):
    """Model for face detection responses."""

    faces_detected: int
    timestamp: str


class SoundSampleResponse(BaseModel):
    """Model for sound analysis responses."""

    avg_db: float
    timestamp: str


class SensorStatusResponse(BaseModel):
    """Model for sensor status."""

    camera: bool
    microphone: bool
    system_resources: bool


class SystemStatsResponse(BaseModel):
    """Model for system statistics."""

    uptime: int
    active_sensors: int
    data_points: int
    breakdown: Dict[str, int]


class EmotionData(BaseModel):
    """Model for emotion distribution."""

    neutral: float = 0.0
    happy: float = 0.0
    sad: float = 0.0
    angry: float = 0.0
    surprised: float = 0.0
    fearful: float = 0.0
    disgusted: float = 0.0


class LiveDataResponse(BaseModel):
    """Model for live aggregated data."""

    faces_detected: int
    avg_db: float
    dominant_emotion: str
    avg_green_pct: float
    last_updated: str
    emotions: EmotionData
    stats: Dict[str, float]


class HealthCheckResponse(BaseModel):
    """Model for health check endpoint."""

    status: str
    version: str
    name: str


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


# Database Models (for internal use)


class SensorDataDB(BaseModel):
    """Internal database representation of sensor data."""

    id: int
    sensor_type: str
    value: float
    timestamp: str

    class Config:
        from_attributes = True


class FaceDetectionDB(BaseModel):
    """Internal database representation of face detection."""

    id: int
    faces_detected: int
    timestamp: str

    class Config:
        from_attributes = True


class SoundSampleDB(BaseModel):
    """Internal database representation of sound sample."""

    id: int
    avg_db: float
    timestamp: str

    class Config:
        from_attributes = True
