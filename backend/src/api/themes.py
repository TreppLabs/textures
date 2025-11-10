"""
API endpoints for theme management.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from models.database import get_db
from models.schemas import Theme as ThemeModel
from core.theme_manager import ThemeManager
from pydantic import BaseModel

router = APIRouter()

# Pydantic models for request/response
class ThemeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    base_prompt: str
    parent_theme_id: Optional[int] = None

class ThemeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_prompt: Optional[str] = None

class ThemeBranch(BaseModel):
    name: str
    description: Optional[str] = None
    base_prompt: Optional[str] = None

@router.get("/", response_model=List[dict])
async def get_themes(db: Session = Depends(get_db)):
    """Get all themes."""
    try:
        theme_manager = ThemeManager(db)
        themes = theme_manager.list_themes()
        return themes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch themes: {str(e)}")

@router.get("/{theme_id}", response_model=dict)
async def get_theme(theme_id: int, db: Session = Depends(get_db)):
    """Get a specific theme by ID."""
    try:
        theme_manager = ThemeManager(db)
        theme = theme_manager.get_theme(theme_id)
        
        if "error" in theme:
            raise HTTPException(status_code=404, detail=theme["error"])
        
        return theme
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch theme: {str(e)}")

@router.delete("/{theme_id}", response_model=dict)
async def delete_theme(theme_id: int, db: Session = Depends(get_db)):
    """
    Delete a theme and all associated generations, images, and prompt history.
    
    This will permanently delete:
    - The theme
    - All generations for this theme
    - All images in those generations
    - All prompt history entries for this theme
    """
    try:
        from models.schemas import Generation, Image, PromptHistory
        
        # Get the theme
        theme = db.query(ThemeModel).filter(ThemeModel.id == theme_id).first()
        if not theme:
            raise HTTPException(status_code=404, detail="Theme not found")
        
        # Get all generations for this theme
        generations = db.query(Generation).filter(Generation.theme_id == theme_id).all()
        generation_ids = [g.id for g in generations]
        
        # Delete all images for these generations
        if generation_ids:
            images_deleted = db.query(Image).filter(Image.generation_id.in_(generation_ids)).delete(synchronize_session=False)
        else:
            images_deleted = 0
        
        # Delete prompt history entries for this theme
        prompt_history_deleted = db.query(PromptHistory).filter(PromptHistory.theme_id == theme_id).delete(synchronize_session=False)
        
        # Delete all generations
        generations_deleted = len(generations)
        if generations:
            db.query(Generation).filter(Generation.theme_id == theme_id).delete(synchronize_session=False)
        
        # Delete the theme
        theme_name = theme.name
        db.delete(theme)
        db.commit()
        
        return {
            "message": "Theme deleted successfully",
            "theme_id": theme_id,
            "theme_name": theme_name,
            "generations_deleted": generations_deleted,
            "images_deleted": images_deleted,
            "prompt_history_deleted": prompt_history_deleted
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete theme: {str(e)}")

@router.post("/", response_model=dict)
async def create_theme(theme_data: ThemeCreate, db: Session = Depends(get_db)):
    """Create a new theme."""
    try:
        theme_manager = ThemeManager(db)
        theme = theme_manager.create_theme(
            name=theme_data.name,
            description=theme_data.description,
            base_prompt=theme_data.base_prompt,
            parent_theme_id=theme_data.parent_theme_id
        )
        
        if "error" in theme:
            raise HTTPException(status_code=400, detail=theme["error"])
        
        return theme
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create theme: {str(e)}")

@router.put("/{theme_id}", response_model=dict)
async def update_theme(
    theme_id: int, 
    theme_data: ThemeUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing theme."""
    try:
        theme_manager = ThemeManager(db)
        theme = theme_manager.update_theme(
            theme_id=theme_id,
            name=theme_data.name,
            base_prompt=theme_data.base_prompt,
            description=theme_data.description
        )
        
        if "error" in theme:
            raise HTTPException(status_code=404, detail=theme["error"])
        
        return theme
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update theme: {str(e)}")

@router.post("/{theme_id}/branch", response_model=dict)
async def branch_theme(
    theme_id: int, 
    branch_data: ThemeBranch, 
    db: Session = Depends(get_db)
):
    """Create a new theme branched from an existing one."""
    try:
        theme_manager = ThemeManager(db)
        theme = theme_manager.branch_theme(
            parent_theme_id=theme_id,
            new_name=branch_data.name,
            new_base_prompt=branch_data.base_prompt,
            description=branch_data.description
        )
        
        if "error" in theme:
            raise HTTPException(status_code=400, detail=theme["error"])
        
        return theme
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to branch theme: {str(e)}")

@router.get("/{theme_id}/statistics", response_model=dict)
async def get_theme_statistics(theme_id: int, db: Session = Depends(get_db)):
    """Get statistics for a specific theme."""
    try:
        theme_manager = ThemeManager(db)
        stats = theme_manager.get_theme_statistics(theme_id)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch theme statistics: {str(e)}")

@router.get("/{theme_id}/images", response_model=List[dict])
async def get_theme_images(theme_id: int, db: Session = Depends(get_db)):
    """Get all images for a specific theme."""
    try:
        # For now, return empty list - we'll implement this when we have image storage
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch theme images: {str(e)}")
