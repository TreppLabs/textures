"""
API endpoints for image management and rating.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
import json
from models.database import get_db
from models.schemas import Image as ImageModel, Generation, Theme
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

@router.get("/theme/{theme_id}", response_model=List[ImageResponse])
async def get_images_by_theme(
    theme_id: int,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all images for a specific theme."""
    try:
        # Verify theme exists
        theme = db.query(Theme).filter(Theme.id == theme_id).first()
        if not theme:
            raise HTTPException(status_code=404, detail="Theme not found")
        
        # Get generations for this theme
        generations = db.query(Generation.id).filter(Generation.theme_id == theme_id).all()
        generation_ids = [g.id for g in generations]
        
        if not generation_ids:
            return []
        
        # Get images for these generations
        images = db.query(ImageModel)\
            .filter(ImageModel.generation_id.in_(generation_ids))\
            .order_by(desc(ImageModel.created_at))\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        return [image_to_response(img) for img in images]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch theme images: {str(e)}")

@router.get("/top-per-theme", response_model=List[ImageResponse])
async def get_top_image_per_theme(
    db: Session = Depends(get_db)
):
    """Get the top-rated image from each theme (or most recent if no ratings)."""
    try:
        # Get all themes
        themes = db.query(Theme).all()
        top_images = []
        
        for theme in themes:
            # Get generations for this theme
            generations = db.query(Generation.id).filter(Generation.theme_id == theme.id).all()
            generation_ids = [g.id for g in generations]
            
            if not generation_ids:
                continue
            
            # Try to get highest rated image first
            top_image = db.query(ImageModel)\
                .filter(ImageModel.generation_id.in_(generation_ids))\
                .filter(ImageModel.rating.isnot(None))\
                .order_by(desc(ImageModel.rating), desc(ImageModel.created_at))\
                .first()
            
            # If no rated images, get most recent
            if not top_image:
                top_image = db.query(ImageModel)\
                    .filter(ImageModel.generation_id.in_(generation_ids))\
                    .order_by(desc(ImageModel.created_at))\
                    .first()
            
            if top_image:
                top_images.append(image_to_response(top_image))
        
        # Sort by rating (highest first), then by creation date
        top_images.sort(key=lambda x: (x.rating or 0, x.created_at), reverse=True)
        
        return top_images
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch top images: {str(e)}")

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
