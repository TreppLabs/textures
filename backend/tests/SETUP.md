# Test Setup Instructions

## Initial Setup

1. **Create and activate virtual environment** (if not already done):
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

2. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install pytest pytest-asyncio fastapi sqlalchemy pydantic python-dotenv httpx openai
   ```

   Note: Pillow may have compatibility issues with Python 3.13. If you need it for image processing, you can install a newer version:
   ```bash
   pip install Pillow
   ```

## Running Tests

**Always activate the virtual environment first:**
```bash
source venv/bin/activate  # On macOS/Linux
```

Then run tests:
```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run a specific test file
pytest tests/test_keyword_extractor.py

# Run with shorter traceback
pytest tests/ --tb=short
```

## Quick Test Command

You can also use the provided script:
```bash
./run_tests.sh
```

Make sure it's executable:
```bash
chmod +x run_tests.sh
```

