# Contributing to CV-Mindcare

Thank you for your interest in contributing to CV-Mindcare! This document provides guidelines and information about contributing to this project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Issue Management](#issue-management)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)

## Code of Conduct
This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

### Prerequisites
- Python 3.9 or higher
- Git
- Node.js and npm (for frontend development)
- Visual Studio Code (recommended)

### Development Setup
1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/CV-Mindcare.git
   cd CV-Mindcare
   ```
3. Set up Python environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```
4. Set up frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

## Issue Management

### Issue Labels
- `priority: high/medium/low` - Indicates task urgency
- `good first issue` - Beginner-friendly tasks
- `help wanted` - Tasks needing contributors
- `bug` - Something isn't working
- `feature` - New feature or request
- `documentation` - Documentation improvements
- `enhancement` - Improvements to existing features

### Working on Issues
1. Comment on an issue you want to work on
2. Wait for assignment or approval
3. Create a branch: `feature/issue-number-brief-description`
4. Follow the issue template and acceptance criteria
5. Update the issue with progress regularly

## Making Changes

### Branching Strategy
- `master` - Main development branch
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `docs/*` - Documentation updates

### Commit Messages
Follow conventional commits format:
- `feat: add new feature`
- `fix: resolve bug issue`
- `docs: update documentation`
- `refactor: improve code structure`
- `test: add tests`

## Pull Request Process
1. Update documentation if needed
2. Add or update tests
3. Ensure all tests pass
4. Update the README.md if needed
5. Link the PR to relevant issues
6. Request review from maintainers
7. Address review comments

## Code Style
- Python: Follow PEP 8
- JavaScript: Use ESLint with project config
- Use type hints in Python code
- Comment complex logic
- Write clear, descriptive variable names

## Review Process
1. Automated checks must pass
2. At least one maintainer approval required
3. All conversations must be resolved
4. Documentation must be updated

## Questions?
Feel free to open an issue or contact the maintainers.