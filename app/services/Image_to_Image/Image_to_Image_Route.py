from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
from typing import Optional

from .Image_to_Image_Schema import (
    ImageToImageRequest, 
    ImageToImageResponse, 
    ErrorResponse
)
from .Image_to_Image import image_to_image_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["Image to Image"])

@router.post(
    "/image-to-image",
    response_model=ImageToImageResponse,
    summary="Generate Image from Image and Prompt",
    description="""Generate a new image based on an input image and text prompt using BytePlus Ark AI.
    
    This endpoint accepts:
    - An image file (JPEG, PNG, etc.)
    - A text prompt describing the desired transformation
    
    The service uses BytePlus Ark's seedream-4-0-250828 model for image generation.
    Uses default settings: 2K size, URL response format, watermark enabled.
    """
)
async def generate_image_to_image(
    image: UploadFile = File(
        ..., 
        description="Input image file (JPEG, PNG, etc.) - max 10MB",
        media_type="image/*"
    ),
    prompt: str = Form(
        ..., 
        description="Text prompt describing the desired image transformation",
        min_length=1,
        max_length=1000
    )
):
    """Generate image-to-image transformation"""
    
    try:
        # Log the incoming request
        logger.info(f"Received image-to-image request: prompt='{prompt[:50]}...'")
        
        # Validate file type
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Please upload an image file (JPEG, PNG, etc.)"
            )
        
        # Read the image data
        try:
            image_data = await image.read()
        except Exception as e:
            logger.error(f"Error reading uploaded image: {str(e)}")
            raise HTTPException(status_code=400, detail="Error reading uploaded image file")
        
        # Validate image data
        if not image_data:
            raise HTTPException(status_code=400, detail="Empty image file")
        
        # Create request object
        request = ImageToImageRequest(
            prompt=prompt
        )
        
        # Generate the image
        result = await image_to_image_service.generate_image_to_image(request, image_data)
        
        # Log the result
        if result.success:
            logger.info(f"Successfully generated image in {result.generation_time:.2f}s")
        else:
            logger.warning(f"Image generation failed: {result.message}")
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in image-to-image endpoint: {str(e)}")
        return ImageToImageResponse(
            success=False,
            message=f"Internal server error: {str(e)}",
            prompt_used=prompt if 'prompt' in locals() else "Unknown",
            model_used="seedream-4-0-250828"
        )

@router.get(
    "/image-to-image/health",
    summary="Health Check for Image-to-Image Service",
    description="Check if the Image-to-Image service is healthy and API key is configured"
)
async def health_check():
    """Health check endpoint for image-to-image service"""
    try:
        # Check if service is properly initialized
        if not image_to_image_service.api_key:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "unhealthy",
                    "message": "ARK_API_KEY not configured",
                    "service": "image-to-image"
                }
            )
        
        return {
            "status": "healthy",
            "message": "Image-to-Image service is running",
            "service": "image-to-image",
            "model": image_to_image_service.model,
            "api_configured": True,
            "sdk": "BytePlus Ark SDK"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "message": f"Service error: {str(e)}",
                "service": "image-to-image"
            }
        )

@router.get(
    "/image-to-image/info",
    summary="Get Image-to-Image Service Information",
    description="Get information about available models, sizes, and capabilities"
)
async def service_info():
    """Get service information and capabilities"""
    return {
        "service": "image-to-image",
        "description": "Generate new images based on input images and text prompts using BytePlus Ark AI",
        "model": "seedream-4-0-250828",
        "sdk": "BytePlus Ark SDK",
        "supported_formats": ["JPEG", "PNG", "WebP", "BMP", "TIFF"],
        "max_file_size": "10MB",
        "default_size": "2K",
        "default_response_format": "url",
        "default_watermark": True,
        "features": {
            "simplified_api": "Streamlined API with sensible defaults",
            "prompt_based": "Natural language prompts for image transformation",
            "high_quality": "AI-powered image generation with seedream model"
        },
        "limits": {
            "prompt_length": "1-1000 characters",
            "image_dimensions": "32x32 to 4096x4096 pixels",
            "concurrent_requests": "As per BytePlus API limits"
        }
    }