"""
API endpoints for image management and rating.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import json
from models.database import get_db
from models.schemas import Image as ImageModel
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Pydantic models for request/response
class ImageRating(BaseModel):
    rating: int

class ImageResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    prompt: str
    keywords: Optional[List[str]] = None
    rating: Optional[int] = None
    created_at: str

def parse_keywords(keywords_json: Optional[str]) -> List[str]:
    """Parse keywords from JSON string."""
    if not keywords_json:
        return []
    try:
        keywords = json.loads(keywords_json)
        return keywords if isinstance(keywords, list) else []
    except (json.JSONDecodeError, TypeError):
        return []

def image_to_response(image: ImageModel) -> ImageResponse:
    """Convert Image model to ImageResponse."""
    return ImageResponse(
        id=image.id,
        filename=image.filename,
        file_path=image.file_path,
        prompt=image.prompt,
        keywords=parse_keywords(image.keywords),
        rating=image.rating,
        created_at=image.created_at.isoformat() if image.created_at else datetime.utcnow().isoformat()
    )

@router.get("/", response_model=List[ImageResponse])
async def get_all_images(
    limit: int = 100,
    offset: int = 0,
    min_rating: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all images with optional filtering."""
    try:
        query = db.query(ImageModel)
        
        # Filter by minimum rating if provided
        if min_rating is not None:
            query = query.filter(ImageModel.rating >= min_rating)
        
        # Order by created_at descending (newest first)
        query = query.order_by(desc(ImageModel.created_at))
        
        # Apply pagination
        images = query.offset(offset).limit(limit).all()
        
        return [image_to_response(img) for img in images]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch images: {str(e)}")

@router.get("/recent", response_model=List[ImageResponse])
async def get_recent_images(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get recently generated images."""
    try:
        images = db.query(ImageModel)\
            .order_by(desc(ImageModel.created_at))\
            .limit(limit)\
            .all()
        
        return [image_to_response(img) for img in images]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recent images: {str(e)}")

@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(image_id: int, db: Session = Depends(get_db)):
    """Get a specific image by ID."""
    try:
        image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        return image_to_response(image)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch image: {str(e)}")

@router.post("/{image_id}/rate", response_model=dict)
async def rate_image(
    image_id: int, 
    rating_data: ImageRating, 
    db: Session = Depends(get_db)
):
    """Rate an image (1-5 stars)."""
    try:
        # Validate rating
        if not (1 <= rating_data.rating <= 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Find the image
        image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Update rating
        image.rating = rating_data.rating
        db.commit()
        db.refresh(image)
        
        return {
            "message": "Rating updated successfully",
            "image_id": image_id,
            "rating": rating_data.rating
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to rate image: {str(e)}")

@router.delete("/{image_id}", response_model=dict)
async def delete_image(image_id: int, db: Session = Depends(get_db)):
    """Delete an image."""
    try:
        image = db.query(ImageModel).filter(ImageModel.id == image_id).first()
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        db.delete(image)
        db.commit()
        
        return {"message": "Image deleted successfully", "image_id": image_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")
