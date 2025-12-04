from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
import time
import os
import uuid
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
async def generate_story_simple(
    image: Optional[UploadFile] = File(None),
    gender: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    style: str = Form(...),
    language: str = Form(...),
    story_idea: str = Form(...),
    chapter_number: str = Form(...)
):
    """Generate a personalized story with optional image upload for character analysis."""
    start_time = time.time()
    
    try:
        # Create request object from form data
        request = TextWithImageRequest(
            gender=GenderEnum(gender),
            name=name,
            age=age,
            style=StyleEnum(style),
            language=LanguageEnum(language),
            story_idea=story_idea,
            chapter_number=ChapterEnum(chapter_number)
        )
        
        logger.info(f"Generating story for {request.name}")
        
        # Handle image upload if provided
        uploaded_image_path = None
        if image and image.filename:
            # Create uploads directory if it doesn't exist
            upload_dir = "uploads/text_with_image"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            file_extension = os.path.splitext(image.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            uploaded_image_path = os.path.join(upload_dir, unique_filename)
            
            # Save uploaded file
            with open(uploaded_image_path, "wb") as buffer:
                content = await image.read()
                buffer.write(content)
            
            logger.info(f"Image uploaded successfully: {uploaded_image_path}")
        
        # Generate story with or without uploaded image
        generated_story = text_service.generate_story_with_images(request, uploaded_image_path=uploaded_image_path)
        
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

