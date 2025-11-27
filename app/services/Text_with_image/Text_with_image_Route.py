from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import time
from typing import Optional
import logging
from .Text_with_image_Schema import (
    TextWithImageRequest,
    TextWithImageResponse,
    GenderEnum,
    StyleEnum,
    LanguageEnum,
    ChapterEnum
)
from .Text_with_image import TextWithImageService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/text-with-image", tags=["Text with Image"])

# Initialize service
text_service = TextWithImageService()

@router.post("/generate-story-simple", response_model=TextWithImageResponse)
async def generate_story_simple(request: TextWithImageRequest):
    """Generate a personalized story without image upload (JSON request)."""
    start_time = time.time()
    
    try:
        logger.info(f"Generating simple story for {request.name}")
        
        # Generate story without uploaded image
        generated_story = text_service.generate_story_with_images(request, uploaded_image_path=None)
        
        processing_time = time.time() - start_time
        
        return TextWithImageResponse(
            success=True,
            message=f"Story generated successfully for {request.name}!",
            story=generated_story,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error generating simple story: {str(e)}")
        return TextWithImageResponse(
            success=False,
            message=f"Failed to generate story: {str(e)}",
            story=None,
            processing_time=time.time() - start_time
        )

