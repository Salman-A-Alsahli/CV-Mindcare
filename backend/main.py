from typing import Any, Dict
import json
import asyncio
import random
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="CV Mindcare Backend")

# Sampler runtime state is stored on app.state
app.state.sampler_running = False
app.state.sampler_task = None
app.state.sampler_stop_event = None
app.state.last_sample = None

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT / "frontend"


@app.get("/api/health")
async def health() -> Dict[str, Any]:
    return {"status": "ok"}


def _safe_import(module_name: str):
    try:
        return __import__(module_name, fromlist=["*"])
    except Exception:
        return None


@app.get("/api/live")
async def live_readings():
    """Return a best-effort snapshot of current readings.

    This will try to use sensor modules but falls back to last DB record or
    to mocked values if unavailable.
    """
    sensors = _safe_import("cv_mindcare.sensors.noise")
    vision_mod = _safe_import("cv_mindcare.sensors.vision")
    emotion_mod = _safe_import("cv_mindcare.sensors.emotion")
    dbm = _safe_import("cv_mindcare.database_manager")

    # Try to get a recent DB row as fallback
    fallback = {}
    try:
        if dbm:
            df = dbm.get_session_history(7)
            if not df.empty:
                last = df.iloc[-1]
                fallback = {
                    "dominant_emotion": last.get("dominant_emotion"),
                    "avg_db": float(last.get("avg_db")) if last.get("avg_db") is not None else None,
                    "noise_classification": None,
                    "avg_green_pct": float(last.get("avg_green_pct")) if last.get("avg_green_pct") is not None else None,
                }
    except Exception:
        fallback = {}

    # Build a best-effort live reading
    result = {
        "dominant_emotion": None,
        "avg_db": None,
        "noise_classification": None,
        "avg_green_pct": None,
    }

    # Noise
    try:
        if sensors and hasattr(sensors, "measure_noise_once"):
            v = sensors.measure_noise_once()
            if v is not None:
                result["avg_db"] = v
                result["noise_classification"] = sensors.classify_noise(v)
    except Exception:
        pass

    # Greenery: cannot run interactive run_greenery_sampling; skip live camera heavy ops
    try:
        if vision_mod and hasattr(vision_mod, "detect_greenery"):
            # Not able to capture a frame here; leave None
            pass
    except Exception:
        pass

    # Emotion: skip heavy model calls for live endpoint

    # Fill from fallback when missing
    for k, v in fallback.items():
        if result.get(k) is None and v is not None:
            result[k] = v

    # As last resort use mock values
    if result["avg_db"] is None:
        result["avg_db"] = 45.0
        result["noise_classification"] = "Calm"
    if result["dominant_emotion"] is None:
        result["dominant_emotion"] = "neutral"
    if result["avg_green_pct"] is None:
        result["avg_green_pct"] = 8.5

    return JSONResponse(result)


@app.get("/api/context")
async def context_payload(days: int = 30):
    """Return the combined context payload using database analysis.

    Uses `create_context_for_ai` if available; otherwise synthesizes a minimal
    payload from last DB row.
    """
    dbm = _safe_import("cv_mindcare.database_manager")
    ollama = _safe_import("cv_mindcare.llm.ollama")

    # Try to get current readings from live_readings
    live = await live_readings()
    current = live.body if hasattr(live, "body") else live

    if ollama and hasattr(ollama, "create_context_for_ai"):
        payload = ollama.create_context_for_ai(current, days=days, include_json=False)
        return JSONResponse(payload)

    # Fallback: synthesize simple historical summary
    hist = {"most_frequent_emotion": None, "noisiest_time_of_day": None, "insight": None}
    try:
        if dbm:
            df = dbm.get_session_history(days)
            analysis = dbm.analyze_and_rank_trends(df)
            hist = {
                "most_frequent_emotion": analysis.get("emotions_rank", {}).get("most_common"),
                "noisiest_time_of_day": analysis.get("noisy_time_category", {}).get("category"),
                "insight": None,
            }
    except Exception:
        pass

    return JSONResponse({"current_readings": current, "historical_summary": hist})


@app.get("/")
async def index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    raise HTTPException(status_code=404, detail="Frontend not found")


