CV Mindcare — Computer Vision Mental Health Assistant

Project layout (created by refactor):

cv_mindcare/
  __init__.py
  # CV Mindcare

  CV Mindcare is a small toolkit that inspects local environmental signals (sound level, presence of greenery in a camera view, and brief facial affect sampling) and provides human-readable observations and practical suggestions to improve a room or workspace. The project is intended as a privacy-respecting local utility for personal wellbeing and workspace optimization.

  This repository contains sensor wrappers, a small summary engine, and a command-line interface to run quick environment checks.

  Project structure

  - `cv_mindcare/` — main package
    - `cli/` — command-line entrypoint and interactive loop
    - `sensors/` — sensor wrappers (noise, camera-based greenery detection, simple emotion sampling)
    - `core/` — summarization and advice logic
    - `llm/` — optional helper for local text generation (kept in the tree but not required)

  Quick start (no hardware required)

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

  Real sensor runs

  - Noise sampling uses the local microphone (requires `sounddevice`)
  - Greenery detection uses the webcam (requires `opencv-python`)
  - Emotion sampling is optional and relies on `deepface` + webcam

  If a dependency or hardware resource is missing, the sensors return a clear `available: False` result and the CLI will still provide fallback suggestions.

  Developer notes

  - Tests: `tests/` contains a basic test for the summarization logic. Use `pytest` to run tests.
  - CI: A GitHub Actions workflow runs the test suite on push/PRs to `main`.
  - Packaging: `pyproject.toml` / `setup.cfg` are included for easy packaging.

  Contributing

  If you'd like to contribute, please open an issue or submit a pull request with small, focused changes. For sensor code changes, include a note about how you tested it (mocked inputs are fine).

  License

  This project is released under the MIT License. See the `LICENSE` file for details.
