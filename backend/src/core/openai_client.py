"""
OpenAI API client for texture generation.
"""

import openai
import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from .structure_prompt import load_structure_prompt, combine_prompts

load_dotenv()

class OpenAIClient:
    """Client for interacting with OpenAI API for texture generation."""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "dall-e-3")
        self.structure_prompt = load_structure_prompt()
    
    def generate_texture_variations(
        self, 
        base_prompt: str, 
        num_variations: int = 4,
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple texture variations from a base prompt.
        
        Args:
            base_prompt: The base prompt for texture generation
            num_variations: Number of variations to generate (max 6)
            size: Image size (1024x1024, 1792x1024, or 1024x1792)
            quality: Image quality (standard or hd)
            
        Returns:
            List of dictionaries containing image data and metadata
        """
        if num_variations > 6:
            num_variations = 6
        
        variations = []
        
        for i in range(num_variations):
            try:
                # Create variation of the theme prompt
                theme_variation = self._create_prompt_variation(base_prompt, i)
                
                # Combine structure prompt (applies to all images) with theme prompt
                combined_prompt = combine_prompts(self.structure_prompt, theme_variation)
                
                # Remove ## keywords for the actual API call (they're just for tracking)
                clean_prompt = combined_prompt.replace("##", "")
                
                # The structure prompt already includes black and white, so we don't need to add it again
                enhanced_prompt = clean_prompt
                
                # Generate image
                response = self.client.images.generate(
                    model=self.model,
                    prompt=enhanced_prompt,
                    size=size,
                    quality=quality,
                    n=1,
                    response_format="url"
                )
                
                # Extract image data
                image_data = response.data[0]
                variations.append({
                    "prompt": theme_variation,  # Keep original prompt with ## keywords for tracking
                    "image_url": image_data.url,
                    "variation_index": i,
                    "size": size,
                    "quality": quality,
                    "enhanced_prompt": enhanced_prompt  # Store the actual prompt sent to API
                })
                
            except Exception as e:
                import traceback
                print(f"Error generating variation {i}: {str(e)}")
                print(traceback.format_exc())
                continue
        
        return variations
    
    def _create_prompt_variation(self, base_prompt: str, variation_index: int) -> str:
        """
        Create a variation of the base prompt.
        
        This is a simple implementation that can be enhanced with more sophisticated
        prompt engineering based on keyword analysis and rating history.
        """
        # For now, just add variation descriptors
        variation_descriptors = [
            "with subtle variations",
            "with organic flow",
            "with geometric precision", 
            "with natural randomness",
            "with structured chaos",
            "with flowing lines"
        ]
        
        if variation_index < len(variation_descriptors):
            return f"{base_prompt}, {variation_descriptors[variation_index]}"
        else:
            return base_prompt
    
    def extract_keywords(self, prompt: str) -> List[str]:
        """
        Extract ##keywords from a prompt.
        
        Args:
            prompt: The prompt text to analyze
            
        Returns:
            List of keywords found in the prompt
        """
        import re
        keyword_pattern = r'##(\w+)'
        keywords = re.findall(keyword_pattern, prompt)
        return keywords
    
    def analyze_prompt_effectiveness(self, prompt: str, rating: int) -> Dict[str, Any]:
        """
        Analyze prompt effectiveness based on rating.
        
        Args:
            prompt: The prompt that was rated
            rating: The rating (1-5 stars)
            
        Returns:
            Dictionary with analysis results
        """
        keywords = self.extract_keywords(prompt)
        
        return {
            "keywords": keywords,
            "rating": rating,
            "is_high_rated": rating >= 4,
            "keyword_count": len(keywords),
            "prompt_length": len(prompt)
        }
