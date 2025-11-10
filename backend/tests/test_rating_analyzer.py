"""
Unit tests for RatingAnalyzer.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from core.rating_analyzer import RatingAnalyzer


class TestRatingAnalyzer:
    """Test cases for RatingAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = RatingAnalyzer()
    
    def test_analyze_theme_performance_basic(self):
        """Test basic theme performance analysis."""
        theme_data = [
            {"rating": 5, "prompt": "test1"},
            {"rating": 4, "prompt": "test2"},
            {"rating": 3, "prompt": "test3"},
            {"rating": 5, "prompt": "test4"},
            {"rating": 2, "prompt": "test5"},
        ]
        
        result = self.analyzer.analyze_theme_performance(theme_data)
        
        assert "average_rating" in result
        assert "median_rating" in result
        assert "success_rate" in result
        assert "high_rated_count" in result
        assert result["total_images"] == 5
        assert result["rated_images"] == 5
        assert result["average_rating"] == pytest.approx(3.8, abs=0.1)
        assert result["high_rated_count"] == 3  # Ratings >= 4
    
    def test_analyze_theme_performance_no_ratings(self):
        """Test theme performance with no ratings."""
        theme_data = [
            {"prompt": "test1"},
            {"prompt": "test2"},
        ]
        
        result = self.analyzer.analyze_theme_performance(theme_data)
        assert "error" in result
        assert result["error"] == "No ratings found"
    
    def test_analyze_theme_performance_empty(self):
        """Test theme performance with empty data."""
        result = self.analyzer.analyze_theme_performance([])
        assert "error" in result
    
    def test_analyze_keyword_effectiveness(self):
        """Test keyword effectiveness analysis."""
        image_data = [
            {"keywords": ["fractal", "organic"], "rating": 5},
            {"keywords": ["fractal", "flowing"], "rating": 4},
            {"keywords": ["grid", "geometric"], "rating": 2},
            {"keywords": ["fractal"], "rating": 5},
            {"keywords": ["grid"], "rating": 1},
            {"keywords": ["flowing"], "rating": 4},
            {"keywords": ["grid", "angular"], "rating": 2},  # Add one more grid to meet min_samples
        ]
        
        result = self.analyzer.analyze_keyword_effectiveness(image_data)
        
        assert "keyword_effectiveness" in result
        assert "top_performers" in result
        assert "underperformers" in result
        assert "fractal" in result["keyword_effectiveness"]
        # Grid should be in results if it has >= 3 samples
        if "grid" in result["keyword_effectiveness"]:
            # Fractal should have higher success rate than grid
            fractal_data = result["keyword_effectiveness"]["fractal"]
            grid_data = result["keyword_effectiveness"]["grid"]
            assert fractal_data["success_rate"] > grid_data["success_rate"]
    
    def test_analyze_keyword_effectiveness_insufficient_samples(self):
        """Test keyword effectiveness with insufficient samples."""
        image_data = [
            {"keywords": ["fractal"], "rating": 5},
            {"keywords": ["grid"], "rating": 2},
        ]
        
        result = self.analyzer.analyze_keyword_effectiveness(image_data)
        
        # Should not include keywords with < 3 samples
        assert "keyword_effectiveness" in result
        # May be empty if no keyword has enough samples
    
    def test_suggest_prompt_improvements(self):
        """Test prompt improvement suggestions."""
        current_prompt = "organic structure with ##grid patterns"
        theme_data = [
            {"prompt": "organic with ##fractal", "rating": 5},
            {"prompt": "organic with ##flowing", "rating": 4},
            {"prompt": "organic with ##grid", "rating": 2},
        ]
        
        keyword_effectiveness = {
            "keyword_effectiveness": {
                "fractal": {"success_rate": 0.8, "average_rating": 4.5},
                "flowing": {"success_rate": 0.7, "average_rating": 4.2},
                "grid": {"success_rate": 0.2, "average_rating": 2.0},
            },
            "top_performers": ["fractal", "flowing"],
            "underperformers": ["grid"],
            "analysis_quality": "medium"
        }
        
        suggestions = self.analyzer.suggest_prompt_improvements(
            current_prompt,
            theme_data,
            keyword_effectiveness
        )
        
        assert "add_keywords" in suggestions
        assert "remove_keywords" in suggestions
        assert "modify_approach" in suggestions
        assert "confidence" in suggestions
        
        # Should suggest adding fractal or flowing
        add_keywords = [kw["keyword"] for kw in suggestions["add_keywords"]]
        assert "fractal" in add_keywords or "flowing" in add_keywords
        
        # Should suggest removing grid
        remove_keywords = [kw["keyword"] for kw in suggestions["remove_keywords"]]
        assert "grid" in remove_keywords
    
    def test_get_performance_level(self):
        """Test performance level calculation."""
        assert self.analyzer._get_performance_level(0.8, 4.5) == "excellent"
        assert self.analyzer._get_performance_level(0.6, 3.8) == "good"
        assert self.analyzer._get_performance_level(0.4, 3.2) == "fair"
        assert self.analyzer._get_performance_level(0.2, 2.5) == "poor"
    
    def test_calculate_confidence(self):
        """Test confidence calculation."""
        assert self.analyzer._calculate_confidence(15, 0.8) == "high"
        assert self.analyzer._calculate_confidence(7, 0.6) == "medium"
        assert self.analyzer._calculate_confidence(3, 0.4) == "low"
    
    def test_analyze_rating_trend(self):
        """Test rating trend analysis."""
        theme_data = [
            {"rating": 2, "created_at": "2024-01-01T00:00:00"},
            {"rating": 3, "created_at": "2024-01-02T00:00:00"},
            {"rating": 4, "created_at": "2024-01-03T00:00:00"},
            {"rating": 4, "created_at": "2024-01-04T00:00:00"},
            {"rating": 5, "created_at": "2024-01-05T00:00:00"},
        ]
        
        trend = self.analyzer._analyze_rating_trend(theme_data)
        assert trend in ["improving", "stable", "declining"]
    
    def test_analyze_rating_trend_insufficient_data(self):
        """Test rating trend with insufficient data."""
        theme_data = [
            {"rating": 3, "created_at": "2024-01-01T00:00:00"},
            {"rating": 4, "created_at": "2024-01-02T00:00:00"},
        ]
        
        trend = self.analyzer._analyze_rating_trend(theme_data)
        assert trend == "insufficient_data"

