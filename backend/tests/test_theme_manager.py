"""
Unit tests for ThemeManager.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from models.schemas import Theme, Generation, Image


class TestThemeManager:
    """Test cases for ThemeManager."""
    
    def test_create_theme(self, theme_manager, sample_theme_data):
        """Test creating a theme."""
        theme = theme_manager.create_theme(
            name=sample_theme_data["name"],
            base_prompt=sample_theme_data["base_prompt"],
            description=sample_theme_data["description"]
        )
        
        assert "error" not in theme
        assert theme["name"] == sample_theme_data["name"]
        assert theme["base_prompt"] == sample_theme_data["base_prompt"]
        assert "id" in theme
        assert theme["id"] > 0
    
    def test_get_theme(self, theme_manager, sample_theme_data):
        """Test getting a theme by ID."""
        # Create a theme first
        created = theme_manager.create_theme(
            name=sample_theme_data["name"],
            base_prompt=sample_theme_data["base_prompt"],
            description=sample_theme_data["description"]
        )
        theme_id = created["id"]
        
        # Get the theme
        theme = theme_manager.get_theme(theme_id)
        
        assert "error" not in theme
        assert theme["id"] == theme_id
        assert theme["name"] == sample_theme_data["name"]
    
    def test_get_theme_not_found(self, theme_manager):
        """Test getting a non-existent theme."""
        theme = theme_manager.get_theme(99999)
        assert "error" in theme
        assert theme["error"] == "Theme not found"
    
    def test_list_themes(self, theme_manager, sample_theme_data):
        """Test listing all themes."""
        # Create a few themes
        theme_manager.create_theme(
            name="Theme 1",
            base_prompt="prompt 1",
            description="Description 1"
        )
        theme_manager.create_theme(
            name="Theme 2",
            base_prompt="prompt 2",
            description="Description 2"
        )
        
        themes = theme_manager.list_themes()
        
        assert len(themes) >= 2
        assert all("id" in theme for theme in themes)
        assert all("name" in theme for theme in themes)
    
    def test_branch_theme(self, theme_manager, sample_theme_data):
        """Test branching a theme."""
        # Create parent theme
        parent = theme_manager.create_theme(
            name="Parent Theme",
            base_prompt="parent prompt",
            description="Parent description"
        )
        parent_id = parent["id"]
        
        # Branch the theme
        branch = theme_manager.branch_theme(
            parent_theme_id=parent_id,
            new_name="Branched Theme",
            new_base_prompt="branched prompt"
        )
        
        assert "error" not in branch
        assert branch["name"] == "Branched Theme"
        assert branch["parent_theme_id"] == parent_id
        assert branch["base_prompt"] == "branched prompt"
    
    def test_branch_theme_uses_parent_prompt(self, theme_manager):
        """Test that branching without prompt uses parent's prompt."""
        # Create parent theme
        parent = theme_manager.create_theme(
            name="Parent Theme",
            base_prompt="parent prompt",
            description="Parent description"
        )
        parent_id = parent["id"]
        
        # Branch without providing new prompt
        branch = theme_manager.branch_theme(
            parent_theme_id=parent_id,
            new_name="Branched Theme"
        )
        
        assert "error" not in branch
        assert branch["base_prompt"] == "parent prompt"
    
    def test_branch_theme_parent_not_found(self, theme_manager):
        """Test branching from non-existent parent."""
        branch = theme_manager.branch_theme(
            parent_theme_id=99999,
            new_name="Branched Theme"
        )
        
        assert "error" in branch
        assert "not found" in branch["error"].lower()
    
    def test_update_theme(self, theme_manager, sample_theme_data):
        """Test updating a theme."""
        # Create a theme
        created = theme_manager.create_theme(
            name=sample_theme_data["name"],
            base_prompt=sample_theme_data["base_prompt"],
            description=sample_theme_data["description"]
        )
        theme_id = created["id"]
        
        # Update the theme
        updated = theme_manager.update_theme(
            theme_id=theme_id,
            name="Updated Name",
            base_prompt="Updated prompt"
        )
        
        assert "error" not in updated
        assert updated["name"] == "Updated Name"
        assert updated["base_prompt"] == "Updated prompt"
    
    def test_update_theme_not_found(self, theme_manager):
        """Test updating a non-existent theme."""
        updated = theme_manager.update_theme(
            theme_id=99999,
            name="Updated Name"
        )
        
        assert "error" in updated
        assert "not found" in updated["error"].lower()
    
    def test_get_theme_statistics(self, theme_manager):
        """Test getting theme statistics."""
        # Create theme
        theme = theme_manager.create_theme(
            name="Test Theme",
            base_prompt="test prompt"
        )
        theme_id = theme["id"]
        
        # Get statistics
        stats = theme_manager.get_theme_statistics(theme_id)
        
        assert "error" not in stats
        assert stats["theme_id"] == theme_id
        assert "generations_count" in stats
        assert "images_count" in stats
        assert "rated_images_count" in stats
        assert "average_rating" in stats
        assert "completion_rate" in stats

