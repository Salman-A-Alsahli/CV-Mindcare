# Archived Files

This directory contains files from the original CV Mindcare implementation that were deprecated as part of the hybrid architecture redesign.

## Contents of `/original_backend`

1. `WholeSystem.py`
   - Reason: Replaced by new modular architecture with separate launcher, backend, and frontend
   - Status: Deprecated - keeping for reference of original implementation

2. `run_app.py`
   - Reason: New architecture uses launcher-based startup instead of direct script execution
   - Status: Deprecated - functionality moved to launcher/launcher.py

3. `cv_mindcare/` directory
   - Reason: Code being restructured into new modular architecture
   - Status: Will be refactored into new backend/sensors and backend/models structure

4. `setup.sh` and `setup.ps1`
   - Reason: Setup process being replaced with new launcher-based system checks
   - Status: Deprecated - functionality moved to launcher system check module

5. `setup.cfg`
   - Reason: Moving to more modern pyproject.toml-based configuration
   - Status: Deprecated - configuration now in pyproject.toml

## Note

These files are preserved for reference and historical purposes. The new architecture implements the same functionality in a more modular and maintainable way, with:

- A desktop launcher (system checks and process management)
- A Flask/FastAPI backend (sensor data collection and processing)
- A web-based dashboard (data visualization and control)

Do not use these archived files in the new implementation.