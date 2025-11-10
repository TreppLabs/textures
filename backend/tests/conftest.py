"""
Pytest configuration and fixtures for backend tests.
"""

import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import models and database setup
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from models.database import Base, get_db
from models.schemas import Theme, Generation, Image, Keyword, PromptHistory


@pytest.fixture(scope="function")
def test_db():
    """Create a temporary in-memory SQLite database for testing."""
    # Create in-memory database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create a session
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_theme_data():
    """Sample theme data for testing."""
    return {
        "name": "Test Theme",
        "description": "A test theme",
        "base_prompt": "organic cellular structure with ##flowing lines, ##fractal patterns"
    }


@pytest.fixture
def sample_image_data():
    """Sample image data for testing."""
    return {
        "filename": "test_image.png",
        "file_path": "theme_1/gen_1/test_image.png",
        "prompt": "organic cellular structure with ##flowing lines",
        "keywords": '["flowing", "cellular"]',
        "rating": 4
    }


@pytest.fixture
def sample_generation_data():
    """Sample generation data for testing."""
    return {
        "session_name": "Test Generation",
        "base_prompt": "organic cellular structure",
        "variation_params": '{"num_variations": 4}'
    }


@pytest.fixture
def sample_theme_history():
    """Sample theme history for rating analysis."""
    return [
        {
            "prompt": "organic structure with ##fractal patterns",
            "rating": 5,
            "keywords": ["fractal", "organic"],
            "created_at": "2024-01-01T00:00:00"
        },
        {
            "prompt": "geometric pattern with ##grid lines",
            "rating": 2,
            "keywords": ["grid", "geometric"],
            "created_at": "2024-01-02T00:00:00"
        },
        {
            "prompt": "organic structure with ##flowing lines",
            "rating": 4,
            "keywords": ["flowing", "organic"],
            "created_at": "2024-01-03T00:00:00"
        },
        {
            "prompt": "cellular structure with ##voronoi patterns",
            "rating": 5,
            "keywords": ["voronoi", "cellular"],
            "created_at": "2024-01-04T00:00:00"
        },
        {
            "prompt": "geometric pattern with ##angular shapes",
            "rating": 3,
            "keywords": ["angular", "geometric"],
            "created_at": "2024-01-05T00:00:00"
        }
    ]


@pytest.fixture
def mock_openai_client(monkeypatch):
    """Mock OpenAI client to avoid API calls during testing."""
    class MockOpenAIClient:
        def __init__(self):
            self.api_key = "test-key"
        
        async def generate_texture_variations(self, base_prompt, num_variations=4, size="1024x1024", quality="standard"):
            """Mock image generation."""
            variations = []
            for i in range(num_variations):
                variations.append({
                    "prompt": f"{base_prompt} variation {i+1}",
                    "image_url": f"https://example.com/image_{i+1}.png",
                    "revised_prompt": f"{base_prompt} variation {i+1} (revised)"
                })
            return variations
    
    monkeypatch.setattr("core.openai_client.OpenAIClient", MockOpenAIClient)
    return MockOpenAIClient()


@pytest.fixture
def theme_manager(test_db):
    """Create a ThemeManager instance with test database."""
    from core.theme_manager import ThemeManager
    manager = ThemeManager()
    # Override the db session with our test database
    # Note: ThemeManager will try to close the db in finally blocks,
    # but we prevent that by not calling close on the test_db
    original_close = test_db.close
    test_db.close = lambda: None  # Prevent closing test_db
    manager.db = test_db
    yield manager
    # Restore original close method
    test_db.close = original_close

