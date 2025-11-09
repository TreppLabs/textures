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
from pydantic import BaseModel
import os
import httpx
import asyncio
from datetime import datetime
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
    num_variations: int = 4
    size: str = "1024x1024"  # DALL-E 3 minimum size
    quality: str = "standard"  # Use "standard" for faster generation (not "hd")

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
        if not (1 <= request.num_variations <= 6):
            raise HTTPException(status_code=400, detail="Number of variations must be between 1 and 6")
        
        if request.size not in ["1024x1024", "1792x1024", "1024x1792"]:
            raise HTTPException(status_code=400, detail="Invalid image size")
        
        if request.quality not in ["standard", "hd"]:
            raise HTTPException(status_code=400, detail="Invalid quality setting")
        
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
        images_dir = os.getenv("IMAGES_DIR", "./data/images")
        # Convert to absolute path if relative
        if not os.path.isabs(images_dir):
            # Go up from backend/src/api to project root
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
            images_dir = os.path.join(project_root, images_dir.lstrip("./"))
        logger.info(f"Images directory: {images_dir}")
        
        theme_dir = os.path.join(images_dir, f"theme_{request.theme_id}")
        gen_dir = os.path.join(theme_dir, f"gen_{generation.id}")
        os.makedirs(gen_dir, exist_ok=True)
        
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
                
                # Download the image (using sync httpx)
                logger.info(f"Downloading image {image_index} from OpenAI...")
                with httpx.Client(timeout=60.0, follow_redirects=True) as client:
                    response = client.get(image_url)
                    logger.info(f"Download response status for image {image_index}: {response.status_code}")
                    
                    if response.status_code != 200:
                        logger.error(f"Failed to download image {image_index}. Status: {response.status_code}")
                        logger.error(f"Response text: {response.text[:200]}")
                        return None
                    
                    # Save image to disk
                    filename = f"texture_{generation.id}_{image_index}.png"
                    file_path = os.path.join(gen_dir, filename)
                    logger.info(f"Saving image {image_index} to: {file_path}")
                    
                    try:
                        with open(file_path, "wb") as f:
                            f.write(response.content)
                        
                        file_size = os.path.getsize(file_path)
                        logger.info(f"Image {image_index} saved successfully! File size: {file_size} bytes")
                        
                        if not os.path.exists(file_path):
                            logger.error(f"ERROR: File was not created at {file_path}")
                            return None
                    except Exception as save_error:
                        logger.error(f"ERROR saving file: {str(save_error)}")
                        import traceback
                        logger.error(traceback.format_exc())
                        return None
                    
                    # Store relative path for serving
                    relative_path = f"theme_{request.theme_id}/gen_{generation.id}/{filename}"
                    
                    # Extract keywords from prompt
                    keywords = keyword_extractor.extract_keywords(prompt)
                    
                    # Return image data (we'll save to DB after all images are generated)
                    return {
                        "filename": filename,
                        "file_path": relative_path,
                        "prompt": prompt,
                        "keywords": keywords,
                        "variation_params": image_data.get("variation_params", {}),
                        "image_index": image_index
                    }
                    
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
                    "created_at": image_record.created_at.isoformat() if image_record.created_at else datetime.utcnow().isoformat()
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
