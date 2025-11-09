"""
Prompt engineering and variation generation.
"""

import random
import json
from typing import List, Dict, Any
from .keyword_extractor import KeywordExtractor
from .rating_analyzer import RatingAnalyzer

class PromptEngine:
    """Engine for generating and evolving prompts based on ratings."""
    
    def __init__(self):
        self.keyword_extractor = KeywordExtractor()
        self.rating_analyzer = RatingAnalyzer()
        
        # Keyword categories for variation
        self.keyword_categories = {
            "structural": ["grid", "radial", "fractal", "voronoi", "maze", "tessellated"],
            "organic": ["cellular", "flowing", "growth", "branching", "veins", "natural"],
            "textural": ["rough", "smooth", "grainy", "sharp", "soft", "coarse"],
            "map_like": ["topographic", "contour", "terrain", "elevation", "isoline"],
            "geometric": ["angular", "curved", "symmetrical", "tessellated", "polygonal"]
        }
        
        # Variation strategies
        self.variation_strategies = [
            "keyword_substitution",
            "descriptor_addition", 
            "emphasis_shifting",
            "keyword_combination",
            "parameter_tweaking"
        ]
    
    def generate_variations(
        self, 
        base_prompt: str, 
        num_variations: int = 4,
        theme_history: List[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate prompt variations based on base prompt and theme history.
        
        Args:
            base_prompt: The base prompt to vary
            num_variations: Number of variations to generate
            theme_history: Previous generations and ratings for this theme
            
        Returns:
            List of variation dictionaries with prompts and metadata
        """
        variations = []
        
        # Extract current keywords
        current_keywords = self.keyword_extractor.extract_keywords(base_prompt)
        
        # Analyze successful patterns from history
        successful_patterns = self._analyze_successful_patterns(theme_history)
        
        for i in range(num_variations):
            strategy = self._select_variation_strategy(i, successful_patterns)
            variation = self._apply_variation_strategy(
                base_prompt, 
                strategy, 
                current_keywords, 
                successful_patterns,
                i
            )
            variations.append(variation)
        
        return variations
    
    def _analyze_successful_patterns(self, theme_history: List[Dict]) -> Dict[str, Any]:
        """Analyze successful patterns from theme history."""
        if not theme_history:
            return {}
        
        high_rated_images = [img for img in theme_history if img.get('rating', 0) >= 4]
        
        if not high_rated_images:
            return {}
        
        # Extract common keywords from high-rated images
        successful_keywords = []
        for img in high_rated_images:
            keywords = self.keyword_extractor.extract_keywords(img.get('prompt', ''))
            successful_keywords.extend(keywords)
        
        # Count keyword frequency
        keyword_counts = {}
        for keyword in successful_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        return {
            "successful_keywords": keyword_counts,
            "high_rated_count": len(high_rated_images),
            "total_count": len(theme_history)
        }
    
    def _select_variation_strategy(self, index: int, patterns: Dict) -> str:
        """Select variation strategy based on index and patterns."""
        if patterns.get("high_rated_count", 0) > 0:
            # If we have successful patterns, use them more often
            if index % 3 == 0:
                return "keyword_combination"
            elif index % 3 == 1:
                return "keyword_substitution"
            else:
                return random.choice(self.variation_strategies)
        else:
            # Random strategy for new themes
            return random.choice(self.variation_strategies)
    
    def _apply_variation_strategy(
        self, 
        base_prompt: str, 
        strategy: str, 
        current_keywords: List[str],
        patterns: Dict,
        index: int
    ) -> Dict[str, Any]:
        """Apply a specific variation strategy to the base prompt."""
        
        if strategy == "keyword_substitution":
            return self._keyword_substitution(base_prompt, current_keywords, index)
        elif strategy == "descriptor_addition":
            return self._descriptor_addition(base_prompt, index)
        elif strategy == "emphasis_shifting":
            return self._emphasis_shifting(base_prompt, index)
        elif strategy == "keyword_combination":
            return self._keyword_combination(base_prompt, patterns, index)
        elif strategy == "parameter_tweaking":
            return self._parameter_tweaking(base_prompt, index)
        else:
            return self._descriptor_addition(base_prompt, index)
    
    def _keyword_substitution(self, prompt: str, keywords: List[str], index: int) -> Dict[str, Any]:
        """Replace keywords with similar ones from the same category."""
        if not keywords:
            return {"prompt": prompt, "strategy": "keyword_substitution", "changes": []}
        
        # Find replacement keywords
        new_prompt = prompt
        changes = []
        
        for keyword in keywords[:2]:  # Limit to first 2 keywords
            category = self._find_keyword_category(keyword)
            if category and len(self.keyword_categories[category]) > 1:
                # Find a different keyword from the same category
                alternatives = [k for k in self.keyword_categories[category] if k != keyword]
                if alternatives:
                    replacement = random.choice(alternatives)
                    new_prompt = new_prompt.replace(f"##{keyword}", f"##{replacement}")
                    changes.append(f"##{keyword} → ##{replacement}")
        
        return {
            "prompt": new_prompt,
            "strategy": "keyword_substitution",
            "changes": changes
        }
    
    def _descriptor_addition(self, prompt: str, index: int) -> Dict[str, Any]:
        """Add complementary descriptors to the prompt."""
        descriptors = [
            "with flowing lines",
            "with subtle texture",
            "with organic growth",
            "with geometric precision",
            "with natural randomness",
            "with structured chaos"
        ]
        
        descriptor = descriptors[index % len(descriptors)]
        new_prompt = f"{prompt}, {descriptor}"
        
        return {
            "prompt": new_prompt,
            "strategy": "descriptor_addition",
            "changes": [f"Added: {descriptor}"]
        }
    
    def _emphasis_shifting(self, prompt: str, index: int) -> Dict[str, Any]:
        """Shift emphasis between different elements."""
        # Simple implementation - could be more sophisticated
        emphasis_modifiers = [
            "bold", "subtle", "delicate", "strong", "gentle", "dramatic"
        ]
        
        modifier = emphasis_modifiers[index % len(emphasis_modifiers)]
        new_prompt = f"{modifier} {prompt}"
        
        return {
            "prompt": new_prompt,
            "strategy": "emphasis_shifting",
            "changes": [f"Added emphasis: {modifier}"]
        }
    
    def _keyword_combination(self, prompt: str, patterns: Dict, index: int) -> Dict[str, Any]:
        """Combine successful keywords from patterns."""
        successful_keywords = patterns.get("successful_keywords", {})
        if not successful_keywords:
            return self._descriptor_addition(prompt, index)
        
        # Get top keywords
        top_keywords = sorted(successful_keywords.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Add a successful keyword
        if top_keywords:
            keyword = top_keywords[index % len(top_keywords)][0]
            new_prompt = f"{prompt}, ##{keyword}"
            
            return {
                "prompt": new_prompt,
                "strategy": "keyword_combination",
                "changes": [f"Added successful keyword: ##{keyword}"]
            }
        
        return self._descriptor_addition(prompt, index)
    
    def _parameter_tweaking(self, prompt: str, index: int) -> Dict[str, Any]:
        """Add parameter-like descriptors."""
        parameters = [
            "high contrast",
            "low contrast", 
            "fine detail",
            "coarse texture",
            "smooth transitions",
            "sharp edges"
        ]
        
        parameter = parameters[index % len(parameters)]
        new_prompt = f"{prompt}, {parameter}"
        
        return {
            "prompt": new_prompt,
            "strategy": "parameter_tweaking",
            "changes": [f"Added parameter: {parameter}"]
        }
    
    def _find_keyword_category(self, keyword: str) -> str:
        """Find which category a keyword belongs to."""
        for category, keywords in self.keyword_categories.items():
            if keyword in keywords:
                return category
        return None