# Mount static (allow serving CSS/JS if present)
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


    @app.get("/api/start")
    async def start_collection():
        # If already running, return current state
        if app.state.__dict__.get("sampler_running"):
            return JSONResponse({"status": "already_running"})

        # Prepare cancellation event and create task
        stop_event = asyncio.Event()
        app.state.sampler_stop_event = stop_event
        app.state.sampler_running = True
        app.state.last_sample = None
        # Start background sampler task
        app.state.sampler_task = asyncio.create_task(_sampler_loop(stop_event))
        return JSONResponse({"status": "started"})


    @app.get("/api/stop")
    async def stop_collection():
        # Signal the sampler to stop and wait briefly
        ev = getattr(app.state, "sampler_stop_event", None)
        task = getattr(app.state, "sampler_task", None)
        app.state.sampler_running = False
        if ev is not None:
            ev.set()
        if task is not None:
            try:
                await asyncio.wait_for(task, timeout=3.0)
            except Exception:
                try:
                    task.cancel()
                except Exception:
                    pass
        return JSONResponse({"status": "stopped"})


    @app.get("/api/status")
    async def sampler_status():
        running = bool(getattr(app.state, "sampler_running", False))
        last = getattr(app.state, "last_sample", None)
        return JSONResponse({"running": running, "last_sample": last})


    @app.get("/api/live_simple")
    async def get_live_simple():
        """A lightweight mock live endpoint useful for frontend demos and testing."""
        import random

        if not getattr(app.state, "sampler_running", False):
            return JSONResponse({"status": "idle"})

        return JSONResponse({
            "emotion": random.choice(["happy", "sad", "neutral", "angry"]),
            "noise_level": random.randint(30, 90),
            "greenery": random.randint(0, 100),
        })


    async def _sampler_loop(stop_event: asyncio.Event, interval: float = 5.0):
        """Background sampler loop.

        Tries to use sensor modules when available; otherwise emits simulated values.
        Logs to the database via cv_mindcare.database_manager.log_session_data.
        """
        # Lazy imports so missing optional deps don't break server start
        dbm = _safe_import("cv_mindcare.database_manager")
        noise_mod = _safe_import("cv_mindcare.sensors.noise")
        vision_mod = _safe_import("cv_mindcare.sensors.vision")
        emotion_mod = _safe_import("cv_mindcare.sensors.emotion")

        while not stop_event.is_set():
            try:
                # Gather readings (best-effort)
                emotion = None
                avg_db = None
                green_pct = None

                # Emotion
                try:
                    if emotion_mod and hasattr(emotion_mod, "run_emotion_sampling"):
                        res = emotion_mod.run_emotion_sampling(1)
                        emotion = res.get("dominant_emotion") if isinstance(res, dict) else None
                except Exception:
                    emotion = None

                # Noise
                try:
                    if noise_mod and hasattr(noise_mod, "measure_noise_once"):
                        avg_db = noise_mod.measure_noise_once()
                except Exception:
                    avg_db = None

                # Greenery
                try:
                    if vision_mod and hasattr(vision_mod, "run_greenery_sampling"):
                        green_pct = vision_mod.run_greenery_sampling()
                except Exception:
                    green_pct = None

                # Fallback simulated values
                if emotion is None:
                    emotion = random.choice(["happy", "sad", "neutral", "angry"])
                if avg_db is None:
                    avg_db = float(random.randint(30, 80))
                if green_pct is None:
                    green_pct = float(random.randint(0, 100))

                sample = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "dominant_emotion": emotion,
                    "emotion_counts": {},
                    "avg_db": float(avg_db),
                    "noise_classification": None,
                    "avg_green_pct": float(green_pct),
                }

                # Log to DB if available
                try:
                    if dbm and hasattr(dbm, "log_session_data"):
                        dbm.log_session_data(sample)
                except Exception:
                    # swallow DB errors but keep running
                    pass

                # Store last sample for status endpoint
                app.state.last_sample = sample

            except Exception:
                # Ensure loop doesn't stop on unexpected error
                pass

            # Wait for interval or stop
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=interval)
            except asyncio.TimeoutError:
                continue
