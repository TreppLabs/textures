"""
Unit tests for analytics API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os
import json
import importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

# Import app with proper path handling
spec = importlib.util.spec_from_file_location("main", os.path.join(os.path.dirname(__file__), '../src/main.py'))
main_module = importlib.util.module_from_spec(spec)
sys.modules['main'] = main_module
spec.loader.exec_module(main_module)
app = main_module.app
from models.schemas import Theme, Generation, Image


@pytest.fixture
def client(test_db):
    """
    Create a test client with database override.
    
    This ensures all API calls use the test database, never production.
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            # Don't close test_db here - it's managed by the test_db fixture
            pass
    
    # Clear any existing overrides first
    app.dependency_overrides = {}
    from models.database import get_db
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    yield client
    
    # Clean up: remove dependency overrides after test
    app.dependency_overrides.clear()


@pytest.fixture
def theme_with_rated_images(test_db):
    """Create a theme with rated images for analytics testing."""
    # Create theme
    theme = Theme(
        name="Analytics Test Theme",
        base_prompt="organic structure with ##fractal ##flowing patterns"
    )
    test_db.add(theme)
    test_db.commit()
    test_db.refresh(theme)
    
    # Create generation
    generation = Generation(
        theme_id=theme.id,
        base_prompt=theme.base_prompt
    )
    test_db.add(generation)
    test_db.commit()
    test_db.refresh(generation)
    
    # Create images with ratings
    images = [
        Image(
            generation_id=generation.id,
            filename=f"img_{i}.png",
            file_path=f"theme_{theme.id}/gen_{generation.id}/img_{i}.png",
            prompt=f"organic with ##fractal patterns",
            keywords=json.dumps(["fractal", "organic"]),
            rating=5 if i < 2 else 2  # First 2 are high-rated
        )
        for i in range(4)
    ]
    
    # Add some with different keywords
    images.append(Image(
        generation_id=generation.id,
        filename="img_4.png",
        file_path=f"theme_{theme.id}/gen_{generation.id}/img_4.png",
        prompt="geometric with ##grid patterns",
        keywords=json.dumps(["grid", "geometric"]),
        rating=1
    ))
    
    for img in images:
        test_db.add(img)
    test_db.commit()
    
    return theme


class TestAnalyticsAPI:
    """Test cases for analytics API endpoints."""
    
    def test_get_keyword_analysis_all_themes(self, client, theme_with_rated_images):
        """Test getting keyword analysis for all themes."""
        response = client.get("/api/analytics/keywords")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_keyword_analysis_by_theme(self, client, theme_with_rated_images):
        """Test getting keyword analysis for a specific theme."""
        response = client.get(f"/api/analytics/keywords?theme_id={theme_with_rated_images.id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_keyword_analysis_with_min_uses(self, client, theme_with_rated_images):
        """Test getting keyword analysis with minimum uses filter."""
        response = client.get("/api/analytics/keywords?min_uses=2")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_theme_performance(self, client, theme_with_rated_images):
        """Test getting theme performance analytics."""
        response = client.get("/api/analytics/themes/performance")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_analytics_summary(self, client, theme_with_rated_images):
        """Test getting analytics summary."""
        response = client.get("/api/analytics/summary")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Should have summary statistics
        assert "total_themes" in data or "total_images" in data or "total_ratings" in data

