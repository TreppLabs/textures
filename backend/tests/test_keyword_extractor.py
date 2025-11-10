"""
Unit tests for KeywordExtractor.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from core.keyword_extractor import KeywordExtractor


class TestKeywordExtractor:
    """Test cases for KeywordExtractor."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = KeywordExtractor()
    
    def test_extract_keywords_simple(self):
        """Test extracting simple keywords."""
        prompt = "organic structure with ##fractal patterns and ##flowing lines"
        keywords = self.extractor.extract_keywords(prompt)
        
        assert "fractal" in keywords
        assert "flowing" in keywords
        assert len(keywords) == 2
    
    def test_extract_keywords_none(self):
        """Test extracting keywords from prompt with no keywords."""
        prompt = "organic structure with flowing lines"
        keywords = self.extractor.extract_keywords(prompt)
        
        assert keywords == []
    
    def test_extract_keywords_multiple(self):
        """Test extracting multiple keywords."""
        prompt = "##cellular ##fractal ##voronoi structure with ##flowing lines"
        keywords = self.extractor.extract_keywords(prompt)
        
        assert len(keywords) == 4
        assert "cellular" in keywords
        assert "fractal" in keywords
        assert "voronoi" in keywords
        assert "flowing" in keywords
    
    def test_extract_all_keywords(self):
        """Test extracting both tagged and descriptive keywords."""
        prompt = "organic ##fractal structure with flowing lines"
        result = self.extractor.extract_all_keywords(prompt)
        
        assert "tagged" in result
        assert "descriptive" in result
        assert "fractal" in result["tagged"]
        assert "organic" in result["descriptive"] or "structure" in result["descriptive"]
    
    def test_categorize_keywords(self):
        """Test categorizing keywords."""
        keywords = ["fractal", "flowing", "cellular", "grid", "unknown_keyword"]
        categorized = self.extractor.categorize_keywords(keywords)
        
        assert "structural" in categorized
        assert "organic" in categorized
        assert "uncategorized" in categorized
        assert "fractal" in categorized["structural"]
        assert "flowing" in categorized["organic"]
        assert "cellular" in categorized["organic"]
        assert "grid" in categorized["structural"]
        assert "unknown_keyword" in categorized["uncategorized"]
    
    def test_analyze_keyword_effectiveness(self):
        """Test analyzing keyword effectiveness based on ratings."""
        keyword_data = [
            {"keywords": ["fractal", "organic"], "rating": 5},
            {"keywords": ["fractal", "flowing"], "rating": 4},
            {"keywords": ["grid", "geometric"], "rating": 2},
            {"keywords": ["fractal"], "rating": 5},
            {"keywords": ["grid"], "rating": 1},
        ]
        
        effectiveness = self.extractor.analyze_keyword_effectiveness(keyword_data)
        
        assert "fractal" in effectiveness
        assert "grid" in effectiveness
        assert effectiveness["fractal"]["average_rating"] > effectiveness["grid"]["average_rating"]
        assert effectiveness["fractal"]["success_rate"] > effectiveness["grid"]["success_rate"]
    
    def test_analyze_keyword_effectiveness_empty(self):
        """Test analyzing keyword effectiveness with empty data."""
        effectiveness = self.extractor.analyze_keyword_effectiveness([])
        assert effectiveness == {}
    
    def test_suggest_keywords(self):
        """Test suggesting keywords based on effectiveness."""
        current_keywords = ["fractal"]
        effectiveness_data = {
            "fractal": {"success_rate": 0.8, "average_rating": 4.5},
            "flowing": {"success_rate": 0.7, "average_rating": 4.2},
            "cellular": {"success_rate": 0.6, "average_rating": 4.0},
            "grid": {"success_rate": 0.2, "average_rating": 2.0},
        }
        
        suggestions = self.extractor.suggest_keywords(
            current_keywords, 
            effectiveness_data, 
            num_suggestions=2
        )
        
        assert len(suggestions) <= 2
        assert "flowing" in suggestions or "cellular" in suggestions
        assert "grid" not in suggestions  # Low success rate
    
    def test_get_keyword_category(self):
        """Test getting keyword category."""
        assert self.extractor._get_keyword_category("fractal") == "structural"
        assert self.extractor._get_keyword_category("flowing") == "organic"
        assert self.extractor._get_keyword_category("unknown") == "uncategorized"

