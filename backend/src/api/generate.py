"""
API endpoints for texture generation.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from models.database import get_db
from models.schemas import Theme, Generation, Image
from core.openai_client import OpenAIClient
from core.prompt_engine import PromptEngine
from core.keyword_extractor import KeywordExtractor
from pydantic import BaseModel
import os
import httpx
from datetime import datetime
import json

router = APIRouter()

# Pydantic models for request/response
class GenerationRequest(BaseModel):
    theme_id: int
    num_variations: int = 4
    size: str = "1024x1024"
    quality: str = "standard"

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
        print(f"Looking for theme_id: {request.theme_id}")
        theme = db.query(Theme).filter(Theme.id == request.theme_id).first()
        if not theme:
            print(f"Theme {request.theme_id} not found in database")
            raise HTTPException(status_code=404, detail="Theme not found")
        
        print(f"Found theme: {theme.name} with prompt: {theme.base_prompt}")
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
        print(f"Images directory: {images_dir}")
        
        theme_dir = os.path.join(images_dir, f"theme_{request.theme_id}")
        gen_dir = os.path.join(theme_dir, f"gen_{generation.id}")
        os.makedirs(gen_dir, exist_ok=True)
        
        # Generate images using OpenAI
        print(f"Starting OpenAI generation for {len(prompt_variations)} variations")
        generated_images = []
        for i, prompt in enumerate(prompt_variations):
            try:
                print(f"Generating image {i+1}/{len(prompt_variations)} with prompt: {prompt[:50]}...")
                # Generate image via OpenAI
                variations = openai_client.generate_texture_variations(
                    base_prompt=prompt,
                    num_variations=1,
                    size=request.size,
                    quality=request.quality
                )
                
                if not variations:
                    print(f"No variations returned for image {i+1}")
                    continue
                
                image_data = variations[0]
                image_url = image_data["image_url"]
                print(f"Got image URL for image {i+1}: {image_url[:50]}...")
                
                # Download the image (using sync httpx)
                print(f"Downloading image {i+1} from OpenAI...")
                print(f"Image URL: {image_url}")
                
                with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                    response = client.get(image_url)
                    print(f"Download response status for image {i+1}: {response.status_code}")
                    
                    if response.status_code == 200:
                        # Save image to disk
                        filename = f"texture_{generation.id}_{i+1}.png"
                        file_path = os.path.join(gen_dir, filename)
                        print(f"Saving image {i+1} to: {file_path}")
                        print(f"Directory exists? {os.path.exists(gen_dir)}")
                        print(f"Full path: {os.path.abspath(file_path)}")
                        
                        try:
                            with open(file_path, "wb") as f:
                                f.write(response.content)
                            
                            file_size = os.path.getsize(file_path)
                            print(f"Image {i+1} saved successfully! File size: {file_size} bytes")
                            
                            # Verify file was written
                            if not os.path.exists(file_path):
                                print(f"ERROR: File was not created at {file_path}")
                                continue
                        except Exception as save_error:
                            print(f"ERROR saving file: {str(save_error)}")
                            import traceback
                            traceback.print_exc()
                            continue
                        
                        # Store relative path for serving
                        relative_path = f"theme_{request.theme_id}/gen_{generation.id}/{filename}"
                        
                        # Extract keywords from prompt
                        keywords = keyword_extractor.extract_keywords(prompt)
                        
                        # Create image record in database
                        image_record = Image(
                            generation_id=generation.id,
                            filename=filename,
                            file_path=relative_path,
                            prompt=prompt,
                            keywords=json.dumps(keywords),
                            variation_params=json.dumps(image_data.get("variation_params", {}))
                        )
                        db.add(image_record)
                        db.commit()
                        db.refresh(image_record)
                        print(f"Image {i+1} record created in database with ID: {image_record.id}")
                        
                        generated_images.append({
                            "id": image_record.id,
                            "filename": image_record.filename,
                            "file_path": image_record.file_path,
                            "prompt": image_record.prompt,
                            "keywords": keywords,
                            "rating": image_record.rating,
                            "created_at": image_record.created_at.isoformat() if image_record.created_at else datetime.utcnow().isoformat()
                        })
                    else:
                        print(f"ERROR: Failed to download image {i+1}. Status: {response.status_code}")
                        print(f"Response text: {response.text[:200]}")
                        
            except Exception as e:
                import traceback
                print(f"Error generating image {i+1}: {str(e)}")
                print(traceback.format_exc())
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
        print(f"Error in generate_textures: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to generate textures: {str(e)}")

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
