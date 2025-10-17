"""
Wellbeing Environment Assistant
--------------------------------
Integrates:
1) Noise detection (sounddevice)
2) Greenery detection (OpenCV webcam)
3) Emotion detection (DeepFace)
4) (Optional / commented) MQ-135 air-quality reader for Raspberry Pi

After collecting quick measurements, the script summarizes results
and asks a local LLaMA 7B chat model to give guidance, then starts
an interactive chat seeded with the measurements.

USAGE
-----
python wellbeing_assistant.py --noise-samples 5 --emotion-seconds 15 --camera 0

Keys during greenery capture:
  - Press 's' to stop greenery sampling and continue
  - Press 'q' to abort

REQUIREMENTS
------------
- Python 3.9+
- pip install: sounddevice numpy opencv-python deepface transformers accelerate torch safetensors
- A webcam for greenery/emotion
- A local LLaMA model (default: meta-llama/Llama-2-7b-chat-hf) accessible via Hugging Face
  (You may need to accept the license on Hugging Face and set HF_TOKEN env var.)

NOTE on GPU: If you have a CUDA GPU, Transformers will try to use it automatically
with device_map="auto". Otherwise it will run on CPU (slower).

Air-quality (MQ-135) is included below as commented-out code since hardware is not present yet.
"""
import requests
import json

def llama_local_response(prompt, model="llama2:7b-chat"):
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {"model": model, "prompt": prompt, "stream": False}
    r = requests.post(url, headers=headers, data=json.dumps(data))
    if r.status_code == 200:
        return r.json()["response"]
    else:
        return f"Error: {r.text}"

import argparse
import collections
import time
import sys
from typing import Dict, List, Tuple, Optional

# --- Optional deps guarded with helpful error messages ---
try:
    import numpy as np
except Exception as e:
    print("[WARN] numpy missing: pip install numpy", file=sys.stderr)
    raise

try:
    import sounddevice as sd
except Exception:
    sd = None
    print("[WARN] sounddevice not available. Noise measurement will be skipped.")

try:
    import cv2
except Exception:
    cv2 = None
    print("[WARN] opencv-python not available. Greenery/Emotion will be skipped.")

try:
    from deepface import DeepFace
except Exception:
    DeepFace = None
    print("[WARN] deepface not available. Emotion detection will be skipped.")

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
except Exception:
    AutoModelForCausalLM = None
    AutoTokenizer = None
    pipeline = None
    print("[WARN] transformers/torch not available. LLaMA response & chat will be disabled.")

# ------------------ Noise detection ------------------
REF = 32768  # reference for 16-bit audio

def measure_noise_once(duration: float = 1.0, samplerate: int = 44100) -> Optional[float]:
    if sd is None:
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

# ------------------ Greenery detection ------------------

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

# ------------------ Emotion detection ------------------

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

# ------------------ LLaMA Chat ------------------
LLAMA_DEFAULT = "meta-llama/Llama-2-7b-chat-hf"  # 7B chat model

SYSTEM_PROMPT = (
    "You are a supportive wellbeing assistant. You will be given observations "
    "about the user's environment (noise, greenery, emotions, air quality). "
    "Explain the results in simple terms, give concise, practical tips, and keep a positive tone."
)

import requests, json

# set an Ollama-friendly default
LLAMA_DEFAULT = "llama2:7b-chat"

# (keep your Ollama HTTP functions)
def load_llama(model_name: str = LLAMA_DEFAULT):
    print(f"[LLM] Using local Ollama model: {model_name}")
    return model_name, None

def format_prompt(system: str, history: List[Tuple[str, str]], user_msg: str) -> str:
    """Very simple chat prompt for Llama-2-7b-chat style models."""
    sep = "\n\n"
    prompt = f"[SYSTEM]\n{system}{sep}"
    for (role, msg) in history:
        if role == "user":
            prompt += f"[USER]\n{msg}{sep}"
        else:
            prompt += f"[ASSISTANT]\n{msg}{sep}"
    prompt += f"[USER]\n{user_msg}{sep}[ASSISTANT]\n"
    return prompt

