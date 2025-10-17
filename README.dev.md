Development notes

- To run tests: pip install -r requirements.txt; pip install pytest; pytest
- To run CLI: python -m cv_mindcare.cli.main --mock
- To format: black .; lint: flake8 cv_mindcare
- To add new sensors, create modules under cv_mindcare/sensors and export in sensors/__init__.py
