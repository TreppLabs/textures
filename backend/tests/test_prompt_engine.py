"""
Unit tests for PromptEngine.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from core.prompt_engine import PromptEngine


class TestPromptEngine:
    """Test cases for PromptEngine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = PromptEngine()
    
    def test_generate_variations_basic(self):
        """Test generating basic prompt variations."""
        base_prompt = "organic structure with ##fractal patterns"
        variations = self.engine.generate_variations(base_prompt, num_variations=4)
        
        assert len(variations) == 4
        for variation in variations:
            assert "prompt" in variation
            assert "strategy" in variation
            assert isinstance(variation["prompt"], str)
            assert len(variation["prompt"]) > 0
    
    def test_generate_variations_with_history(self):
        """Test generating variations with theme history."""
        base_prompt = "organic structure"
        theme_history = [
            {"prompt": "organic with ##fractal", "rating": 5},
            {"prompt": "organic with ##flowing", "rating": 4},
            {"prompt": "organic with ##grid", "rating": 2},
        ]
        
        variations = self.engine.generate_variations(
            base_prompt, 
            num_variations=4,
            theme_history=theme_history
        )
        
        assert len(variations) == 4
        # Should prefer successful patterns
        strategies = [v["strategy"] for v in variations]
        assert "keyword_combination" in strategies or "keyword_substitution" in strategies
    
    def test_keyword_substitution(self):
        """Test keyword substitution strategy."""
        prompt = "organic structure with ##fractal patterns"
        keywords = ["fractal"]
        variation = self.engine._keyword_substitution(prompt, keywords, 0)
        
        assert "prompt" in variation
        assert "strategy" in variation
        assert variation["strategy"] == "keyword_substitution"
        # May or may not have changes depending on category availability
        assert "changes" in variation
    
    def test_descriptor_addition(self):
        """Test descriptor addition strategy."""
        prompt = "organic structure"
        variation = self.engine._descriptor_addition(prompt, 0)
        
        assert "prompt" in variation
        assert "strategy" in variation
        assert variation["strategy"] == "descriptor_addition"
        assert len(variation["prompt"]) > len(prompt)
        assert "changes" in variation
    
    def test_emphasis_shifting(self):
        """Test emphasis shifting strategy."""
        prompt = "organic structure"
        variation = self.engine._emphasis_shifting(prompt, 0)
        
        assert "prompt" in variation
        assert "strategy" in variation
        assert variation["strategy"] == "emphasis_shifting"
        assert len(variation["prompt"]) > len(prompt)
    
    def test_keyword_combination(self):
        """Test keyword combination strategy."""
        prompt = "organic structure"
        patterns = {
            "successful_keywords": {
                "fractal": 3,
                "flowing": 2,
            }
        }
        variation = self.engine._keyword_combination(prompt, patterns, 0)
        
        assert "prompt" in variation
        assert "strategy" in variation
        assert variation["strategy"] == "keyword_combination"
        # Should include a successful keyword
        assert "fractal" in variation["prompt"] or "flowing" in variation["prompt"]
    
    def test_keyword_combination_no_patterns(self):
        """Test keyword combination with no successful patterns."""
        prompt = "organic structure"
        patterns = {}
        variation = self.engine._keyword_combination(prompt, patterns, 0)
        
        # Should fall back to descriptor addition
        assert "prompt" in variation
        assert variation["strategy"] in ["descriptor_addition", "keyword_combination"]
    
    def test_parameter_tweaking(self):
        """Test parameter tweaking strategy."""
        prompt = "organic structure"
        variation = self.engine._parameter_tweaking(prompt, 0)
        
        assert "prompt" in variation
        assert "strategy" in variation
        assert variation["strategy"] == "parameter_tweaking"
        assert len(variation["prompt"]) > len(prompt)
    
    def test_analyze_successful_patterns(self):
        """Test analyzing successful patterns from history."""
        theme_history = [
            {"prompt": "organic with ##fractal", "rating": 5},
            {"prompt": "organic with ##flowing", "rating": 4},
            {"prompt": "organic with ##grid", "rating": 2},
        ]
        
        patterns = self.engine._analyze_successful_patterns(theme_history)
        
        assert "successful_keywords" in patterns
        assert "high_rated_count" in patterns
        assert patterns["high_rated_count"] == 2  # Ratings >= 4
        assert "fractal" in patterns["successful_keywords"]
        assert "flowing" in patterns["successful_keywords"]
    
    def test_analyze_successful_patterns_empty(self):
        """Test analyzing patterns with empty history."""
        patterns = self.engine._analyze_successful_patterns([])
        assert patterns == {}
    
    def test_analyze_successful_patterns_no_high_rated(self):
        """Test analyzing patterns with no high-rated images."""
        theme_history = [
            {"prompt": "organic with ##grid", "rating": 2},
            {"prompt": "organic with ##angular", "rating": 1},
        ]
        
        patterns = self.engine._analyze_successful_patterns(theme_history)
        assert patterns == {}
    
    def test_find_keyword_category(self):
        """Test finding keyword category."""
        assert self.engine._find_keyword_category("fractal") == "structural"
        assert self.engine._find_keyword_category("flowing") == "organic"
        assert self.engine._find_keyword_category("unknown") is None

