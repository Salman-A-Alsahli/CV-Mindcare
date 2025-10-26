# Development Guide - CV-Mindcare

Guide for developers who want to contribute to or extend CV-Mindcare.

## Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Development Environment](#development-environment)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Code Style](#code-style)
- [Contributing](#contributing)
- [Architecture](#architecture)

## Getting Started

### Prerequisites

- Python 3.9+
- Git
- Code editor (VS Code recommended)
- Windows 10/11

### Clone and Setup

```powershell
# Clone repository
git clone https://github.com/Salman-A-Alsahli/CV-Mindcare.git
cd CV-Mindcare

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install pytest pytest-cov pytest-mock black flake8 pre-commit
```

## Project Structure

```
CV-Mindcare/
├── backend/              # FastAPI backend server
│   ├── app.py           # Main FastAPI application
│   ├── database.py      # SQLite database layer
│   ├── models.py        # Pydantic data models
│   └── sensors/         # Sensor modules
│       ├── __init__.py
│       ├── camera.py    # Camera/face detection
│       ├── microphone.py # Sound monitoring
│       └── system_monitor.py # System resources
├── frontend/            # Web dashboard
│   ├── index.html      # Main HTML
│   ├── css/
│   │   └── styles.css  # Custom styles
│   └── js/
│       └── dashboard.js # Dashboard logic
├── launcher/            # Desktop launcher app
│   ├── launcher.py     # Main GUI
│   ├── process_manager.py # Backend lifecycle
│   └── system_check.py # System validation
├── docs/                # Documentation
│   ├── INSTALLATION.md
│   ├── API.md
│   ├── DEVELOPMENT.md (this file)
│   └── README.md
├── tests/               # Test suite
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── requirements.txt     # Python dependencies
├── pyproject.toml      # Project configuration
└── README.md           # Main documentation
```

### Key Files

- **backend/app.py**: REST API endpoints
- **backend/database.py**: Database schema and CRUD operations
- **backend/sensors/*.py**: Sensor data collection modules
- **launcher/launcher.py**: Desktop application GUI
- **launcher/process_manager.py**: Backend process management
- **frontend/js/dashboard.js**: Web dashboard logic

## Development Environment

### VS Code Setup

Recommended extensions:
- Python (Microsoft)
- Pylance
- Python Test Explorer
- GitLens
- Better Comments

### VS Code Settings

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "100"],
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false
}
```

### Environment Variables

Create `.env` file for development:

```env
# Backend
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
DATABASE_PATH=backend/cv_mindcare.db

# Frontend
FRONTEND_PORT=3000

# Development
DEBUG=True
LOG_LEVEL=INFO
```

## Running the Application

### Run Backend Only

```powershell
cd backend
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

The `--reload` flag enables auto-reload on code changes.

### Run Frontend Only

Open `frontend/index.html` in a browser, or use a local server:

```powershell
cd frontend
python -m http.server 3000
```

### Run Launcher

```powershell
python -m launcher.launcher
```

Or:

```powershell
python launcher/launcher.py
```

### Run Full System

The launcher automatically starts the backend, so just run:

```powershell
python -m launcher.launcher
```

## Testing

### Running Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov=launcher --cov-report=html

# Run specific test file
pytest tests/unit/test_database.py

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

### Writing Tests

#### Unit Test Example

Create `tests/unit/test_database.py`:

```python
import pytest
from backend.database import insert_sensor_data, get_recent_sensor_data

def test_insert_and_retrieve_sensor_data():
    # Insert test data
    insert_sensor_data("test_sensor", 42.0)
    
    # Retrieve and verify
    recent = get_recent_sensor_data(limit=1)
    assert len(recent) == 1
    assert recent[0]["sensor_type"] == "test_sensor"
    assert recent[0]["value"] == 42.0
```

#### Integration Test Example

Create `tests/integration/test_api_database.py`:

```python
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_post_and_get_sensor():
    # Post data
    response = client.post("/api/sensors", json={
        "sensor_type": "test",
        "value": 100.0
    })
    assert response.status_code == 201
    
    # Get data
    response = client.get("/api/sensors")
    assert response.status_code == 200
    data = response.json()
    assert "recent" in data
```

### Test Coverage

Aim for:
- Backend: 80%+ coverage
- Launcher: 70%+ coverage
- Sensors: 75%+ coverage

View coverage report:

```powershell
pytest --cov=backend --cov=launcher --cov-report=html
start htmlcov/index.html
```

## Code Style

### Python Style Guide

Follow PEP 8 with these modifications:
- Line length: 100 characters
- Use double quotes for strings
- Use Black for formatting

### Formatting

```powershell
# Format all Python files
black .

# Format specific file
black backend/app.py

# Check without modifying
black --check .
```

### Linting

```powershell
# Run flake8
flake8 backend/ launcher/

# With specific rules
flake8 --max-line-length=100 --ignore=E203,W503 backend/
```

### Type Hints

Use type hints for all functions:

```python
from typing import Dict, List, Optional

def get_sensor_data(sensor_type: str, limit: int = 10) -> List[Dict[str, any]]:
    """Get recent sensor data."""
    # Implementation
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def calculate_average(values: List[float]) -> float:
    """
    Calculate the average of a list of values.
    
    Args:
        values: List of numeric values
        
    Returns:
        Average value as float
        
    Raises:
        ValueError: If values list is empty
        
    Example:
        >>> calculate_average([1, 2, 3])
        2.0
    """
    if not values:
        raise ValueError("Cannot calculate average of empty list")
    return sum(values) / len(values)
```

## Contributing

### Workflow

1. **Fork and Clone**
   ```powershell
   git clone https://github.com/YOUR_USERNAME/CV-Mindcare.git
   ```

2. **Create Branch**
   ```powershell
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

4. **Test**
   ```powershell
   pytest
   black .
   flake8
   ```

5. **Commit**
   ```powershell
   git add .
   git commit -m "feat: add your feature description"
   ```

6. **Push and PR**
   ```powershell
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub

### Commit Message Format

Use conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding tests
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Maintenance tasks

Examples:
```
feat: add emotion detection to camera sensor
fix: resolve database connection timeout
docs: update API documentation for live endpoint
test: add integration tests for launcher
```

### Code Review Checklist

- [ ] Tests pass
- [ ] Code formatted with Black
- [ ] No linting errors
- [ ] Documentation updated
- [ ] Type hints added
- [ ] Docstrings written
- [ ] No breaking changes (or documented)

## Architecture

### Backend Architecture

```
FastAPI App
    ├── Endpoints (app.py)
    ├── Database Layer (database.py)
    ├── Models (models.py)
    └── Sensors
        ├── Camera
        ├── Microphone
        └── System Monitor
```

### Data Flow

```
Sensors → Backend API → Database → Dashboard
           ↑                           ↓
           └─────── Launcher ──────────┘
```

1. **Sensors** collect data (camera, mic, system)
2. **Backend API** receives and stores data
3. **Database** persists historical records
4. **Dashboard** polls API for live updates
5. **Launcher** manages backend lifecycle

### Database Schema

- **sensor_data**: Generic sensor readings
- **face_detection**: Face detection results
- **sound_analysis**: Audio level measurements

### Adding New Sensors

1. Create sensor module in `backend/sensors/`:

```python
# backend/sensors/my_sensor.py

class MySensor:
    def __init__(self):
        pass
    
    def is_available(self) -> bool:
        """Check if sensor is available."""
        return True
    
    def get_reading(self) -> Dict[str, any]:
        """Get sensor reading."""
        return {
            "value": 42.0,
            "available": True
        }
```

2. Add API endpoint in `backend/app.py`:

```python
@app.get("/api/my-sensor")
async def get_my_sensor() -> Dict[str, any]:
    sensor = MySensor()
    return sensor.get_reading()
```

3. Update dashboard to display data

4. Add tests

### Adding New API Endpoints

1. Define Pydantic model in `backend/models.py`
2. Add endpoint in `backend/app.py`
3. Update `docs/API.md`
4. Write tests

## Debugging

### Backend Debugging

Add breakpoints and run with debugger:

```powershell
# VS Code: F5 or Debug → Start Debugging
```

Or use print debugging:

```python
print(f"DEBUG: Sensor value = {value}")
```

### Launcher Debugging

Add log messages:

```python
self._add_log_line(f"DEBUG: Backend status = {status}")
```

### Database Debugging

```powershell
# Open database
sqlite3 backend/cv_mindcare.db

# View tables
.tables

# Query data
SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10;

# Exit
.quit
```

## Performance Tips

- Use async/await in FastAPI endpoints for I/O operations
- Implement database connection pooling for high load
- Cache frequently accessed data
- Use indexes on timestamp columns
- Limit query results with LIMIT clause

## Security Considerations

- Never commit `.env` files
- Sanitize user inputs
- Use parameterized SQL queries (already done)
- Add authentication for production
- Enable HTTPS in production
- Validate all API inputs with Pydantic

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [CustomTkinter Docs](https://customtkinter.tomschimansky.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Python Testing with pytest](https://docs.pytest.org/)

---

**Version**: 0.1.0  
**Last Updated**: October 26, 2025  
**Questions?**: Open an issue on GitHub
