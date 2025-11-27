from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"

class StyleEnum(str, Enum):
    CARTOON = "Cartoon"
    STORYBOOK = "Storybook"
    ILLUSTRATION = "Illustration"
    COLORFUL = "Colorful"
    SIMPLE = "Simple"

class LanguageEnum(str, Enum):
    ENGLISH = "English"
    ARABIC = "Arabic"
    FRENCH = "French"
    SPANISH = "Spanish"
    ITALIAN = "Italian"

class ChapterEnum(str, Enum):
    SINGLE = "Single"
    TWO = "Two"
    FOUR = "Four"
    SIX = "Six"
    TEN = "Ten"

class TextWithImageRequest(BaseModel):
    gender: GenderEnum = Field(..., description="Character gender: Male or Female")
    name: str = Field(..., min_length=1, max_length=50, description="Character name")
    age: int = Field(..., ge=1, le=100, description="Character age")
    style: StyleEnum = Field(..., description="Story style: Cartoon, Storybook, Illustration, Colorful, or Simple")
    language: LanguageEnum = Field(..., description="Story language: English, Arabic, French, Spanish, or Italian")
    story_idea: str = Field(..., min_length=10, max_length=1000, description="Story idea provided by the user")
    chapter_number: ChapterEnum = Field(..., description="Number of chapters: Single, Two, Four, Six, or Ten")

class StoryPage(BaseModel):
    page_number: int = Field(..., description="Page number")
    title: str = Field(..., description="Page title")
    content: str = Field(..., description="Page content/text")
    image_description: str = Field(..., description="Description of the image for this page")

class GeneratedStory(BaseModel):
    story_title: str = Field(..., description="Generated story title")
    character_name: str = Field(..., description="Main character name")
    character_gender: str = Field(..., description="Character gender")
    character_age: int = Field(..., description="Character age")
    style: str = Field(..., description="Story style")
    language: str = Field(..., description="Story language")
    total_chapters: int = Field(..., description="Total number of chapters")
    cover_image_description: str = Field(..., description="Description for the book cover image")
    pages: List[StoryPage] = Field(..., description="List of story pages")
    
class TextWithImageResponse(BaseModel):
    success: bool = Field(..., description="Whether the story generation was successful")
    message: str = Field(..., description="Response message")
    story: Optional[GeneratedStory] = Field(None, description="Generated story data")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

class ServiceInfoResponse(BaseModel):
    service: str
    description: str
    version: str
    endpoints: List[str]
    supported_formats: dict