def llama_respond(model_name, _tok, system: str, history: List[Tuple[str, str]], user_msg: str, max_new_tokens: int = 300):
    prompt = format_prompt(system, history, user_msg)
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "model": model_name,
                "prompt": prompt,
                "stream": False
            })
        )
        if r.status_code == 200:
            data = r.json()
            return data.get("response", "").strip()
        else:
            return f"[Error] Ollama returned status {r.status_code}: {r.text}"
    except Exception as e:
        return f"[Error] Failed to connect to Ollama: {e}"


# ------------------ Orchestration ------------------

def summarize_findings(noise: Dict, green: Dict, emo: Dict) -> str:
    lines = ["Here are the quick observations from your environment:"]
    if noise.get("available"):
        lines.append(f"- Noise: avg {noise['avg_db']} dB → {noise['classification']}")
    else:
        lines.append(f"- Noise: unavailable ({noise.get('reason', 'unknown')})")

    if green.get("available"):
        lines.append(f"- Greenery: avg {green['avg_green_pct']:.2f}% → {green['classification']}")
    else:
        lines.append(f"- Greenery: unavailable ({green.get('reason', 'unknown')})")

    if emo.get("available"):
        lines.append(f"- Emotion: dominant '{emo['dominant_emotion']}' over {sum(emo.get('counts', {}).values())} samples")
    else:
        lines.append(f"- Emotion: unavailable ({emo.get('reason', 'unknown')})")

    # Air quality: intentionally not measured (hardware not present)
    lines.append("- Air quality: skipped (sensor not connected yet)")
    return "\n".join(lines)

# ------------------ Fallback rule-based advice (when no LLM) ------------------

