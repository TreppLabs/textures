"""
Unit tests for images API endpoints.
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
def sample_theme(test_db):
    """Create a sample theme for testing."""
    theme = Theme(
        name="Test Theme",
        description="Test description",
        base_prompt="test prompt"
    )
    test_db.add(theme)
    test_db.commit()
    test_db.refresh(theme)
    return theme


@pytest.fixture
def sample_generation(test_db, sample_theme):
    """Create a sample generation for testing."""
    generation = Generation(
        theme_id=sample_theme.id,
        base_prompt="test prompt",
        variation_params=json.dumps({"num_variations": 4})
    )
    test_db.add(generation)
    test_db.commit()
    test_db.refresh(generation)
    return generation


@pytest.fixture
def sample_image(test_db, sample_generation):
    """Create a sample image for testing."""
    image = Image(
        generation_id=sample_generation.id,
        filename="test_image.png",
        file_path="theme_1/gen_1/test_image.png",
        prompt="test prompt",
        keywords=json.dumps(["fractal", "organic"]),
        rating=None
    )
    test_db.add(image)
    test_db.commit()
    test_db.refresh(image)
    return image


class TestImagesAPI:
    """Test cases for images API endpoints."""
    
    def test_get_all_images(self, client, sample_image):
        """Test getting all images."""
        response = client.get("/api/images/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_recent_images(self, client, sample_image):
        """Test getting recent images."""
        response = client.get("/api/images/recent?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_images_by_theme(self, client, sample_theme, sample_generation, sample_image):
        """Test getting images by theme."""
        response = client.get(f"/api/images/theme/{sample_theme.id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["id"] == sample_image.id
    
    def test_get_top_image_per_theme(self, client, sample_theme, sample_generation, sample_image):
        """Test getting top image per theme."""
        response = client.get("/api/images/top-per-theme")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_image_by_id(self, client, sample_image):
        """Test getting a specific image by ID."""
        response = client.get(f"/api/images/{sample_image.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_image.id
        assert data["filename"] == sample_image.filename
    
    def test_get_image_not_found(self, client):
        """Test getting a non-existent image."""
        response = client.get("/api/images/99999")
        assert response.status_code == 404
    
    def test_rate_image(self, client, sample_image):
        """Test rating an image."""
        rating_data = {"rating": 5}
        response = client.post(f"/api/images/{sample_image.id}/rate", json=rating_data)
        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == 5
        assert data["image_id"] == sample_image.id
    
    def test_rate_image_invalid_rating(self, client, sample_image):
        """Test rating with invalid rating value."""
        rating_data = {"rating": 6}  # Invalid: should be 1-5
        response = client.post(f"/api/images/{sample_image.id}/rate", json=rating_data)
        assert response.status_code == 400
    
    def test_rate_image_zero_rating(self, client, sample_image):
        """Test rating with zero rating."""
        rating_data = {"rating": 0}  # Invalid: should be 1-5
        response = client.post(f"/api/images/{sample_image.id}/rate", json=rating_data)
        assert response.status_code == 400
    
    def test_rate_image_not_found(self, client):
        """Test rating a non-existent image."""
        rating_data = {"rating": 5}
        response = client.post("/api/images/99999/rate", json=rating_data)
        assert response.status_code == 404
    
    def test_filter_images_by_min_rating(self, client, sample_image):
        """Test filtering images by minimum rating."""
        # First, rate the image
        client.post(f"/api/images/{sample_image.id}/rate", json={"rating": 4})
        
        # Filter by minimum rating
        response = client.get("/api/images/?min_rating=4")
        assert response.status_code == 200
        data = response.json()
        assert all(img["rating"] >= 4 for img in data if img.get("rating"))

