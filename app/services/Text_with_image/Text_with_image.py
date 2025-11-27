import time
import logging
import os
from typing import Dict, List, Optional
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI package not available. Install with: pip install openai")
from .Text_with_image_Schema import (
    TextWithImageRequest,
    GeneratedStory,
    StoryPage,
    GenderEnum,
    StyleEnum,
    LanguageEnum,
    ChapterEnum
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextWithImageService:
    """Service class for generating stories with images based on user input."""
    
    def __init__(self):
        self.story_templates = self._initialize_story_templates()
        self.style_prompts = self._initialize_style_prompts()
        
        # OpenAI configuration
        self.openai_api_key = ""
        self.openai_model = "gpt-3.5-turbo"
        
        if OPENAI_AVAILABLE and self.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
            logger.info("OpenAI API configured successfully")
        else:
            self.openai_client = None
            logger.warning("OpenAI not available or API key not set. Using template-based stories.")
        
    def _initialize_story_templates(self) -> Dict[str, Dict[str, str]]:
        """Initialize story templates for different languages."""
        return {
            "English": {
                "intro": "Once upon a time, there was a {gender_adj} {age}-year-old named {name}.",
                "adventure_start": "{name} discovered something magical that would change everything.",
                "conflict": "But {name} faced a great challenge that tested their courage.",
                "resolution": "With determination and heart, {name} found a way to overcome the obstacle.",
                "ending": "And so {name} learned that with courage and kindness, anything is possible."
            },
            "Spanish": {
                "intro": "Érase una vez, había {gender_adj} {age} años llamado {name}.",
                "adventure_start": "{name} descubrió algo mágico que lo cambiaría todo.",
                "conflict": "Pero {name} enfrentó un gran desafío que puso a prueba su valor.",
                "resolution": "Con determinación y corazón, {name} encontró una manera de superar el obstáculo.",
                "ending": "Y así {name} aprendió que con valor y bondad, todo es posible."
            },
            "French": {
                "intro": "Il était une fois, il y avait {gender_adj} de {age} ans nommé {name}.",
                "adventure_start": "{name} découvrit quelque chose de magique qui allait tout changer.",
                "conflict": "Mais {name} fit face à un grand défi qui testa son courage.",
                "resolution": "Avec détermination et cœur, {name} trouva un moyen de surmonter l'obstacle.",
                "ending": "Et ainsi {name} apprit qu'avec courage et gentillesse, tout est possible."
            },
            "Italian": {
                "intro": "C'era una volta {gender_adj} di {age} anni chiamato {name}.",
                "adventure_start": "{name} scoprì qualcosa di magico che avrebbe cambiato tutto.",
                "conflict": "Ma {name} affrontò una grande sfida che mise alla prova il suo coraggio.",
                "resolution": "Con determinazione e cuore, {name} trovò un modo per superare l'ostacolo.",
                "ending": "E così {name} imparò che con coraggio e gentilezza, tutto è possibile."
            },
            "Arabic": {
                "intro": "كان يا ما كان، كان هناك {gender_adj} يبلغ من العمر {age} عامًا يُدعى {name}.",
                "adventure_start": "اكتشف {name} شيئًا سحريًا من شأنه أن يغير كل شيء.",
                "conflict": "لكن {name} واجه تحديًا كبيرًا اختبر شجاعته.",
                "resolution": "بالعزيمة والقلب، وجد {name} طريقة للتغلب على العقبة.",
                "ending": "وهكذا تعلم {name} أنه بالشجاعة واللطف، كل شيء ممكن."
            }
        }
    
    def _initialize_style_prompts(self) -> Dict[str, str]:
        """Initialize style-specific prompts for image generation."""
        return {
            "Cartoon": "bright, animated, cartoon-style illustration with bold colors and fun characters",
            "Storybook": "classic storybook illustration with soft watercolor style and whimsical details",
            "Illustration": "detailed digital illustration with rich colors and artistic composition",
            "Colorful": "vibrant, colorful artwork with dynamic composition and cheerful atmosphere",
            "Simple": "minimalist, clean illustration with simple shapes and gentle colors"
        }
    
    def _get_gender_adjective(self, gender: str, language: str) -> str:
        """Get gender-appropriate adjective for different languages."""
        gender_map = {
            "English": {"Male": "a young boy", "Female": "a young girl"},
            "Spanish": {"Male": "un niño", "Female": "una niña"},
            "French": {"Male": "un garçon", "Female": "une fille"},
            "Italian": {"Male": "un ragazzo", "Female": "una ragazza"},
            "Arabic": {"Male": "فتى", "Female": "فتاة"}
        }
        return gender_map.get(language, {}).get(gender, "a child")
    
    def _determine_pages_count(self, chapter_number: str) -> int:
        """Determine total number of pages based on chapter selection."""
        chapter_map = {
            "Single": 1,
            "Two": 2,
            "Four": 4,
            "Six": 6,
            "Ten": 10
        }
        return chapter_map.get(chapter_number, 1)
    
    def _determine_pages_count(self, chapter_number: str) -> int:
        """Determine total number of pages based on chapter selection."""
        chapter_map = {
            "Single": 1,
            "Two": 2,
            "Four": 4,
            "Six": 6,
            "Ten": 10
        }
        return chapter_map.get(chapter_number, 1)
    

    
    def _generate_story_content(self, request: TextWithImageRequest) -> List[StoryPage]:
        """Generate story content based on user inputs."""
        pages = []
        total_pages = self._determine_pages_count(request.chapter_number)
        templates = self.story_templates.get(request.language, self.story_templates["English"])
        gender_adj = self._get_gender_adjective(request.gender, request.language)
        
        # Base story elements
        story_elements = {
            "name": request.name,
            "age": request.age,
            "gender_adj": gender_adj,
            "idea": request.story_idea
        }
        
        if total_pages == 1:
            # Single page story
            content = f"{templates['intro'].format(**story_elements)} {request.story_idea} {templates['ending'].format(**story_elements)}"
            image_description = f"{self.style_prompts[request.style]}, featuring {request.name} as the main character, {gender_adj} of {request.age} years old, {request.story_idea}"
            pages.append(StoryPage(
                page_number=1,
                title=f"The Adventure of {request.name}",
                content=content,
                image_description=image_description
            ))
        else:
            # Multi-page story
            story_structure = [
                ("Introduction", templates["intro"]),
                ("Adventure Begins", templates["adventure_start"]),
                ("The Challenge", templates["conflict"]),
                ("Resolution", templates["resolution"]),
                ("Happy Ending", templates["ending"])
            ]
            
            # Distribute content across pages
            for i in range(total_pages):
                if i < len(story_structure):
                    title, template = story_structure[i]
                    content = template.format(**story_elements)
                    if i == 1:  # Adventure begins page
                        content += f" {request.story_idea}"
                else:
                    title = f"Chapter {i + 1}"
                    content = f"The story of {request.name} continues with new adventures and discoveries."
                
                image_description = f"{self.style_prompts[request.style]}, showing {request.name} ({gender_adj} of {request.age} years old) in scene {i + 1}, {title.lower()}, {request.story_idea}"
                pages.append(StoryPage(
                    page_number=i + 1,
                    title=title,
                    content=content,
                    image_description=image_description
                ))
        
        return pages
    
    def _generate_openai_story(self, request: TextWithImageRequest) -> List[StoryPage]:
        """Generate story content using OpenAI API with 25-word limit per page."""
        pages = []
        total_pages = self._determine_pages_count(request.chapter_number)
        
        if not OPENAI_AVAILABLE or not self.openai_client:
            # Fallback to template-based generation
            return self._generate_template_story(request)
        
        try:
            # Create OpenAI prompt for story generation
            prompt = f"""
            Create a {total_pages}-page children's story about {request.name}, a {request.age}-year-old {request.gender.lower()} character.
            Story theme: {request.story_idea}
            Style: {request.style}
            Language: {request.language}
            
            Requirements:
            - Each page should have EXACTLY 25 words or less
            - Distribute the complete story across {total_pages} pages
            - Make it age-appropriate and engaging
            - Each page should advance the story
            
            Format your response as JSON:
            {{
                "pages": [
                    {{
                        "page_number": 1,
                        "title": "Page Title",
                        "content": "Story content (max 25 words)"
                    }}
                ]
            }}
            """
            
            logger.info(f"Generating {total_pages}-page story using OpenAI")
            
            # Make API call to OpenAI
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a professional children's story writer. Always respond with valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            # Parse the response
            import json
            content = response.choices[0].message.content
            story_data = json.loads(content)
            
            # Create StoryPage objects with image descriptions
            for page_data in story_data["pages"]:
                # Generate detailed image description based on actual page content
                image_description = self._generate_image_description(
                    page_data["content"], 
                    request.name, 
                    request.style,
                    page_data["page_number"]
                )
                
                pages.append(StoryPage(
                    page_number=page_data["page_number"],
                    title=page_data["title"],
                    content=page_data["content"],
                    image_description=image_description
                ))
            
            logger.info(f"Successfully generated {len(pages)} pages using OpenAI")
            return pages
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {str(e)}. Falling back to templates.")
            return self._generate_template_story(request)
    
    def _generate_image_description(self, content: str, character_name: str, style: str, page_number: int) -> str:
        """Generate detailed image description based on specific page content."""
        style_prompt = self.style_prompts.get(style, "illustration")
        content_lower = content.lower()
        
        # Extract detailed scene elements from content
        scene_elements = []
        objects_and_items = []
        character_actions = []
        emotions_and_mood = []
        
        # Enhanced location detection with more specific descriptions
        locations = {
            "forest": ["forest", "trees", "woods", "jungle"],
            "magical enchanted forest with glowing trees and fairy lights": ["magical forest", "enchanted", "fairy"],
            "royal castle with tall towers and golden gates": ["castle", "palace", "kingdom", "royal"],
            "beautiful garden with colorful flowers and butterflies": ["garden", "flowers", "butterfly", "bloom"],
            "mysterious cave with sparkling crystals": ["cave", "crystal", "underground"],
            "peaceful meadow with rolling hills": ["meadow", "field", "grass", "hills"],
            "cozy home with warm lighting": ["home", "house", "room", "attic"],
            "starry night sky with twinkling stars": ["night", "stars", "moon", "sky"],
            "sunny beach with golden sand": ["beach", "sand", "ocean", "sea"],
            "snowy mountain peak": ["mountain", "snow", "peak", "cold"]
        }
        
        location_found = "in a whimsical storybook setting"
        for location_desc, keywords in locations.items():
            if any(keyword in content_lower for keyword in keywords):
                location_found = f"in {location_desc}"
                break
        
        # Enhanced object and item detection
        items = {
            "holding a magical paintbrush": ["paint", "brush", "canvas", "art"],
            "surrounded by colorful butterflies": ["butterfly", "butterflies"],
            "with a wise owl companion": ["owl", "bird"],
            "near a treasure chest": ["treasure", "chest", "gold"],
            "with a glowing wand": ["wand", "magic", "spell"],
            "reading an ancient book": ["book", "reading", "story"],
            "wearing a beautiful crown": ["crown", "princess", "prince"],
            "with a friendly dragon": ["dragon", "creature"],
            "holding a lantern": ["lantern", "light", "glow"],
            "with musical instruments": ["music", "song", "singing"]
        }
        
        for item_desc, keywords in items.items():
            if any(keyword in content_lower for keyword in keywords):
                objects_and_items.append(item_desc)
        
        # Enhanced action detection
        actions = {
            "dancing gracefully": ["dance", "dancing", "twirl"],
            "running through the scene": ["running", "chase", "hurry", "race"],
            "flying through the air": ["fly", "flying", "soar"],
            "climbing or exploring": ["climb", "explore", "adventure"],
            "painting or creating art": ["paint", "draw", "create", "art"],
            "discovering something wonderful": ["discover", "find", "found", "surprise"],
            "talking to animals": ["talk", "speak", "conversation", "animal"],
            "solving a puzzle or problem": ["solve", "think", "problem", "puzzle"],
            "helping friends": ["help", "friend", "together", "team"],
            "celebrating or cheering": ["celebrate", "cheer", "victory", "success"]
        }
        
        for action_desc, keywords in actions.items():
            if any(keyword in content_lower for keyword in keywords):
                character_actions.append(action_desc)
        
        # Enhanced emotion and mood detection
        emotions = {
            "with a bright, joyful smile": ["happy", "joy", "smile", "laugh", "giggle"],
            "with wonder and curiosity in their eyes": ["wonder", "curious", "amazed", "surprise"],
            "with determination and courage": ["brave", "courage", "determined", "strong"],
            "with a gentle, kind expression": ["kind", "gentle", "caring", "love"],
            "with excitement and energy": ["excited", "energy", "enthusiastic"],
            "with peaceful contentment": ["peaceful", "calm", "content", "serene"],
            "with focused concentration": ["focus", "concentrate", "think", "study"],
            "with magical sparkles around them": ["magic", "magical", "sparkle", "glow"]
        }
        
        for emotion_desc, keywords in emotions.items():
            if any(keyword in content_lower for keyword in keywords):
                emotions_and_mood.append(emotion_desc)
        
        # Combine all elements into a rich description
        description_parts = [style_prompt]
        description_parts.append(f"showing {character_name}")
        
        if character_actions:
            description_parts.append(character_actions[0])
        
        if objects_and_items:
            description_parts.append(objects_and_items[0])
        
        description_parts.append(location_found)
        
        if emotions_and_mood:
            description_parts.append(emotions_and_mood[0])
        
        # Add page-specific context based on actual content words
        content_words = content.split()
        if len(content_words) > 5:
            # Extract key descriptive words from content
            key_words = [word for word in content_words if len(word) > 4 and word.lower() not in 
                        ['there', 'where', 'their', 'would', 'could', 'should', 'about', 'after', 'before']]
            if key_words[:2]:  # Use first 2 meaningful words
                description_parts.append(f"capturing the essence of '{' '.join(key_words[:2]).lower()}'")
        
        description_parts.append(f"page {page_number} illustration")
        
        return ", ".join(description_parts)
    
    def _generate_cover_image_description(self, request: TextWithImageRequest) -> str:
        """Generate a book cover description based on story details."""
        style_prompt = self.style_prompts.get(request.style, "illustration")
        gender_adj = self._get_gender_adjective(request.gender, request.language).lower()
        
        # Create cover description
        cover_description = (
            f"Book cover design in {style_prompt.lower()} style, featuring {request.name}, "
            f"{gender_adj} of {request.age} years old, as the main character. "
            f"Title '{self._generate_story_title(request.name)}' prominently displayed at the top. "
            f"Cover scene depicts the story theme: {request.story_idea}. "
            f"Colorful, eye-catching design suitable for children's book, "
            f"with {request.style.lower()} artistic style, inviting and magical atmosphere"
        )
        
        return cover_description
    
    def _generate_story_title(self, character_name: str) -> str:
        """Generate story title based on character name."""
        return f"The Amazing Adventures of {character_name}"
    
    def _generate_template_story(self, request: TextWithImageRequest) -> List[StoryPage]:
        """Fallback method using templates when OpenAI is not available."""
        pages = []
        total_pages = self._determine_pages_count(request.chapter_number)
        templates = self.story_templates.get(request.language, self.story_templates["English"])
        gender_adj = self._get_gender_adjective(request.gender, request.language)
        
        # Base story elements
        story_elements = {
            "name": request.name,
            "age": request.age,
            "gender_adj": gender_adj,
            "idea": request.story_idea
        }
        
        if total_pages == 1:
            # Single page story (limit to 25 words)
            content = f"Once upon a time, {request.name} discovered something magical. {request.story_idea}. The adventure changed everything forever."
            content = " ".join(content.split()[:25])  # Limit to 25 words
            
            pages.append(StoryPage(
                page_number=1,
                title=f"The Adventure of {request.name}",
                content=content,
                image_description=self._generate_image_description(content, request.name, request.style, 1)
            ))
        else:
            # Multi-page story
            story_parts = [
                f"Once upon a time, {request.name} lived in a wonderful place.",
                f"{request.name} discovered something amazing that would change everything.",
                f"An exciting adventure began with {request.story_idea}.",
                f"Challenges appeared, but {request.name} was brave and determined.",
                f"With courage and kindness, {request.name} found the perfect solution."
            ]
            
            for i in range(total_pages):
                if i < len(story_parts):
                    content = story_parts[i]
                else:
                    content = f"{request.name} continued the amazing adventure with new discoveries."
                
                # Limit to 25 words
                content = " ".join(content.split()[:25])
                
                pages.append(StoryPage(
                    page_number=i + 1,
                    title=f"Chapter {i + 1}",
                    content=content,
                    image_description=self._generate_image_description(content, request.name, request.style, i + 1)
                ))
        
        return pages

    def generate_story_with_images(self, request: TextWithImageRequest, uploaded_image_path: Optional[str] = None) -> GeneratedStory:
        """Generate a complete story with images based on user input."""
        try:
            logger.info(f"Generating story for {request.name} with {request.chapter_number} chapters")
            
            # Generate story pages using OpenAI
            pages = self._generate_openai_story(request)
            
            # Create the complete story
            story = GeneratedStory(
                story_title=self._generate_story_title(request.name),
                character_name=request.name,
                character_gender=request.gender,
                character_age=request.age,
                style=request.style,
                language=request.language,
                total_chapters=self._determine_pages_count(request.chapter_number),
                cover_image_description=self._generate_cover_image_description(request),
                pages=pages
            )
            
            logger.info(f"Successfully generated story with {len(pages)} pages")
            return story
            
        except Exception as e:
            logger.error(f"Error generating story: {str(e)}")
            raise Exception(f"Failed to generate story: {str(e)}")
    
    def get_service_info(self) -> dict:
        """Get service information and capabilities."""
        return {
            "service": "Text with Image Story Generator",
            "description": "Generate personalized stories with custom characters and images",
            "version": "1.0.0",
            "supported_genders": [gender.value for gender in GenderEnum],
            "supported_styles": [style.value for style in StyleEnum],
            "supported_languages": [lang.value for lang in LanguageEnum],
            "supported_chapters": [chapter.value for chapter in ChapterEnum],
            "features": [
                "Personalized character integration",
                "Multi-language support",
                "Various artistic styles",
                "Flexible chapter lengths",
                "Image-based character representation"
            ]
        }
