"""
Keyword extraction and analysis utilities.
"""

import re
from typing import List, Dict, Any
from collections import Counter

class KeywordExtractor:
    """Extract and analyze keywords from prompts."""
    
    def __init__(self):
        # Keyword categories for classification
        self.categories = {
            "structural": ["grid", "radial", "fractal", "voronoi", "maze", "tessellated", "lattice"],
            "organic": ["cellular", "flowing", "growth", "branching", "veins", "natural", "biological"],
            "textural": ["rough", "smooth", "grainy", "sharp", "soft", "coarse", "fine", "gritty"],
            "map_like": ["topographic", "contour", "terrain", "elevation", "isoline", "cartographic"],
            "geometric": ["angular", "curved", "symmetrical", "tessellated", "polygonal", "circular"],
            "visual": ["bold", "subtle", "delicate", "strong", "gentle", "dramatic", "minimalist"]
        }
    
    def extract_keywords(self, prompt: str) -> List[str]:
        """
        Extract ##keywords from a prompt.
        
        Args:
            prompt: The prompt text to analyze
            
        Returns:
            List of keywords found in the prompt
        """
        keyword_pattern = r'##(\w+)'
        keywords = re.findall(keyword_pattern, prompt)
        return keywords
    
    def extract_all_keywords(self, prompt: str) -> Dict[str, List[str]]:
        """
        Extract both ##keywords and regular descriptive words.
        
        Args:
            prompt: The prompt text to analyze
            
        Returns:
            Dictionary with 'tagged' and 'descriptive' keywords
        """
        # Extract ##keywords
        tagged_keywords = self.extract_keywords(prompt)
        
        # Extract descriptive words (simple approach)
        words = re.findall(r'\b\w+\b', prompt.lower())
        descriptive_words = [word for word in words if len(word) > 3 and word not in ['with', 'and', 'the', 'for', 'are', 'this', 'that']]
        
        return {
            "tagged": tagged_keywords,
            "descriptive": descriptive_words
        }
    
    def categorize_keywords(self, keywords: List[str]) -> Dict[str, List[str]]:
        """
        Categorize keywords by type.
        
        Args:
            keywords: List of keywords to categorize
            
        Returns:
            Dictionary mapping categories to lists of keywords
        """
        categorized = {category: [] for category in self.categories.keys()}
        uncategorized = []
        
        for keyword in keywords:
            categorized_flag = False
            for category, category_keywords in self.categories.items():
                if keyword.lower() in category_keywords:
                    categorized[category].append(keyword)
                    categorized_flag = True
                    break
            
            if not categorized_flag:
                uncategorized.append(keyword)
        
        if uncategorized:
            categorized["uncategorized"] = uncategorized
        
        return categorized
    
    def analyze_keyword_effectiveness(
        self, 
        keyword_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze keyword effectiveness based on ratings.
        
        Args:
            keyword_data: List of dictionaries with 'keywords' and 'rating' keys
            
        Returns:
            Dictionary with keyword effectiveness analysis
        """
        keyword_ratings = {}
        keyword_counts = Counter()
        
        for data in keyword_data:
            keywords = data.get('keywords', [])
            rating = data.get('rating', 0)
            
            for keyword in keywords:
                if keyword not in keyword_ratings:
                    keyword_ratings[keyword] = []
                keyword_ratings[keyword].append(rating)
                keyword_counts[keyword] += 1
        
        # Calculate effectiveness metrics
        effectiveness = {}
        for keyword, ratings in keyword_ratings.items():
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                high_rated_count = sum(1 for r in ratings if r >= 4)
                success_rate = high_rated_count / len(ratings) if ratings else 0
                
                effectiveness[keyword] = {
                    "average_rating": round(avg_rating, 2),
                    "total_uses": len(ratings),
                    "high_rated_count": high_rated_count,
                    "success_rate": round(success_rate, 2),
                    "category": self._get_keyword_category(keyword)
                }
        
        return effectiveness
    
    def suggest_keywords(
        self, 
        current_keywords: List[str], 
        effectiveness_data: Dict[str, Any],
        num_suggestions: int = 3
    ) -> List[str]:
        """
        Suggest new keywords based on effectiveness data.
        
        Args:
            current_keywords: Current keywords in the prompt
            effectiveness_data: Keyword effectiveness analysis
            num_suggestions: Number of suggestions to return
            
        Returns:
            List of suggested keywords
        """
        # Get high-performing keywords not currently used
        available_keywords = []
        for keyword, data in effectiveness_data.items():
            if keyword not in current_keywords and data.get('success_rate', 0) > 0.5:
                available_keywords.append((keyword, data['success_rate']))
        
        # Sort by success rate
        available_keywords.sort(key=lambda x: x[1], reverse=True)
        
        # Return top suggestions
        suggestions = [kw[0] for kw in available_keywords[:num_suggestions]]
        
        # If not enough high-performing keywords, suggest from categories
        if len(suggestions) < num_suggestions:
            current_categories = set()
            for kw in current_keywords:
                category = self._get_keyword_category(kw)
                if category:
                    current_categories.add(category)
            
            # Suggest from underrepresented categories
            for category, keywords in self.categories.items():
                if category not in current_categories:
                    for keyword in keywords:
                        if keyword not in current_keywords and keyword not in suggestions:
                            suggestions.append(keyword)
                            if len(suggestions) >= num_suggestions:
                                break
                    if len(suggestions) >= num_suggestions:
                        break
        
        return suggestions[:num_suggestions]
    
    def _get_keyword_category(self, keyword: str) -> str:
        """Get the category for a keyword."""
        keyword_lower = keyword.lower()
        for category, keywords in self.categories.items():
            if keyword_lower in keywords:
                return category
        return "uncategorized"
