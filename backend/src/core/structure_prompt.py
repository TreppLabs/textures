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
    # Return a concise version that emphasizes both connectivity and detail control
    return (
        "The image must be designed for laser cutting where black portions are cut out to create voids/windows, "
        "and white portions remain as solid material. The black pattern must connect the sides of the image, "
        "creating pathways that span from edge to edge. The white material must form a connected structure "
        "that reaches at least one edge of the image to maintain stability. "
        "CRITICAL: The image must be a completely flat, two-dimensional pattern with no perspective, no depth, no shadows, no 3D appearance, no viewing angle, and no separate objects. "
        "The pattern must fill the entire image canvas edge-to-edge with no white borders. It must appear as a flat graphic design filling the entire canvas. "
        "Bold, simplified pattern with large-scale elements. Minimum detail size: all features must be at least 3-5 pixels wide. "
        "Avoid fine details, intricate textures, or tiny elements. Use a coarse, graphic style like bold graphic design or stencil art, "
        "not detailed illustration. High contrast black and white only, no grayscale, no intermediate tones. "
        "Clean, minimal aesthetic with simple shapes and patterns rather than complex, detailed textures."
    )

def _get_default_structure_prompt() -> str:
    """Return a default structure prompt if file cannot be loaded."""
    return (
        "Black and white high contrast image designed for laser cutting. "
        "Black portions create voids, white portions form connected structure reaching image edges. "
        "CRITICAL: Completely flat, two-dimensional pattern with no perspective, no depth, no shadows, no 3D appearance, no viewing angle, no separate objects. "
        "Pattern must fill entire image canvas edge-to-edge with no white borders. Flat graphic design filling entire canvas. "
        "Bold, simplified pattern with large-scale elements. Minimum detail size: all features must be at least 3-5 pixels wide. "
        "Avoid fine details, intricate textures, or tiny elements. Coarse, graphic style like bold graphic design or stencil art."
    )

def combine_prompts(structure_prompt: str, theme_prompt: str) -> str:
    """
    Combine structure and theme prompts into a final generation prompt.
    
    Args:
        structure_prompt: The structure constraints (applied to all images)
        theme_prompt: The theme-specific prompt
        
    Returns:
        Combined prompt string
    """
    return f"{structure_prompt}. {theme_prompt}"