def fallback_advice(noise: Dict, green: Dict, emo: Dict) -> str:
    tips = []
    # Noise
    if noise.get("available"):
        n = noise.get("avg_db", 0)
        nc = noise.get("classification", "")
        if n >= 70 or nc == "Harmful":
            tips.append("Noise is very high. Use headphones with isolation, close doors/windows, and add soft furnishings or panels.")
        elif n >= 55 or nc in {"Stress Zone"}:
            tips.append("Noise is above the focus sweet spot. Reduce notifications, enable noise suppression, and distance noisy devices.")
        else:
            tips.append("Noise level looks fine for focus.")
    else:
        tips.append("Noise reading unavailable—if possible, retry with a working microphone.")

    # Greenery
    if green.get("available"):
        g = green.get("avg_green_pct", 0)
        if g < 5:
            tips.append("Greenery is low. Add a plant or two in your field of view or a green poster; target >12% coverage.")
        elif g < 12:
            tips.append("Greenery is moderate. One more plant can push you into the 'high' zone.")
        else:
            tips.append("Great greenery—keep plants healthy and visible.")
    else:
        tips.append("Greenery unavailable—check webcam permissions.")

    # Emotion
    if emo.get("available"):
        d = (emo.get("dominant_emotion") or "").lower()
        if d in {"sad", "angry", "fear"}:
            tips.append("Mood skews negative. Try a 2–3 minute reset: stand, shoulder rolls, 6 slow breaths (4s in, 6s out), then a 25-minute focus block.")
        elif d in {"neutral"}:
            tips.append("Mood is neutral. A short stretch and a clear 30-minute goal can boost engagement.")
        else:
            tips.append("Positive affect detected—nice! Keep short breaks to maintain it.")
    else:
        tips.append("Emotion unavailable—face not detected or camera blocked.")

    quick = [
        "Open a window or run a fan for 2 minutes to refresh air.",
        "Silence non-critical app notifications.",
        "Place a plant or green object within your eye line.",
    ]
    return (
        "\n===== Opinion & Advice (Fallback) =====\n"
        "Your environment has a few easy improvements. Here are the priorities:\n"
        + "\n- " + "\n- ".join(tips) +
        "\n\nQuick wins (next 10 minutes):\n- " + "\n- ".join(quick) +
        "\n=======================================\n"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--camera", type=int, default=0, help="Webcam index (default 0)")
    ap.add_argument("--noise-samples", type=int, default=5, help="Number of noise samples")
    ap.add_argument("--emotion-seconds", type=int, default=15, help="Seconds to sample emotions")
    ap.add_argument("--model", type=str, default=LLAMA_DEFAULT, help="HF model id for LLaMA chat")
    ap.add_argument("--mock", action="store_true", help="Skip sensors and use mock readings to get immediate advice from the model")
    args = ap.parse_args()

    if args.mock:
        print("[MOCK] Using sample readings to get direct LLaMA advice...")
        noise = {"available": True, "avg_db": 58.1, "classification": "Acceptable", "readings": [58.2, 57.9, 58.3]}
        green = {"available": True, "avg_green_pct": 7.6, "classification": "Moderate", "samples": 120}
        emo = {"available": True, "dominant_emotion": "neutral", "counts": {"happy": 4, "neutral": 9, "sad": 2, "angry": 1}}
    else:
        # 1) Noise
        noise = run_noise_sampling(args.noise_samples)
        # 2) Greenery (interactive until 's')
        green = run_greenery_sampling(args.camera)
        # 3) Emotion (time-bounded)
        emo = run_emotion_sampling(args.emotion_seconds, args.camera)

    # 4) Summarize
    summary = summarize_findings(noise, green, emo)
    print("================ SUMMARY ================")
    print(summary)
    print("========================================")

    # 5) LLaMA guidance or fallback
    if pipeline is None:
        print("[LLM] transformers/torch missing — using built-in fallback advice.\n")
        print(fallback_advice(noise, green, emo))
        return

    llm, tok = load_llama(args.model)
    if llm is None:
        print("[LLM] Could not load model pipeline — using built-in fallback advice.\n")
        print(fallback_advice(noise, green, emo))
        return

    history: List[Tuple[str, str]] = []
    initial_user = (
        f"Please review these measurements and give brief, actionable advice to improve my wellbeing.\n\n{summary}\n\n"
        "Keep it friendly and specific to the readings."
    )
    assistant_reply = llama_respond(llm, tok, SYSTEM_PROMPT, history, initial_user)
    print("\n===== Assistant (LLaMA) =====\n" + assistant_reply + "\n=============================\n")
    history.append(("user", initial_user))
    history.append(("assistant", assistant_reply))

    # 6) Interactive chat loop
    print("Type your message to continue chatting with the assistant. Type '/exit' to quit.")
    try:
        while True:
            user_msg = input("You: ").strip()
            if not user_msg:
                continue
            if user_msg.lower() in {"/exit", "exit", ":q"}:
                print("Goodbye! 👋")
                break
            reply = llama_respond(llm, tok, SYSTEM_PROMPT, history, user_msg)
            print("Assistant:" + reply + "")
            history.append(("user", user_msg))
            history.append(("assistant", reply))
    except KeyboardInterrupt:
        print("Goodbye! 👋")


if __name__ == "__main__":
    main()



# ------------------ (COMMENTED) MQ-135 Air Quality Module ------------------
# The following is left as comments because the hardware sensor isn't connected yet.
# When ready, move this into a separate file or integrate similarly to the modules above,
# then call it before the LLaMA step to add its summary line.
"""
# import spidev
# import math
# SPI_BUS = 0
# SPI_DEVICE = 0
# ADC_CHANNEL = 0
# VREF = 5.0
# RL_VALUE = 10_000.0
# Ro = None
# CLEAN_AIR_FACTOR = 3.6
# spi = spidev.SpiDev()
# spi.open(SPI_BUS, SPI_DEVICE)
# spi.max_speed_hz = 1350000
# def read_adc(channel):
#     r = spi.xfer2([1, (8 + channel) << 4, 0])
#     return ((r[1] & 3) << 8) + r[2]
# def adc_to_voltage(adc_value):
#     return (adc_value / 1023.0) * VREF
# def rs_from_adc(adc_value):
#     if adc_value == 0:
#         return float('inf')
#     v_out = adc_to_voltage(adc_value)
#     return RL_VALUE * (VREF - v_out) / (v_out + 1e-12)
# def estimate_co2_proxy(rs, ro):
#     if ro is None or ro == 0:
#         return None
#     ratio = rs / ro
#     if ratio > 2.5:
#         return ("Good", ratio)
#     elif ratio > 1.2:
#         return ("Moderate", ratio)
#     elif ratio > 0.7:
#         return ("Poor", ratio)
#     else:
#         return ("Unsafe", ratio)
# def compute_ro_from_clean_air_samples(samples):
#     if not samples:
#         return None
#     avg_rs = sum(samples) / len(samples)
#     return avg_rs / CLEAN_AIR_FACTOR
# def run_air_quality_sample(calibrate_first=False, calibration_duration=30):
#     # returns dict similar to other modules
#     pass
"""
