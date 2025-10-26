"""Noise measurement utilities."""
import time
import sys
from typing import Optional, Dict, List
try:
    import numpy as np
except Exception:
    np = None
    print("[WARN] numpy missing: pip install numpy", file=sys.stderr)
try:
    import sounddevice as sd
except Exception:
    sd = None
    print("[WARN] sounddevice not available. Noise measurement will be skipped.")

REF = 32768


def measure_noise_once(duration: float = 1.0, samplerate: int = 44100) -> Optional[float]:
    if sd is None or np is None:
        return None
    rec = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    rms = float(np.sqrt(np.mean(rec.astype(np.float64) ** 2)))
    db = 100 + 20 * np.log10(rms / REF + 1e-6)
    return round(db, 2)


def classify_noise(db_level: float) -> str:
    if db_level < 40:
        return "Calm"
    elif db_level < 55:
        return "Acceptable"
    elif db_level < 70:
        return "Stress Zone"
    else:
        return "Harmful"


def run_noise_sampling(n_samples: int = 5, pause_s: float = 0.5) -> Dict:
    readings: List[float] = []
    if sd is None:
        return {"available": False, "reason": "sounddevice not installed"}
    print("[Noise] Sampling...")
    for i in range(n_samples):
        val = measure_noise_once()
        if val is not None:
            readings.append(val)
            print(f"  {i+1}/{n_samples}: {val} dB")
        time.sleep(pause_s)
    if not readings:
        return {"available": False, "reason": "no readings"}
    avg = float(np.mean(readings))
    cls = classify_noise(avg)
    return {
        "available": True,
        "avg_db": round(avg, 2),
        "classification": cls,
        "readings": readings,
    }
