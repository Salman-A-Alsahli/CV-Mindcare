# CI/CD Pipeline Documentation

## Overview

CV-Mindcare uses GitHub Actions for continuous integration and continuous deployment. The CI/CD pipeline ensures code quality, security, and reliability through automated testing, linting, and security scanning.

## Workflows

### 1. Tests Workflow (`test.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**
- **Matrix Testing**: Tests against Python 3.10, 3.11, and 3.12
- **Unit Tests**: Runs all unit tests with coverage reporting
- **Coverage Upload**: Uploads coverage to Codecov

**Usage:**
```bash
# Run locally
pytest tests/unit/ -v --cov=backend --cov-report=term
```

### 2. Lint Workflow (`lint.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**
- **Black**: Code formatting check
- **Flake8**: Linting and style check
- **MyPy**: Type checking (non-blocking)

**Usage:**
```bash
# Run locally
black --check backend/ tests/
flake8 backend/ tests/ --max-line-length=100 --extend-ignore=E203,W503
mypy backend/ --ignore-missing-imports --no-strict-optional
```

**Auto-fix formatting:**
```bash
black backend/ tests/
```

### 3. Security Workflow (`security.yml`)

**Triggers:**
- Push to `main` branch
- Pull requests to `main` branch
- Weekly schedule (Monday at midnight)

**Jobs:**
- **CodeQL Analysis**: Scans for security vulnerabilities
- **Dependency Check**: Checks dependencies for known vulnerabilities using `safety`

**Usage:**
```bash
# Run dependency check locally
pip install safety
safety check -r requirements-base.txt
```

## Pre-Commit Hooks

Pre-commit hooks run automatically before each commit to catch issues early.

### Setup

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

### Hooks Configured

1. **Trailing Whitespace**: Removes trailing whitespace
2. **End of File Fixer**: Ensures files end with newline
3. **YAML/JSON/TOML Check**: Validates syntax
4. **Large Files Check**: Prevents committing large files (>1MB)
5. **Merge Conflict Check**: Detects merge conflict markers
6. **Private Key Detection**: Prevents committing private keys
7. **Black**: Automatically formats code
8. **Flake8**: Lints code
9. **MyPy**: Type checks code

### Bypassing Hooks

Only in exceptional cases:
```bash
git commit --no-verify -m "message"
```

## Code Quality Standards

### Black Configuration

- **Line length**: 100 characters
- **Target**: Python 3.10+
- **Style**: PEP 8 compliant with Black defaults

### Flake8 Configuration

- **Max line length**: 100
- **Ignored**: E203 (whitespace before ':'), W503 (line break before binary operator)

### MyPy Configuration

- **Ignore missing imports**: Yes
- **Strict optional**: No (for gradual typing adoption)

## Test Coverage

### Current Coverage

- **Overall**: >80% target
- **Backend**: Full coverage of core modules
- **Sensors**: Mock mode allows testing without hardware

### Coverage Reports

- **Terminal**: Displayed after each test run
- **XML**: Generated for Codecov upload
- **HTML**: Generate with `pytest --cov=backend --cov-report=html`

### Viewing Coverage

```bash
# Generate HTML report
pytest tests/unit/ --cov=backend --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Continuous Deployment

### Version Tagging

```bash
# Create release tag
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

### Release Process

1. **Merge to main**: All features merged via pull requests
2. **Version bump**: Update version in `backend/app.py`
3. **Tag release**: Create git tag with version
4. **GitHub Release**: Create release notes

### Branch Strategy

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/**: Individual feature branches
- **hotfix/**: Critical bug fixes

## Troubleshooting

### Test Failures

```bash
# Run specific test
pytest tests/unit/test_analytics.py::test_aggregate_data -v

# Run with detailed output
pytest tests/unit/ -vv

# Run failed tests only
pytest --lf
```

### Linting Issues

```bash
# Auto-fix with Black
black backend/ tests/

# Check specific file
flake8 backend/analytics.py
```

### Pre-commit Issues

```bash
# Update hooks
pre-commit autoupdate

# Clean and reinstall
pre-commit clean
pre-commit install
```

### CI Workflow Debugging

```bash
# Install act for local CI testing
# https://github.com/nektos/act

# Run workflows locally
act push
act pull_request
```

## Best Practices

### Before Committing

1. Run tests: `pytest tests/unit/ -v`
2. Check formatting: `black --check .`
3. Run linter: `flake8 .`
4. Update tests for new code
5. Update documentation

### Pull Requests

1. Create feature branch from `develop`
2. Write descriptive commit messages
3. Include tests for new features
4. Update documentation
5. Request code review
6. Address review comments
7. Squash commits if needed

### Code Review Checklist

- [ ] All tests passing
- [ ] Code coverage maintained/improved
- [ ] Linting checks pass
- [ ] Security checks pass
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Meaningful commit messages

## Performance Optimization

### CI Pipeline Speed

- **Caching**: pip packages cached by GitHub Actions
- **Matrix strategy**: Parallel testing across Python versions
- **Early failure**: Fail fast on first test failure

### Local Development

```bash
# Run only changed tests
pytest tests/unit/ -v --lf

# Run specific test categories
pytest tests/unit/test_sensors*.py -v

# Skip slow tests
pytest tests/unit/ -v -m "not slow"
```

## Security

### Secret Management

- **Never commit**: API keys, passwords, tokens
- **Use GitHub Secrets**: For sensitive CI/CD variables
- **Rotate regularly**: Change secrets periodically

### Dependency Updates

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update requirements file
pip freeze > requirements-base.txt
```

### Security Scanning

- **CodeQL**: Weekly automated scans
- **Safety**: Dependency vulnerability checks
- **Manual review**: For critical changes

## Monitoring

### GitHub Actions Dashboard

- View workflow runs: Repository → Actions
- Check job logs for failures
- Download artifacts from successful runs

### Codecov Dashboard

- View coverage trends over time
- Identify uncovered code
- Track coverage changes per PR

## Support

For CI/CD issues:
1. Check workflow logs in GitHub Actions
2. Run tests locally to reproduce
3. Review this documentation
4. Create issue with workflow logs

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Codecov Documentation](https://docs.codecov.com/)
