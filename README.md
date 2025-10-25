# CV Mindcare

CV Mindcare is a privacy-first local utility that observes a few environmental signals (sound level, presence of greenery via camera, and brief facial affect sampling) and provides human-readable observations, trend analysis, and practical suggestions to improve wellbeing in a workspace or room.

This repository now includes a lightweight local database and a context-aware assistant that uses historical data to provide personalized recommendations.

## Architecture

The data flow has been upgraded from a simple pipeline to a context-rich loop that supports long-term personalization:

1. Real-time Sensing
   - The application captures live data: dominant emotion (from face analysis), ambient noise (dB), and greenery percentage from the camera view.

2. Database Logging
   - Each live reading is immediately logged to an on-disk SQLite database (`mindcare.db`) as a historical record.

3. Historical Analysis
   - The system queries recent sessions and computes trends and statistics (most frequent emotions, noisy times of day, correlations between greenery and mood).

4. Context Creation
   - A combined JSON payload is created that merges the `current_readings` with a `historical_summary` describing detected trends.

5. Context-Aware Inference
   - The rich payload is passed to the local assistant, which compares the current reading to historical patterns and returns both immediate advice and longer-term recommendations.

This loop allows the assistant to become more personalized and useful over time as more sessions are logged.

## Project structure

- `cv_mindcare/` — main package
  - `cli/` — command-line entrypoint and interactive loop
  - `sensors/` — sensor wrappers (noise, camera-based greenery detection, simple emotion sampling)
  - `core/` — summarization and advice logic
  - `llm/` — helper functions for contextual prompts and model calls

## Quick start (no hardware required)

1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install runtime dependencies (optional for mock mode):

```powershell
pip install -r requirements.txt
```

3. Run the CLI with mock data (fast, no camera or microphone needed):

```powershell
python -m cv_mindcare.cli.main --mock
```

## Real sensor runs

- Noise sampling uses the local microphone (requires `sounddevice`)
- Greenery detection uses the webcam (requires `opencv-python`)
- Emotion sampling is optional and relies on `deepface` + webcam

If a dependency or hardware resource is missing, the sensors return a clear `available: False` result and the CLI will still provide fallback suggestions.

## Technology stack

- Python 3.9+
- sqlite3 (built-in) — stores `mindcare.db`
- pandas — analyzes historical data and prepares statistics
- numpy — numeric operations used by sensors
- sounddevice — microphone capture (optional)
- opencv-python — camera capture and simple image processing (optional)
- deepface — optional facial affect detection (optional)
- requests — HTTP client (used by local model wrappers if present)

## Setup & Usage

1) Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies:

```powershell
pip install -r requirements.txt
```

3) Initialize the database

The database (`mindcare.db`) will be created automatically the first time the application runs or when `database_manager.log_session_data()` is called. To explicitly initialize the database, run the CLI once (mock mode is fine):

```powershell
python -m cv_mindcare.cli.main --mock
```

This creates `mindcare.db` in the repository root and ensures the sessions table exists.

4) Run the assistant

- Quick test (no hardware):

```powershell
python -m cv_mindcare.cli.main --mock
```

- Real sensor run (requires microphone/webcam and optional model):

```powershell
python -m cv_mindcare.cli.main
```

The assistant is no longer stateless — it remembers past sessions and will provide personalized insights that improve with continued use.

## Key modules

- `cv_mindcare/sensors/` — wrappers for noise, camera-based greenery detection, and (optional) emotion sampling.
- `cv_mindcare/core/summary.py` — summarization and fallback advice logic for single sessions.
- `cv_mindcare/database_manager.py` — historical logging & analysis (new).
  - Responsibilities:
    - Creates and manages the `mindcare.db` SQLite database.
    - `log_session_data()` — saves a session entry (dominant emotion, counts, avg_db, classification, avg_green_pct).
    - `get_session_history(days=7)` — returns a pandas DataFrame with recent history.
    - `analyze_and_rank_trends(df)` — computes trends used to build AI context.
- `cv_mindcare/llm/ollama.py` — LLM helper functions and `create_context_for_ai()` to synthesize current readings + historical_summary.

## Context payload schema

When preparing context for the assistant, the application creates a two-part JSON object and passes it to the model. Example:

```json
{
  "current_readings": {
    "dominant_emotion": "sad",
    "avg_db": 65.5,
    "noise_classification": "Stress Zone",
    "avg_green_pct": 4.1
  },
  "historical_summary": {
    "most_frequent_emotion": "neutral",
    "noisiest_time_of_day": "afternoon",
    "insight": "Higher greenery levels correlate with more frequent 'happy' emotions in your history."
  }
}
```

The assistant's system prompt instructs it to first provide immediate, actionable advice based on `current_readings`, then to compare the current state to the historical trends and offer personalized, longer-term suggestions.

## Contributing

If you'd like to contribute, please open an issue or submit a pull request. For sensor changes, include notes on how you tested with mocked inputs or sample recordings/frames.

## License

MIT — see the `LICENSE` file for details.

---

## Quick Start (from Copilot Enhancement Blueprint)

### 1) Setup (Unix / macOS)

```bash
./setup.sh
```

### 1b) Setup (Windows PowerShell)

```powershell
.\setup.ps1
```

### 2) Run development mode

```bash
make run
```

### 3) Build & Serve production

```bash
make build && make serve
```

### 4) Run via Docker

```bash
docker build -t cvmindcare .
docker run -p 8000:8000 cvmindcare

# then open http://localhost:8000
```

Note: frontend dependencies include shadcn/ui, lucide-react, framer-motion and recharts. To initialize shadcn UI components run from `frontend/`:

```bash
npx shadcn@latest init
npx shadcn add card button input navbar toggle chart
```
