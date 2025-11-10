"""
Utility functions for the backend.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path
import os


def get_project_root() -> Path:
    """
    Get the absolute path to the project root directory.
    
    Returns:
        Path object pointing to the project root.
    """
    # Go up from backend/src/core to project root
    return Path(__file__).parent.parent.parent.parent


def resolve_path(relative_path: str) -> str:
    """
    Resolve a relative path to an absolute path based on project root.
    
    Args:
        relative_path: Relative path string (e.g., "./data/images")
        
    Returns:
        Absolute path string
    """
    if os.path.isabs(relative_path):
        return relative_path
    
    project_root = get_project_root()
    # Remove leading "./" if present
    clean_path = relative_path.lstrip("./")
    return str(project_root / clean_path)


def serialize_theme(theme, include_status: bool = False) -> Dict[str, Any]:
    """
    Serialize a Theme model to a dictionary.
    
    Args:
        theme: Theme SQLAlchemy model instance
        include_status: Whether to include status field
        
    Returns:
        Dictionary with theme data
    """
    result = {
        "id": theme.id,
        "name": theme.name,
        "description": theme.description,
        "base_prompt": theme.base_prompt,
        "parent_theme_id": theme.parent_theme_id,
        "created_at": theme.created_at.isoformat() if theme.created_at else None,
        "updated_at": theme.updated_at.isoformat() if theme.updated_at else None,
    }
    
    if include_status:
        result["status"] = "created"
    
    return result


def get_utc_now() -> datetime:
    """
    Get current UTC datetime (timezone-aware).
    
    Returns:
        Current datetime in UTC timezone
    """
    return datetime.now(timezone.utc)

