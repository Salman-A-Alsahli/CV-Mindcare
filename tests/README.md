# Tests

This directory contains all tests for the CV-Mindcare system.

## Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests across modules
├── e2e/            # End-to-end tests
└── fixtures/       # Test data and fixtures
```

## Test Categories

### Unit Tests
- **Backend Tests**
  - API endpoint tests
  - Database function tests
  - Sensor module tests
  
- **Frontend Tests**
  - Dashboard component tests
  - API integration tests
  
- **Launcher Tests**
  - System check tests
  - Process management tests

### Integration Tests
- Launcher → Backend integration
- Backend → Database integration
- Frontend → Backend API integration

### End-to-End Tests
- Complete system workflow
- User scenario testing

## Running Tests

### All Tests
```bash
pytest
```

### Specific Test Category
```bash
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

### With Coverage
```bash
pytest --cov=backend --cov=launcher --cov-report=html
```

### Watch Mode
```bash
pytest-watch
```

## Test Requirements

- pytest - Testing framework
- pytest-cov - Coverage reporting
- pytest-mock - Mocking support
- httpx - Async HTTP client for API testing

## Writing Tests

### Backend API Test Example
```python
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"
```

### Database Test Example
```python
from backend.database import insert_sensor_data, get_recent_sensor_data

def test_sensor_data_storage():
    insert_sensor_data("test_sensor", 42.0)
    recent = get_recent_sensor_data(limit=1)
    assert len(recent) == 1
    assert recent[0]["sensor_type"] == "test_sensor"
```

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Commits to main branch
- Pre-commit hooks (if configured)

## Coverage Goals

- Backend: 80%+ coverage
- Launcher: 70%+ coverage
- Frontend: 60%+ coverage (JavaScript)

## Test Data

Mock data and fixtures are stored in `tests/fixtures/`:
- Mock sensor readings
- Sample database states
- Test configuration files
