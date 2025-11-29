from pydantic import BaseModel, Field, validator
from typing import Optional

class ImageToImageRequest(BaseModel):
    """Request schema for Image-to-Image generation"""
    prompt: str = Field(
        ..., 
        min_length=1, 
        max_length=1000, 
        description="Text prompt describing the desired image transformation"
    )
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v or not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v.strip()

class ImageToImageResponse(BaseModel):
    """Response schema for Image-to-Image generation"""
    success: bool = Field(..., description="Whether the generation was successful")
    message: str = Field(..., description="Response message")
    image_url: Optional[str] = Field(None, description="URL of the generated image")
    image_data: Optional[str] = Field(None, description="Base64 encoded image data")
    prompt_used: str = Field(..., description="The prompt that was used for generation")
    model_used: str = Field(..., description="Model used for generation")
    generation_time: Optional[float] = Field(None, description="Time taken for generation in seconds")

class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = Field(default=False, description="Always false for error responses")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code if available")
    details: Optional[dict] = Field(None, description="Additional error details")