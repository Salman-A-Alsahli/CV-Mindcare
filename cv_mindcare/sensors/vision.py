"""Greenery detection using OpenCV."""
import sys
from typing import Tuple, List, Dict
try:
    import cv2
    import numpy as np
except Exception:
    cv2 = None
    np = None
    print("[WARN] opencv-python not available. Greenery/Emotion will be skipped.")


def detect_greenery(frame) -> Tuple[float, np.ndarray]:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    green_pixels = cv2.countNonZero(mask)
    total_pixels = frame.shape[0] * frame.shape[1]
    green_ratio = (green_pixels / float(total_pixels)) * 100.0
    return green_ratio, mask


def classify_greenery(avg_green: float) -> str:
    if avg_green < 5:
        return "Low"
    elif 5 < avg_green < 12:
        return "Moderate"
    else:
        return "High"


def run_greenery_sampling(camera_index: int = 0) -> Dict:
    if cv2 is None:
        return {"available": False, "reason": "opencv not installed"}
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        return {"available": False, "reason": f"cannot open camera {camera_index}"}

    print("[Greenery] Press 's' to stop and analyze, 'q' to abort.")
    green_values: List[float] = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        green_ratio, mask = detect_greenery(frame)
        green_values.append(green_ratio)

        cv2.putText(frame, f"Greenery: {green_ratio:.2f}%", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Camera Feed", frame)
        cv2.imshow("Green Mask", mask)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            break
        if key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return {"available": False, "reason": "aborted"}

    cap.release()
    cv2.destroyAllWindows()

    if not green_values:
        return {"available": False, "reason": "no frames"}
    avg_green = float(np.mean(green_values))
    cls = classify_greenery(avg_green)
    return {
        "available": True,
        "avg_green_pct": round(avg_green, 2),
        "classification": cls,
        "samples": len(green_values),
    }
