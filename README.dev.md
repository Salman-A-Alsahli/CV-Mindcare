Development notes

This file describes common developer workflows.

Run tests

1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies and run tests:

```powershell
pip install -r requirements.txt
pip install pytest
pytest -q
```

Formatting and linting

Install formatting and linting tools and run them:

```powershell
pip install black flake8 isort
black .
isort .
flake8 cv_mindcare
```

Adding sensors

To add a sensor, create a new module under `cv_mindcare/sensors`, provide a clean function API that returns a dictionary with `available` and result fields, and export it from `cv_mindcare/sensors/__init__.py`.

