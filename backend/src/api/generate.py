"""
API endpoints for texture generation.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from models.database import get_db
from models.schemas import Theme, Generation, Image
from core.openai_client import OpenAIClient
from core.prompt_engine import PromptEngine
from core.keyword_extractor import KeywordExtractor
from core.utils import resolve_path, get_utc_now
from core.constants import (
    MIN_VARIATIONS,
    MAX_VARIATIONS,
    DEFAULT_VARIATIONS,
    DEFAULT_IMAGE_SIZE,
    VALID_IMAGE_SIZES,
    DEFAULT_QUALITY,
    VALID_QUALITIES,
)
from .generate_helpers import (
    prepare_generation_directory,
    download_and_save_image,
    create_image_record_data,
)
from pydantic import BaseModel
import os
import asyncio
import json
import logging
from pathlib import Path

# Set up logging to both console and file
_log_dir = Path(__file__).parent.parent.parent.parent / "logs"
_log_dir.mkdir(exist_ok=True)
_log_file = _log_dir / "backend.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(_log_file),
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Logging to file: {_log_file}")

router = APIRouter()

# Pydantic models for request/response
class GenerationRequest(BaseModel):
    theme_id: int
    num_variations: int = DEFAULT_VARIATIONS
    size: str = DEFAULT_IMAGE_SIZE  # DALL-E 3 minimum size
    quality: str = DEFAULT_QUALITY  # Use "standard" for faster generation (not "hd")

class GenerationResponse(BaseModel):
    generation_id: int
    images: List[dict]
    base_prompt: str
    variations_generated: int

@router.post("/", response_model=GenerationResponse)
async def generate_textures(
    request: GenerationRequest,
    db: Session = Depends(get_db)
):
    """Generate texture variations for a theme."""
    try:
        # Validate request
        if not (MIN_VARIATIONS <= request.num_variations <= MAX_VARIATIONS):
            raise HTTPException(
                status_code=400, 
                detail=f"Number of variations must be between {MIN_VARIATIONS} and {MAX_VARIATIONS}"
            )
        
        if request.size not in VALID_IMAGE_SIZES:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid image size. Must be one of: {', '.join(VALID_IMAGE_SIZES)}"
            )
        
        if request.quality not in VALID_QUALITIES:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid quality setting. Must be one of: {', '.join(VALID_QUALITIES)}"
            )
        
        # Check if OpenAI API key is configured
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
            )
        
        # Get theme from database
        logger.info(f"Looking for theme_id: {request.theme_id}")
        theme = db.query(Theme).filter(Theme.id == request.theme_id).first()
        if not theme:
            logger.error(f"Theme {request.theme_id} not found in database")
            raise HTTPException(status_code=404, detail="Theme not found")
        
        logger.info(f"Found theme: {theme.name} with prompt: {theme.base_prompt}")
        base_prompt = theme.base_prompt
        
        # Initialize components
        openai_client = OpenAIClient()
        prompt_engine = PromptEngine()
        keyword_extractor = KeywordExtractor()
        
        # Generate prompt variations using the prompt engine
        # For now, we'll use simple variations - can enhance with rating history later
        prompt_variations = []
        for i in range(request.num_variations):
            variation = prompt_engine._apply_variation_strategy(
                base_prompt,
                prompt_engine._select_variation_strategy(i, {}),
                keyword_extractor.extract_keywords(base_prompt),
                {},
                i
            )
            prompt_variations.append(variation["prompt"])
        
        # Create generation record in database
        generation = Generation(
            theme_id=request.theme_id,
            base_prompt=base_prompt,
            variation_params=json.dumps({
                "num_variations": request.num_variations,
                "size": request.size,
                "quality": request.quality
            })
        )
        db.add(generation)
        db.commit()
        db.refresh(generation)
        
        # Prepare image storage directory
        images_dir_env = os.getenv("IMAGES_DIR", "./data/images")
        images_dir = resolve_path(images_dir_env)
        logger.info(f"Images directory: {images_dir}")
        
        gen_dir = prepare_generation_directory(
            images_dir, 
            request.theme_id, 
            generation.id
        )
        
        # Helper function to generate a single image (runs in thread pool)
        def generate_single_image(image_index: int, prompt: str, total_count: int) -> Optional[dict]:
            """Generate and save a single image. Returns image dict or None on error."""
            try:
                logger.info(f"Generating image {image_index}/{total_count} with prompt: {prompt[:80]}...")
                
                # Generate image via OpenAI (this is synchronous, so we'll run it in a thread)
                variations = openai_client.generate_texture_variations(
                    base_prompt=prompt,
                    num_variations=1,
                    size=request.size,
                    quality=request.quality
                )
                
                if not variations:
                    logger.error(f"No variations returned for image {image_index}")
                    return None
                
                image_data = variations[0]
                image_url = image_data["image_url"]
                logger.info(f"Got image URL for image {image_index}: {image_url[:50]}...")
                
                # Prepare file paths
                filename = f"texture_{generation.id}_{image_index}.png"
                file_path = os.path.join(gen_dir, filename)
                relative_path = f"theme_{request.theme_id}/gen_{generation.id}/{filename}"
                
                # Download and save image
                if not download_and_save_image(image_url, file_path, image_index):
                    return None
                
                # Extract keywords from prompt
                keywords = keyword_extractor.extract_keywords(prompt)
                
                # Return image data (we'll save to DB after all images are generated)
                return create_image_record_data(
                    filename=filename,
                    relative_path=relative_path,
                    prompt=prompt,
                    keywords=keywords,
                    variation_params=image_data.get("variation_params", {}),
                    image_index=image_index
                )
                    
            except Exception as e:
                import traceback
                logger.error(f"Error generating image {image_index}: {str(e)}")
                logger.error(traceback.format_exc())
                return None
        
        # Generate all images in parallel
        logger.info(f"Starting parallel OpenAI generation for {len(prompt_variations)} variations")
        
        # Run all image generations in parallel using asyncio
        loop = asyncio.get_event_loop()
        total_count = len(prompt_variations)
        tasks = [
            loop.run_in_executor(None, generate_single_image, i+1, prompt, total_count)
            for i, prompt in enumerate(prompt_variations)
        ]
        
        # Wait for all images to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and save to database
        generated_images = []
        for i, result in enumerate(results):
            image_index = i + 1  # 1-based index for logging
            if isinstance(result, Exception):
                logger.error(f"Exception in image {image_index} generation: {str(result)}")
                import traceback
                logger.error(traceback.format_exc())
                continue
            
            if result is None:
                logger.warning(f"Image {image_index} generation returned None")
                continue
            
            # Save to database
            try:
                image_record = Image(
                    generation_id=generation.id,
                    filename=result["filename"],
                    file_path=result["file_path"],
                    prompt=result["prompt"],
                    keywords=json.dumps(result["keywords"]),
                    variation_params=json.dumps(result["variation_params"])
                )
                db.add(image_record)
                db.commit()
                db.refresh(image_record)
                logger.info(f"Image {image_index} record created in database with ID: {image_record.id}")
                
                generated_images.append({
                    "id": image_record.id,
                    "filename": image_record.filename,
                    "file_path": image_record.file_path,
                    "prompt": image_record.prompt,
                    "keywords": result["keywords"],
                    "rating": image_record.rating,
                    "created_at": image_record.created_at.isoformat() if image_record.created_at else get_utc_now().isoformat()
                })
            except Exception as db_error:
                logger.error(f"Error saving image {image_index} to database: {str(db_error)}")
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        if not generated_images:
            raise HTTPException(status_code=500, detail="Failed to generate any images")
        
        return GenerationResponse(
            generation_id=generation.id,
            images=generated_images,
            base_prompt=base_prompt,
            variations_generated=len(generated_images)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"Failed to generate textures: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/status/{generation_id}", response_model=dict)
async def get_generation_status(
    generation_id: int,
    db: Session = Depends(get_db)
):
    """Get the status of a generation request."""
    try:
        # For now, return mock status
        return {
            "generation_id": generation_id,
            "status": "completed",
            "progress": 100,
            "images_generated": 4,
            "created_at": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get generation status: {str(e)}")
