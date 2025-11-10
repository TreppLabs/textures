"""
Helper functions for texture generation.
"""

import os
import httpx
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


def prepare_generation_directory(
    images_dir: str, 
    theme_id: int, 
    generation_id: int
) -> str:
    """
    Prepare directory structure for storing generated images.
    
    Args:
        images_dir: Base images directory
        theme_id: Theme ID
        generation_id: Generation ID
        
    Returns:
        Path to the generation directory
    """
    theme_dir = os.path.join(images_dir, f"theme_{theme_id}")
    gen_dir = os.path.join(theme_dir, f"gen_{generation_id}")
    os.makedirs(gen_dir, exist_ok=True)
    return gen_dir


def download_and_save_image(
    image_url: str,
    file_path: str,
    image_index: int,
    timeout: float = 60.0
) -> bool:
    """
    Download an image from URL and save it to disk.
    
    Args:
        image_url: URL of the image to download
        file_path: Local file path where image should be saved
        image_index: Index of the image (for logging)
        timeout: Request timeout in seconds
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Downloading image {image_index} from OpenAI...")
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(image_url)
            logger.info(f"Download response status for image {image_index}: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Failed to download image {image_index}. Status: {response.status_code}")
                logger.error(f"Response text: {response.text[:200]}")
                return False
            
            # Save image to disk
            logger.info(f"Saving image {image_index} to: {file_path}")
            with open(file_path, "wb") as f:
                f.write(response.content)
            
            file_size = os.path.getsize(file_path)
            logger.info(f"Image {image_index} saved successfully! File size: {file_size} bytes")
            
            if not os.path.exists(file_path):
                logger.error(f"ERROR: File was not created at {file_path}")
                return False
            
            return True
            
    except Exception as save_error:
        logger.error(f"ERROR saving file: {str(save_error)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def create_image_record_data(
    filename: str,
    relative_path: str,
    prompt: str,
    keywords: List[str],
    variation_params: Dict[str, Any],
    image_index: int
) -> Dict[str, Any]:
    """
    Create image record data dictionary.
    
    Args:
        filename: Image filename
        relative_path: Relative file path for serving
        prompt: Generation prompt
        keywords: Extracted keywords
        variation_params: Variation parameters
        image_index: Image index
        
    Returns:
        Dictionary with image data
    """
    return {
        "filename": filename,
        "file_path": relative_path,
        "prompt": prompt,
        "keywords": keywords,
        "variation_params": variation_params,
        "image_index": image_index
    }

