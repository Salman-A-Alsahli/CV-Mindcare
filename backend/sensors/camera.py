"""
Camera Sensor Module
------------------
Handles camera-based face detection and emotion analysis.
"""

import cv2
import numpy as np
from typing import Optional, Dict


class CameraSensor:
    """Camera sensor for face detection and emotion analysis."""

    def __init__(self, camera_index: int = 0):
        """
        Initialize camera sensor.

        Args:
            camera_index: Camera device index (default 0 for primary camera)
        """
        self.camera_index = camera_index
        self.cap: Optional[cv2.VideoCapture] = None
        self.face_cascade = None
        self._load_face_cascade()

    def _load_face_cascade(self):
        """Load Haar Cascade for face detection."""
        try:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
        except Exception as e:
            print(f"Error loading face cascade: {e}")
            self.face_cascade = None

    def is_available(self) -> bool:
        """
        Check if camera is available.

        Returns:
            True if camera can be accessed, False otherwise
        """
        try:
            cap = cv2.VideoCapture(self.camera_index)
            if cap.isOpened():
                cap.release()
                return True
            return False
        except:
            return False

    def open(self) -> bool:
        """
        Open camera connection.

        Returns:
            True if successful, False otherwise
        """
        if self.cap is not None and self.cap.isOpened():
            return True

        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            return self.cap.isOpened()
        except:
            return False

    def close(self):
        """Close camera connection."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from camera.

        Returns:
            Frame as numpy array, or None if capture failed
        """
        if self.cap is None or not self.cap.isOpened():
            if not self.open():
                return None

        try:
            ret, frame = self.cap.read()
            if ret:
                return frame
            return None
        except:
            return None

    def detect_faces(self, frame: Optional[np.ndarray] = None) -> Dict[str, any]:
        """
        Detect faces in a frame.

        Args:
            frame: Image frame (if None, captures new frame)

        Returns:
            Dictionary with face detection results:
            - faces_detected: number of faces
            - available: whether detection was successful
            - error: error message if any
        """
        if frame is None:
            frame = self.capture_frame()

        if frame is None:
            return {"faces_detected": 0, "available": False, "error": "Failed to capture frame"}

        if self.face_cascade is None:
            return {"faces_detected": 0, "available": False, "error": "Face cascade not loaded"}

        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )

            return {
                "faces_detected": len(faces),
                "available": True,
                "faces": faces.tolist() if len(faces) > 0 else [],
            }
        except Exception as e:
            return {"faces_detected": 0, "available": False, "error": str(e)}

    def calculate_greenery_percentage(self, frame: Optional[np.ndarray] = None) -> Dict[str, any]:
        """
        Calculate percentage of green pixels in frame (simple greenery detection).

        Args:
            frame: Image frame (if None, captures new frame)

        Returns:
            Dictionary with greenery analysis:
            - green_percentage: percentage of green pixels
            - available: whether analysis was successful
        """
        if frame is None:
            frame = self.capture_frame()

        if frame is None:
            return {"green_percentage": 0.0, "available": False, "error": "Failed to capture frame"}

        try:
            # Convert to HSV color space
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Define range for green color
            # Hue: 40-80 (green range), Saturation: 40-255, Value: 40-255
            lower_green = np.array([40, 40, 40])
            upper_green = np.array([80, 255, 255])

            # Create mask for green pixels
            mask = cv2.inRange(hsv, lower_green, upper_green)

            # Calculate percentage
            total_pixels = frame.shape[0] * frame.shape[1]
            green_pixels = np.count_nonzero(mask)
            green_percentage = (green_pixels / total_pixels) * 100

            return {"green_percentage": round(green_percentage, 2), "available": True}
        except Exception as e:
            return {"green_percentage": 0.0, "available": False, "error": str(e)}

    def get_comprehensive_reading(self) -> Dict[str, any]:
        """
        Get comprehensive camera reading including faces and greenery.

        Returns:
            Dictionary with all camera-based measurements
        """
        frame = self.capture_frame()

        if frame is None:
            return {
                "available": False,
                "error": "Failed to capture frame",
                "faces_detected": 0,
                "green_percentage": 0.0,
            }

        face_data = self.detect_faces(frame)
        greenery_data = self.calculate_greenery_percentage(frame)

        return {
            "available": True,
            "faces_detected": face_data.get("faces_detected", 0),
            "green_percentage": greenery_data.get("green_percentage", 0.0),
            "faces": face_data.get("faces", []),
        }

    def __del__(self):
        """Cleanup on object destruction."""
        self.close()


# Convenience functions


def get_camera_reading(camera_index: int = 0) -> Dict[str, any]:
    """
    Get a single camera reading.

    Args:
        camera_index: Camera device index

    Returns:
        Camera reading dictionary
    """
    sensor = CameraSensor(camera_index)
    reading = sensor.get_comprehensive_reading()
    sensor.close()
    return reading


def check_camera_available(camera_index: int = 0) -> bool:
    """
    Check if camera is available.

    Args:
        camera_index: Camera device index

    Returns:
        True if camera is available
    """
    sensor = CameraSensor(camera_index)
    available = sensor.is_available()
    return available
