# Backend Tests

This directory contains unit tests for the backend functionality.

## Running Tests

From the `backend` directory:

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run a specific test file
pytest tests/test_keyword_extractor.py

# Run a specific test
pytest tests/test_keyword_extractor.py::TestKeywordExtractor::test_extract_keywords_simple

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Test Structure

- `conftest.py` - Pytest fixtures and configuration
- `test_keyword_extractor.py` - Tests for keyword extraction and analysis
- `test_rating_analyzer.py` - Tests for rating analysis and pattern recognition
- `test_prompt_engine.py` - Tests for prompt variation generation
- `test_theme_manager.py` - Tests for theme management (CRUD operations)
- `test_api_themes.py` - Tests for themes API endpoints
- `test_api_images.py` - Tests for images API endpoints
- `test_api_analytics.py` - Tests for analytics API endpoints

## Test Database

Tests use an in-memory SQLite database that is created and destroyed for each test, ensuring test isolation.

## Dependencies

All test dependencies are included in `requirements.txt`:
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support

