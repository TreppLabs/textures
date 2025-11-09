"""
API endpoints for analytics and reporting.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from models.database import get_db
from core.keyword_extractor import KeywordExtractor
from core.rating_analyzer import RatingAnalyzer
from pydantic import BaseModel

router = APIRouter()

# Pydantic models for request/response
class KeywordAnalysis(BaseModel):
    keyword: str
    category: str
    total_uses: int
    average_rating: float
    success_rate: float
    confidence: str

class ThemePerformance(BaseModel):
    theme_id: int
    theme_name: str
    total_images: int
    rated_images: int
    average_rating: float
    success_rate: float

@router.get("/keywords", response_model=List[KeywordAnalysis])
async def get_keyword_analysis(
    theme_id: Optional[int] = Query(None, description="Filter by specific theme"),
    min_uses: int = Query(1, description="Minimum number of uses"),
    db: Session = Depends(get_db)
):
    """Get keyword effectiveness analysis."""
    try:
        # For now, return mock data - we'll implement this when we have image storage
        mock_keywords = [
            KeywordAnalysis(
                keyword="cellular",
                category="organic",
                total_uses=15,
                average_rating=4.2,
                success_rate=0.73,
                confidence="high"
            ),
            KeywordAnalysis(
                keyword="flowing",
                category="organic",
                total_uses=12,
                average_rating=3.8,
                success_rate=0.67,
                confidence="medium"
            ),
            KeywordAnalysis(
                keyword="fractal",
                category="structural",
                total_uses=8,
                average_rating=4.5,
                success_rate=0.88,
                confidence="high"
            ),
            KeywordAnalysis(
                keyword="grid",
                category="structural",
                total_uses=6,
                average_rating=3.2,
                success_rate=0.50,
                confidence="low"
            )
        ]
        
        # Filter by minimum uses
        filtered_keywords = [kw for kw in mock_keywords if kw.total_uses >= min_uses]
        
        return filtered_keywords
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get keyword analysis: {str(e)}")

@router.get("/themes/performance", response_model=List[ThemePerformance])
async def get_theme_performance(
    db: Session = Depends(get_db)
):
    """Get performance metrics for all themes."""
    try:
        # For now, return mock data - we'll implement this when we have image storage
        mock_performance = [
            ThemePerformance(
                theme_id=1,
                theme_name="Organic Cellular",
                total_images=24,
                rated_images=20,
                average_rating=4.1,
                success_rate=0.75
            ),
            ThemePerformance(
                theme_id=2,
                theme_name="Geometric Patterns",
                total_images=18,
                rated_images=15,
                average_rating=3.6,
                success_rate=0.60
            )
        ]
        
        return mock_performance
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get theme performance: {str(e)}")

@router.get("/summary", response_model=dict)
async def get_analytics_summary(db: Session = Depends(get_db)):
    """Get overall analytics summary."""
    try:
        # For now, return mock data
        return {
            "total_themes": 2,
            "total_images": 42,
            "rated_images": 35,
            "average_rating": 3.85,
            "most_effective_keyword": "fractal",
            "most_effective_category": "structural",
            "generation_trend": "increasing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics summary: {str(e)}")
