# Tests Directory

This directory contains the test suite for the Flask Survey Form application.

## Current Test Structure

### End-to-End Tests (JavaScript)
- **Location**: `tests/e2e/`
- **Framework**: JavaScript-based (Playwright/Jest)
- **Purpose**: Full browser automation tests
- **Files**:
  - `survey_form.spec.js` - Main form submission tests
  - `form_validation.spec.js` - Form validation tests
  - `attachment.spec.js` - File attachment tests
  - `edit_form.spec.js` - Form editing tests
  - `export.spec.js` - Data export tests
  - `bulk_add_trainees.spec.js` - Bulk operations tests
  - `quarter_function.spec.js` - Quarter calculation tests

### Python Unit Tests
- **Status**: Not implemented yet
- **Future Location**: `tests/unit/`
- **Framework**: pytest (when implemented)

## Current Testing Strategy

Since there are no Python unit tests yet, the GitHub Actions workflow uses `simple_test.py` in the root directory to validate:
- Module imports
- Configuration loading
- Database connectivity
- Flask application creation

## Adding Python Unit Tests

To add Python unit tests in the future:

1. Create `tests/unit/` directory
2. Add test files following pytest naming convention (`test_*.py`)
3. Install pytest: `pip install pytest pytest-flask`
4. Update GitHub Actions workflow to use pytest

Example test structure:
```
tests/
├── unit/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_forms.py
│   ├── test_auth.py
│   └── test_utils.py
└── e2e/
    └── (existing JavaScript tests)
``` 