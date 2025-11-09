"""
Theme management and lineage tracking.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from models.database import SessionLocal
from models.schemas import Theme, Generation, Image, Keyword, PromptHistory

class ThemeManager:
    """Manage theme lifecycle, branching, and lineage tracking."""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def create_theme(
        self, 
        name: str, 
        base_prompt: str, 
        description: str = None,
        parent_theme_id: int = None
    ) -> Dict[str, Any]:
        """
        Create a new theme.
        
        Args:
            name: Theme name
            base_prompt: Base prompt for the theme
            description: Optional description
            parent_theme_id: ID of parent theme if branching
            
        Returns:
            Dictionary with created theme data
        """
        try:
            theme = Theme(
                name=name,
                description=description,
                base_prompt=base_prompt,
                parent_theme_id=parent_theme_id
            )
            
            self.db.add(theme)
            self.db.commit()
            self.db.refresh(theme)
            
            return {
                "id": theme.id,
                "name": theme.name,
                "description": theme.description,
                "base_prompt": theme.base_prompt,
                "parent_theme_id": theme.parent_theme_id,
                "created_at": theme.created_at.isoformat(),
                "status": "created"
            }
            
        except Exception as e:
            self.db.rollback()
            return {"error": f"Failed to create theme: {str(e)}"}
        finally:
            self.db.close()
    
    def get_theme(self, theme_id: int) -> Dict[str, Any]:
        """Get theme by ID."""
        try:
            theme = self.db.query(Theme).filter(Theme.id == theme_id).first()
            
            if not theme:
                return {"error": "Theme not found"}
            
            return {
                "id": theme.id,
                "name": theme.name,
                "description": theme.description,
                "base_prompt": theme.base_prompt,
                "parent_theme_id": theme.parent_theme_id,
                "created_at": theme.created_at.isoformat(),
                "updated_at": theme.updated_at.isoformat() if theme.updated_at else None
            }
            
        except Exception as e:
            return {"error": f"Failed to get theme: {str(e)}"}
        finally:
            self.db.close()
    
    def list_themes(self) -> List[Dict[str, Any]]:
        """List all themes."""
        try:
            themes = self.db.query(Theme).all()
            
            return [
                {
                    "id": theme.id,
                    "name": theme.name,
                    "description": theme.description,
                    "base_prompt": theme.base_prompt,
                    "parent_theme_id": theme.parent_theme_id,
                    "created_at": theme.created_at.isoformat(),
                    "updated_at": theme.updated_at.isoformat() if theme.updated_at else None
                }
                for theme in themes
            ]
            
        except Exception as e:
            return [{"error": f"Failed to list themes: {str(e)}"}]
        finally:
            self.db.close()
    
    def branch_theme(
        self, 
        parent_theme_id: int, 
        new_name: str, 
        new_base_prompt: str = None,
        description: str = None
    ) -> Dict[str, Any]:
        """
        Create a new theme branched from an existing one.
        
        Args:
            parent_theme_id: ID of the parent theme
            new_name: Name for the new theme
            new_base_prompt: Modified base prompt (uses parent's if None)
            description: Description for the new theme
            
        Returns:
            Dictionary with created theme data
        """
        try:
            # Get parent theme
            parent_theme = self.db.query(Theme).filter(Theme.id == parent_theme_id).first()
            if not parent_theme:
                return {"error": "Parent theme not found"}
            
            # Use parent's prompt if none provided
            if not new_base_prompt:
                new_base_prompt = parent_theme.base_prompt
            
            # Create new theme
            theme = Theme(
                name=new_name,
                description=description or f"Branched from {parent_theme.name}",
                base_prompt=new_base_prompt,
                parent_theme_id=parent_theme_id
            )
            
            self.db.add(theme)
            self.db.commit()
            self.db.refresh(theme)
            
            return {
                "id": theme.id,
                "name": theme.name,
                "description": theme.description,
                "base_prompt": theme.base_prompt,
                "parent_theme_id": theme.parent_theme_id,
                "created_at": theme.created_at.isoformat(),
                "status": "branched"
            }
            
        except Exception as e:
            self.db.rollback()
            return {"error": f"Failed to branch theme: {str(e)}"}
        finally:
            self.db.close()
    
    def get_theme_lineage(self, theme_id: int) -> Dict[str, Any]:
        """
        Get the lineage (parent/child relationships) for a theme.
        
        Args:
            theme_id: ID of the theme to get lineage for
            
        Returns:
            Dictionary with lineage information
        """
        try:
            theme = self.db.query(Theme).filter(Theme.id == theme_id).first()
            if not theme:
                return {"error": "Theme not found"}
            
            # Get ancestors
            ancestors = []
            current_theme = theme
            while current_theme.parent_theme_id:
                parent = self.db.query(Theme).filter(Theme.id == current_theme.parent_theme_id).first()
                if parent:
                    ancestors.append({
                        "id": parent.id,
                        "name": parent.name,
                        "base_prompt": parent.base_prompt
                    })
                    current_theme = parent
                else:
                    break
            
            # Get descendants
            descendants = self.db.query(Theme).filter(Theme.parent_theme_id == theme_id).all()
            descendants_data = [
                {
                    "id": child.id,
                    "name": child.name,
                    "base_prompt": child.base_prompt
                }
                for child in descendants
            ]
            
            return {
                "current_theme": {
                    "id": theme.id,
                    "name": theme.name,
                    "base_prompt": theme.base_prompt
                },
                "ancestors": ancestors,
                "descendants": descendants_data,
                "lineage_depth": len(ancestors)
            }
            
        except Exception as e:
            return {"error": f"Failed to get theme lineage: {str(e)}"}
        finally:
            self.db.close()
    
    def update_theme(
        self, 
        theme_id: int, 
        name: str = None, 
        base_prompt: str = None,
        description: str = None
    ) -> Dict[str, Any]:
        """
        Update theme properties.
        
        Args:
            theme_id: ID of theme to update
            name: New name (optional)
            base_prompt: New base prompt (optional)
            description: New description (optional)
            
        Returns:
            Dictionary with updated theme data
        """
        try:
            theme = self.db.query(Theme).filter(Theme.id == theme_id).first()
            if not theme:
                return {"error": "Theme not found"}
            
            # Update fields if provided
            if name is not None:
                theme.name = name
            if base_prompt is not None:
                theme.base_prompt = base_prompt
            if description is not None:
                theme.description = description
            
            theme.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(theme)
            
            return {
                "id": theme.id,
                "name": theme.name,
                "description": theme.description,
                "base_prompt": theme.base_prompt,
                "parent_theme_id": theme.parent_theme_id,
                "created_at": theme.created_at.isoformat(),
                "updated_at": theme.updated_at.isoformat(),
                "status": "updated"
            }
            
        except Exception as e:
            self.db.rollback()
            return {"error": f"Failed to update theme: {str(e)}"}
        finally:
            self.db.close()
    
    def get_theme_statistics(self, theme_id: int) -> Dict[str, Any]:
        """
        Get statistics for a theme.
        
        Args:
            theme_id: ID of the theme
            
        Returns:
            Dictionary with theme statistics
        """
        try:
            # Get theme
            theme = self.db.query(Theme).filter(Theme.id == theme_id).first()
            if not theme:
                return {"error": "Theme not found"}
            
            # Get generations count
            generations_count = self.db.query(Generation).filter(Generation.theme_id == theme_id).count()
            
            # Get images count
            images_count = self.db.query(Image).join(Generation).filter(Generation.theme_id == theme_id).count()
            
            # Get rated images count
            rated_images_count = self.db.query(Image).join(Generation).filter(
                Generation.theme_id == theme_id,
                Image.rating.isnot(None)
            ).count()
            
            # Get average rating
            avg_rating_result = self.db.query(Image.rating).join(Generation).filter(
                Generation.theme_id == theme_id,
                Image.rating.isnot(None)
            ).all()
            
            avg_rating = None
            if avg_rating_result:
                ratings = [r[0] for r in avg_rating_result if r[0] is not None]
                if ratings:
                    avg_rating = sum(ratings) / len(ratings)
            
            return {
                "theme_id": theme_id,
                "theme_name": theme.name,
                "generations_count": generations_count,
                "images_count": images_count,
                "rated_images_count": rated_images_count,
                "average_rating": round(avg_rating, 2) if avg_rating else None,
                "completion_rate": round(rated_images_count / images_count, 2) if images_count > 0 else 0
            }
            
        except Exception as e:
            return {"error": f"Failed to get theme statistics: {str(e)}"}
        finally:
            self.db.close()
