"""Emotion detection using DeepFace and webcam."""
import time
import sys
import collections
from typing import Dict
try:
    import cv2
except Exception:
    cv2 = None
    print("[WARN] opencv-python not available. Emotion will be skipped.")
try:
    from deepface import DeepFace
except Exception:
    DeepFace = None
    print("[WARN] deepface not available. Emotion detection will be skipped.")


def run_emotion_sampling(seconds: int = 15, camera_index: int = 0) -> Dict:
    if cv2 is None or DeepFace is None:
        missing = []
        if cv2 is None: missing.append("opencv")
        if DeepFace is None: missing.append("deepface")
        return {"available": False, "reason": ", ".join(missing) + " not installed"}

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        return {"available": False, "reason": f"cannot open camera {camera_index}"}

    print(f"[Emotion] Sampling for ~{seconds}s (press 'q' to stop early)...")
    counts = collections.Counter()
    start = time.time()

    while time.time() - start < seconds:
        ret, frame = cap.read()
        if not ret:
            break
        try:
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            dom = result[0]['dominant_emotion']
            counts[dom] += 1
            txt = f"Dominant: {dom}"
        except Exception:
            txt = "No face"
        cv2.putText(frame, txt, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imshow("Emotion Webcam", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        time.sleep(1)

    cap.release()
    cv2.destroyAllWindows()

    if not counts:
        return {"available": False, "reason": "no faces detected"}
    dominant, freq = counts.most_common(1)[0]
    return {
        "available": True,
        "dominant_emotion": dominant,
        "counts": dict(counts),
    }
