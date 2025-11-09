"""
Structure prompt loader for laser-cutting constraints.
"""

import os
from pathlib import Path

def load_structure_prompt() -> str:
    """
    Load the structure prompt from prompts/structure.md.
    
    Returns:
        The structure prompt text, or a default if file not found.
    """
    # Get project root (go up from backend/src/core to project root)
    project_root = Path(__file__).parent.parent.parent.parent
    structure_file = project_root / "prompts" / "structure.md"
    
    if structure_file.exists():
        try:
            with open(structure_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract the main description (skip markdown headers)
                # For now, return a simplified version focusing on the key constraints
                return _extract_structure_description(content)
        except Exception as e:
            print(f"Error loading structure prompt: {e}")
            return _get_default_structure_prompt()
    else:
        print(f"Structure prompt file not found at {structure_file}, using default")
        return _get_default_structure_prompt()

def _extract_structure_description(markdown_content: str) -> str:
    """
    Extract the key structure description from markdown content.
    Focuses on the connectivity constraints for laser cutting and detail control.
    """
    # Return a concise version - keep it short so theme prompt dominates
    return (
        "Flat, two-dimensional black and white pattern filling entire canvas edge-to-edge. "
        "No perspective, no depth, no shadows, no 3D appearance, no separate objects. "
        "Black pattern connects image edges; white material forms connected structure. "
        "Bold, simplified style with large-scale elements (minimum 3-5 pixels). "
        "High contrast only, no grayscale."
    )

def _get_default_structure_prompt() -> str:
    """Return a default structure prompt if file cannot be loaded."""
    return (
        "Flat, two-dimensional black and white pattern filling entire canvas edge-to-edge. "
        "No perspective, no depth, no shadows, no 3D appearance, no separate objects. "
        "Black pattern connects image edges; white material forms connected structure. "
        "Bold, simplified style with large-scale elements (minimum 3-5 pixels). "
        "High contrast only, no grayscale."
    )

def combine_prompts(structure_prompt: str, theme_prompt: str) -> str:
    """
    Combine structure and theme prompts into a final generation prompt.
    
    Args:
        structure_prompt: The structure constraints (applied to all images)
        theme_prompt: The theme-specific prompt
        
    Returns:
        Combined prompt string - theme first, then structure constraints
    """
    # Put theme first so it's more prominent, then add structure constraints
    return f"{theme_prompt}. {structure_prompt}"

