"""
Unit tests for themes API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

# Import app with proper path handling
import importlib.util
spec = importlib.util.spec_from_file_location("main", os.path.join(os.path.dirname(__file__), '../src/main.py'))
main_module = importlib.util.module_from_spec(spec)
sys.modules['main'] = main_module
spec.loader.exec_module(main_module)
app = main_module.app


@pytest.fixture
def client(test_db):
    """
    Create a test client with database override.
    
    This ensures all API calls use the test database, never production.
    """
    # Override get_db dependency to use test database
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


class TestThemesAPI:
    """Test cases for themes API endpoints."""
    
    def test_get_themes_empty(self, client):
        """Test getting themes when none exist."""
        response = client.get("/api/themes/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_theme(self, client):
        """Test creating a theme."""
        theme_data = {
            "name": "Test Theme",
            "description": "A test theme",
            "base_prompt": "organic structure with ##fractal patterns"
        }
        
        response = client.post("/api/themes/", json=theme_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == theme_data["name"]
        assert "id" in data
        assert data["id"] > 0
    
    def test_create_theme_missing_fields(self, client):
        """Test creating theme with missing required fields."""
        theme_data = {
            "name": "Test Theme"
            # Missing base_prompt
        }
        
        response = client.post("/api/themes/", json=theme_data)
        assert response.status_code == 422  # Validation error
    
    def test_get_theme(self, client):
        """Test getting a specific theme."""
        # Create a theme first
        theme_data = {
            "name": "Test Theme",
            "base_prompt": "test prompt"
        }
        create_response = client.post("/api/themes/", json=theme_data)
        theme_id = create_response.json()["id"]
        
        # Get the theme
        response = client.get(f"/api/themes/{theme_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == theme_id
        assert data["name"] == theme_data["name"]
    
    def test_get_theme_not_found(self, client):
        """Test getting a non-existent theme."""
        response = client.get("/api/themes/99999")
        assert response.status_code == 404
    
    def test_update_theme(self, client):
        """Test updating a theme."""
        # Create a theme
        theme_data = {
            "name": "Original Name",
            "base_prompt": "original prompt"
        }
        create_response = client.post("/api/themes/", json=theme_data)
        theme_id = create_response.json()["id"]
        
        # Update the theme
        update_data = {
            "name": "Updated Name",
            "base_prompt": "updated prompt"
        }
        response = client.put(f"/api/themes/{theme_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["base_prompt"] == "updated prompt"
    
    def test_branch_theme(self, client):
        """Test branching a theme."""
        # Create parent theme
        parent_data = {
            "name": "Parent Theme",
            "base_prompt": "parent prompt"
        }
        parent_response = client.post("/api/themes/", json=parent_data)
        parent_id = parent_response.json()["id"]
        
        # Branch the theme
        branch_data = {
            "name": "Branched Theme",
            "base_prompt": "branched prompt"
        }
        response = client.post(f"/api/themes/{parent_id}/branch", json=branch_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Branched Theme"
        assert data["parent_theme_id"] == parent_id
    
    def test_get_theme_statistics(self, client):
        """Test getting theme statistics."""
        # Create a theme
        theme_data = {
            "name": "Test Theme",
            "base_prompt": "test prompt"
        }
        create_response = client.post("/api/themes/", json=theme_data)
        theme_id = create_response.json()["id"]
        
        # Get statistics
        response = client.get(f"/api/themes/{theme_id}/statistics")
        assert response.status_code == 200
        data = response.json()
        assert data["theme_id"] == theme_id
        assert "generations_count" in data
        assert "images_count" in data
        assert "rated_images_count" in data

