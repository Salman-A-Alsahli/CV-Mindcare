CV Mindcare — Computer Vision Mental Health Assistant

Project layout (created by refactor):

cv_mindcare/
  __init__.py
  __main__.py
  sensors/
    __init__.py
    noise.py
    vision.py
    emotion.py
  llm/
    __init__.py
    ollama.py
  core/
    __init__.py
    summary.py
  cli/
    __init__.py
    main.py

How to run:
  python -m cv_mindcare.cli.main --mock

Notes:
- This refactor separates the original monolithic script into modules.
- Hardware-dependent modules gracefully return availability=False when deps are missing.
- Next steps: add unit tests, packaging (setup.cfg/pyproject.toml), type-checking and CI.
