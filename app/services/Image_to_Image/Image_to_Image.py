import os
import time
import base64
import logging
import tempfile
import requests
from typing import Optional, Tuple
from PIL import Image
import io

from .Image_to_Image_Schema import ImageToImageRequest, ImageToImageResponse, ErrorResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageToImageService:
    """Service class for handling Image-to-Image generation using BytePlus Ark API"""
    
    def __init__(self):
        self.api_key = os.getenv("ARK_API_KEY")
        self.model = "seedream-4-0-250828"
        self.base_url = "https://ark.ap-southeast.bytepluses.com/api/v3/images/generations"
        
        if not self.api_key:
            logger.error("ARK_API_KEY not found in environment variables")
            raise ValueError("ARK_API_KEY is required")
        
        logger.info("✅ Image-to-Image service initialized successfully")
    
    def validate_image_file(self, image_data: bytes, max_size_mb: int = 10) -> Tuple[bool, str]:
        """Validate uploaded image file"""
        try:
            # Check file size
            size_mb = len(image_data) / (1024 * 1024)
            if size_mb > max_size_mb:
                return False, f"Image size ({size_mb:.2f}MB) exceeds maximum allowed size ({max_size_mb}MB)"
            
            # Check if it's a valid image by trying to decode
            try:
                img = Image.open(io.BytesIO(image_data))
                img.verify()
                
                # Get image dimensions
                img = Image.open(io.BytesIO(image_data))  # Reopen after verify
                width, height = img.size
                
                # Check minimum dimensions
                if width < 32 or height < 32:
                    return False, "Image is too small (minimum 32x32 pixels)"
                
                # Check maximum dimensions  
                if width > 4096 or height > 4096:
                    return False, "Image is too large (maximum 4096x4096 pixels)"
                
            except Exception as e:
                return False, f"Invalid image file: {str(e)}"
            
            return True, "Valid image"
            
        except Exception as e:
            return False, f"Error validating image: {str(e)}"
    
    def save_temp_image(self, image_data: bytes) -> Optional[str]:
        """Save image data to temporary file and return the path"""
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(image_data)
                temp_path = temp_file.name
            
            return temp_path
        except Exception as e:
            logger.error(f"Error saving temporary image: {str(e)}")
            return None
    
    def cleanup_temp_file(self, file_path: str):
        """Clean up temporary file"""
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.warning(f"Could not clean up temporary file {file_path}: {str(e)}")
    
    async def generate_image_to_image(
        self, 
        request: ImageToImageRequest, 
        image_data: bytes
    ) -> ImageToImageResponse:
        """Generate image-to-image using BytePlus Ark SDK"""
        start_time = time.time()
        temp_image_path = None
        
        try:
            # Validate the input image
            is_valid, validation_message = self.validate_image_file(image_data)
            if not is_valid:
                return ImageToImageResponse(
                    success=False,
                    message=f"Image validation failed: {validation_message}",
                    prompt_used=request.prompt,
                    model_used=self.model
                )
            
            # Save image to temporary file (BytePlus SDK might need file path)
            temp_image_path = self.save_temp_image(image_data)
            if not temp_image_path:
                return ImageToImageResponse(
                    success=False,
                    message="Failed to process uploaded image",
                    prompt_used=request.prompt,
                    model_used=self.model
                )
            
            # For this example, we'll use a base64 data URL
            # In production, you might want to upload to cloud storage
            base64_image = base64.b64encode(image_data).decode('utf-8')
            image_url = f"data:image/jpeg;base64,{base64_image}"
            
            logger.info(f"Generating image with prompt: {request.prompt[:50]}...")
            
            # Prepare the request payload for BytePlus API
            payload = {
                "model": self.model,
                "prompt": request.prompt,
                "image": image_url,  # Using base64 data URL
                "sequential_image_generation": "disabled",
                "size": "4K",  # Default size
                "response_format": "url",  # Default response format
                "watermark": True,  # Default watermark
                "stream": False
            }
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Generate image using BytePlus API via requests
            try:
                response = requests.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=60
                )
                
                generation_time = time.time() - start_time
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Extract the generated image data
                    generated_image_url = None
                    generated_image_data = None
                    
                    if 'data' in response_data and len(response_data['data']) > 0:
                        first_result = response_data['data'][0]
                        
                        # Always use URL format as default
                        if 'url' in first_result:
                            generated_image_url = first_result['url']
                    
                    return ImageToImageResponse(
                        success=True,
                        message="Image generated successfully",
                        image_url=generated_image_url,
                        image_data=generated_image_data,
                        prompt_used=request.prompt,
                        model_used=self.model,
                        generation_time=generation_time
                    )
                else:
                    error_message = f"API request failed with status {response.status_code}"
                    try:
                        error_data = response.json()
                        if 'error' in error_data:
                            error_message += f": {error_data['error']}"
                    except:
                        error_message += f": {response.text[:200]}"
                    
                    logger.error(f"BytePlus API error: {error_message}")
                    
                    return ImageToImageResponse(
                        success=False,
                        message=error_message,
                        prompt_used=request.prompt,
                        model_used=self.model,
                        generation_time=generation_time
                    )
                    
            except requests.exceptions.Timeout:
                return ImageToImageResponse(
                    success=False,
                    message="Request timeout - image generation took too long",
                    prompt_used=request.prompt,
                    model_used=self.model,
                    generation_time=time.time() - start_time
                )
            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception: {str(e)}")
                return ImageToImageResponse(
                    success=False,
                    message=f"Network error: {str(e)}",
                    prompt_used=request.prompt,
                    model_used=self.model,
                    generation_time=time.time() - start_time
                )
                
        except Exception as e:
            logger.error(f"Unexpected error in image generation: {str(e)}")
            return ImageToImageResponse(
                success=False,
                message=f"Unexpected error: {str(e)}",
                prompt_used=request.prompt,
                model_used=self.model,
                generation_time=time.time() - start_time
            )
        finally:
            # Clean up temporary file
            if temp_image_path:
                self.cleanup_temp_file(temp_image_path)

# Create a singleton instance
image_to_image_service = ImageToImageService()