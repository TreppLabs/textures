"""
Rating analysis and pattern recognition for prompt improvement.
"""

from typing import List, Dict, Any
from collections import Counter, defaultdict
import statistics
from core.constants import (
    HIGH_RATING_THRESHOLD,
    MIN_SAMPLES_FOR_ANALYSIS,
    MIN_DATA_SIZE_FOR_HIGH_CONFIDENCE,
    MIN_DATA_SIZE_FOR_MEDIUM_CONFIDENCE,
    HIGH_SUCCESS_RATE_THRESHOLD,
    MEDIUM_SUCCESS_RATE_THRESHOLD,
    EXCELLENT_SUCCESS_RATE,
    EXCELLENT_AVG_RATING,
    GOOD_SUCCESS_RATE,
    GOOD_AVG_RATING,
    FAIR_SUCCESS_RATE,
    FAIR_AVG_RATING,
)

class RatingAnalyzer:
    """Analyze ratings to identify successful patterns and suggest improvements."""
    
    def __init__(self):
        self.min_rating_for_success = HIGH_RATING_THRESHOLD
        self.min_samples_for_analysis = MIN_SAMPLES_FOR_ANALYSIS
    
    def analyze_theme_performance(self, theme_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze overall performance of a theme.
        
        Args:
            theme_data: List of image data with ratings and prompts
            
        Returns:
            Dictionary with performance analysis
        """
        if not theme_data:
            return {"error": "No data provided"}
        
        ratings = [item.get('rating', 0) for item in theme_data if item.get('rating') is not None]
        
        if not ratings:
            return {"error": "No ratings found"}
        
        # Basic statistics
        avg_rating = statistics.mean(ratings)
        median_rating = statistics.median(ratings)
        high_rated_count = sum(1 for r in ratings if r >= HIGH_RATING_THRESHOLD)
        success_rate = high_rated_count / len(ratings)
        
        # Rating distribution
        rating_distribution = Counter(ratings)
        
        # Trend analysis (if we have enough data)
        trend = self._analyze_rating_trend(theme_data)
        
        return {
            "total_images": len(theme_data),
            "rated_images": len(ratings),
            "average_rating": round(avg_rating, 2),
            "median_rating": median_rating,
            "high_rated_count": high_rated_count,
            "success_rate": round(success_rate, 2),
            "rating_distribution": dict(rating_distribution),
            "trend": trend,
            "performance_level": self._get_performance_level(success_rate, avg_rating)
        }
    
    def analyze_keyword_effectiveness(
        self, 
        image_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze which keywords correlate with high ratings.
        
        Args:
            image_data: List of image data with keywords and ratings
            
        Returns:
            Dictionary with keyword effectiveness analysis
        """
        keyword_stats = defaultdict(list)
        
        # Collect keyword-rating pairs
        for item in image_data:
            keywords = item.get('keywords', [])
            rating = item.get('rating')
            
            if rating is not None:
                for keyword in keywords:
                    keyword_stats[keyword].append(rating)
        
        # Calculate effectiveness for each keyword
        effectiveness = {}
        for keyword, ratings in keyword_stats.items():
            if len(ratings) >= MIN_SAMPLES_FOR_ANALYSIS:
                avg_rating = statistics.mean(ratings)
                high_rated_count = sum(1 for r in ratings if r >= HIGH_RATING_THRESHOLD)
                success_rate = high_rated_count / len(ratings)
                
                effectiveness[keyword] = {
                    "total_uses": len(ratings),
                    "average_rating": round(avg_rating, 2),
                    "high_rated_count": high_rated_count,
                    "success_rate": round(success_rate, 2),
                    "confidence": self._calculate_confidence(len(ratings), success_rate)
                }
        
        # Sort by effectiveness
        sorted_keywords = sorted(
            effectiveness.items(), 
            key=lambda x: (x[1]['success_rate'], x[1]['average_rating']), 
            reverse=True
        )
        
        return {
            "keyword_effectiveness": dict(sorted_keywords),
            "top_performers": [kw for kw, data in sorted_keywords[:5] if data['success_rate'] > 0.5],
            "underperformers": [kw for kw, data in sorted_keywords if data['success_rate'] < 0.3],
            "analysis_quality": self._assess_analysis_quality(effectiveness)
        }
    
    def suggest_prompt_improvements(
        self, 
        current_prompt: str, 
        theme_data: List[Dict[str, Any]],
        keyword_effectiveness: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Suggest improvements to the current prompt based on analysis.
        
        Args:
            current_prompt: The current prompt to improve
            theme_data: Historical data for the theme
            keyword_effectiveness: Keyword effectiveness analysis
            
        Returns:
            Dictionary with improvement suggestions
        """
        suggestions = {
            "add_keywords": [],
            "remove_keywords": [],
            "modify_approach": [],
            "confidence": "low"
        }
        
        # Extract current keywords
        current_keywords = self._extract_keywords_from_prompt(current_prompt)
        
        # Suggest adding high-performing keywords
        top_performers = keyword_effectiveness.get('top_performers', [])
        for keyword in top_performers:
            if keyword not in current_keywords:
                suggestions["add_keywords"].append({
                    "keyword": keyword,
                    "reason": "High success rate in theme history"
                })
        
        # Suggest removing underperforming keywords
        underperformers = keyword_effectiveness.get('underperformers', [])
        for keyword in underperformers:
            if keyword in current_keywords:
                suggestions["remove_keywords"].append({
                    "keyword": keyword,
                    "reason": "Low success rate in theme history"
                })
        
        # Suggest approach modifications based on theme performance
        theme_performance = self.analyze_theme_performance(theme_data)
        performance_level = theme_performance.get('performance_level', 'unknown')
        
        if performance_level == 'poor':
            suggestions["modify_approach"].append({
                "suggestion": "Consider more dramatic changes to prompt structure",
                "reason": "Theme has low success rate"
            })
        elif performance_level == 'good':
            suggestions["modify_approach"].append({
                "suggestion": "Fine-tune existing successful patterns",
                "reason": "Theme is performing well, refine rather than overhaul"
            })
        
        # Set confidence level
        suggestions["confidence"] = self._assess_suggestion_confidence(
            len(theme_data), 
            keyword_effectiveness.get('analysis_quality', 'low')
        )
        
        return suggestions
    
    def _analyze_rating_trend(self, theme_data: List[Dict[str, Any]]) -> str:
        """Analyze if ratings are improving over time."""
        if len(theme_data) < 5:
            return "insufficient_data"
        
        # Sort by creation time (assuming data is in order)
        sorted_data = sorted(theme_data, key=lambda x: x.get('created_at', ''))
        ratings = [item.get('rating', 0) for item in sorted_data if item.get('rating') is not None]
        
        if len(ratings) < 3:
            return "insufficient_data"
        
        # Simple trend analysis
        recent_ratings = ratings[-3:]
        early_ratings = ratings[:3]
        
        recent_avg = statistics.mean(recent_ratings)
        early_avg = statistics.mean(early_ratings)
        
        if recent_avg > early_avg + 0.5:
            return "improving"
        elif recent_avg < early_avg - 0.5:
            return "declining"
        else:
            return "stable"
    
    def _get_performance_level(self, success_rate: float, avg_rating: float) -> str:
        """Determine performance level based on success rate and average rating."""
        if success_rate >= EXCELLENT_SUCCESS_RATE and avg_rating >= EXCELLENT_AVG_RATING:
            return "excellent"
        elif success_rate >= GOOD_SUCCESS_RATE and avg_rating >= GOOD_AVG_RATING:
            return "good"
        elif success_rate >= FAIR_SUCCESS_RATE and avg_rating >= FAIR_AVG_RATING:
            return "fair"
        else:
            return "poor"
    
    def _calculate_confidence(self, sample_size: int, success_rate: float) -> str:
        """Calculate confidence level for keyword analysis."""
        if sample_size >= MIN_DATA_SIZE_FOR_HIGH_CONFIDENCE and success_rate > HIGH_SUCCESS_RATE_THRESHOLD:
            return "high"
        elif sample_size >= MIN_DATA_SIZE_FOR_MEDIUM_CONFIDENCE and success_rate > MEDIUM_SUCCESS_RATE_THRESHOLD:
            return "medium"
        else:
            return "low"
    
    def _assess_analysis_quality(self, effectiveness: Dict[str, Any]) -> str:
        """Assess the quality of the keyword effectiveness analysis."""
        if not effectiveness:
            return "no_data"
        
        high_confidence_count = sum(
            1 for data in effectiveness.values() 
            if data.get('confidence') == 'high'
        )
        
        if high_confidence_count >= 3:
            return "high"
        elif high_confidence_count >= 1:
            return "medium"
        else:
            return "low"
    
    def _extract_keywords_from_prompt(self, prompt: str) -> List[str]:
        """Extract ##keywords from a prompt."""
        import re
        from core.constants import KEYWORD_PATTERN
        return re.findall(KEYWORD_PATTERN, prompt)
    
    def _assess_suggestion_confidence(
        self, 
        data_size: int, 
        analysis_quality: str
    ) -> str:
        """Assess confidence level for suggestions."""
        # Use original thresholds for suggestion confidence (20 for high, 10 for medium)
        if data_size >= 20 and analysis_quality == "high":
            return "high"
        elif data_size >= 10 and analysis_quality in ["high", "medium"]:
            return "medium"
        else:
            return "low"
