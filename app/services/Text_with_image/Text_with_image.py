import time
import logging
import os
import base64
from typing import Dict, List, Optional
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI package not available. Install with: pip install openai")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL package not available. Install with: pip install Pillow")
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
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
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
    

    
    def _generate_story_content(self, request: TextWithImageRequest, uploaded_image_path: Optional[str] = None) -> List[StoryPage]:
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
            page_title = f"The Adventure of {request.name}"
            image_description = self._generate_image_description(content, request.name, request.style, 1, request, page_title, uploaded_image_path)
            pages.append(StoryPage(
                page_number=1,
                title=page_title,
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
                
                image_description = self._generate_image_description(content, request.name, request.style, i + 1, request, title, uploaded_image_path)
                pages.append(StoryPage(
                    page_number=i + 1,
                    title=title,
                    content=content,
                    image_description=image_description
                ))
        
        return pages
    
    def _generate_openai_story(self, request: TextWithImageRequest, uploaded_image_path: Optional[str] = None) -> List[StoryPage]:
        """Generate story content using OpenAI API with 25-word limit per page."""
        pages = []
        total_pages = self._determine_pages_count(request.chapter_number)
        
        if not OPENAI_AVAILABLE or not self.openai_client:
            # Fallback to template-based generation
            return self._generate_template_story(request, uploaded_image_path)
        
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
                # Generate detailed image description based on actual page content with consistent character design
                image_description = self._generate_image_description(
                    page_data["content"], 
                    request.name, 
                    request.style,
                    page_data["page_number"],
                    request,
                    page_data["title"],
                    uploaded_image_path
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
            return self._generate_template_story(request, uploaded_image_path)
    
    def _generate_image_description(self, content: str, character_name: str, style: str, page_number: int, request: TextWithImageRequest = None, page_title: str = None, uploaded_image_path: Optional[str] = None) -> str:
        """Generate detailed image description based on specific page content, maintaining consistency with cover design."""
        # Use base character description for consistency across all pages
        if request:
            base_character_desc = self._generate_base_character_description_with_image(request, uploaded_image_path)
        else:
            style_prompt = self.style_prompts.get(style, "illustration")
            base_character_desc = f"{style_prompt}, featuring {character_name} as the main character"
        
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
        
        # Create page description similar to cover format
        scene_elements = []
        
        if character_actions:
            scene_elements.append(character_actions[0])
        
        if objects_and_items:
            scene_elements.append(objects_and_items[0])
        
        scene_elements.append(location_found)
        
        if emotions_and_mood:
            scene_elements.append(emotions_and_mood[0])
        
        # Build description in cover-like format
        page_description = f"Page {page_number} illustration design. {base_character_desc}. "
        
        # Add scene description (similar to cover scene)
        if scene_elements:
            page_description += f"Page scene depicts {', '.join(scene_elements[:2])}. "
        else:
            page_description += "Page scene depicts the story content in an engaging atmosphere. "
        
        # Add page-specific content context
        content_words = content.split()
        if len(content_words) > 5:
            key_words = [word for word in content_words if len(word) > 4 and word.lower() not in 
                        ['there', 'where', 'their', 'would', 'could', 'should', 'about', 'after', 'before']]
            if key_words[:2]:
                page_description += f"Story moment: '{' '.join(key_words[:2]).lower()}'. "
        
        # End similar to cover format
        page_description += "Colorful, engaging design suitable for children's book"
        
        return page_description
    
    def _generate_base_character_description(self, request: TextWithImageRequest) -> str:
        """Generate base character description for consistent visual design across all images."""
        style_prompt = self.style_prompts.get(request.style, "illustration")
        gender_adj = self._get_gender_adjective(request.gender, request.language).lower()
        
        # Create consistent character design description
        base_character_desc = (
            f"{style_prompt}, featuring {request.name} as the main character, "
            f"{gender_adj} of {request.age} years old. "
            f"Character design: consistent appearance with {request.style.lower()} artistic style, "
            f"same facial features, hair style, clothing, and proportions throughout. "
            f"Story theme: {request.story_idea}"
        )
        
        return base_character_desc
    
    def _encode_image_to_base64(self, image_path: str) -> str:
        """Encode image to base64 for OpenAI Vision API."""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image to base64: {str(e)}")
            return ""
    
    def _analyze_character_features(self, image_path: str) -> Dict[str, str]:
        """Analyze uploaded image to extract character features using OpenAI Vision API."""
        if not self.openai_client or not image_path:
            logger.warning("OpenAI client not available or no image path provided")
            return {}
        
        try:
            # Encode image to base64
            base64_image = self._encode_image_to_base64(image_path)
            if not base64_image:
                return {}
            
            # Prepare the prompt for character analysis
            analysis_prompt = """
            Analyze this image of a person and extract the following physical characteristics:
            1. Skin color (be specific: light, medium, tan, brown, dark, etc.)
            2. Hair color (be specific: blonde, brown, black, red, gray, etc.)
            3. Eyebrow color (usually matches hair color)
            
            Please provide a JSON response with these exact keys:
            - skin_color
            - hair_color
            - eyebrow_color
            
            Be descriptive but concise. Focus on the main character in the image.
            """
            
            # Make API call to OpenAI Vision
            response = self.openai_client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": analysis_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            # Extract the response
            analysis_text = response.choices[0].message.content
            logger.info(f"Character analysis result: {analysis_text}")
            
            # Try to extract features from the response
            features = {}
            lines = analysis_text.lower().split('\n')
            
            for line in lines:
                if 'skin' in line and 'color' in line:
                    # Extract skin color
                    parts = line.split(':')
                    if len(parts) > 1:
                        features['skin_color'] = parts[1].strip().replace('"', '').replace(',', '')
                elif 'hair' in line and 'color' in line:
                    # Extract hair color
                    parts = line.split(':')
                    if len(parts) > 1:
                        features['hair_color'] = parts[1].strip().replace('"', '').replace(',', '')
                elif 'eyebrow' in line and 'color' in line:
                    # Extract eyebrow color
                    parts = line.split(':')
                    if len(parts) > 1:
                        features['eyebrow_color'] = parts[1].strip().replace('"', '').replace(',', '')
            
            # Fallback: if eyebrow color not specified, assume it matches hair color
            if 'hair_color' in features and 'eyebrow_color' not in features:
                features['eyebrow_color'] = features['hair_color']
            
            logger.info(f"Extracted character features: {features}")
            return features
            
        except Exception as e:
            logger.error(f"Error analyzing character features: {str(e)}")
            return {}
    
    def _generate_base_character_description_with_image(self, request: TextWithImageRequest, image_path: Optional[str] = None) -> str:
        """Generate base character description incorporating features from uploaded image."""
        style_prompt = self.style_prompts.get(request.style, "illustration")
        gender_adj = self._get_gender_adjective(request.gender, request.language).lower()
        
        # Analyze character features from image if provided
        character_features = {}
        if image_path:
            character_features = self._analyze_character_features(image_path)
        
        # Build character description with or without image features
        base_desc = (
            f"{style_prompt}, featuring {request.name} as the main character, "
            f"{gender_adj} of {request.age} years old."
        )
        
        # Add physical features if extracted from image
        if character_features:
            feature_desc = []
            if character_features.get('skin_color'):
                feature_desc.append(f"{character_features['skin_color']} skin")
            if character_features.get('hair_color'):
                feature_desc.append(f"{character_features['hair_color']} hair")
            if character_features.get('eyebrow_color'):
                feature_desc.append(f"{character_features['eyebrow_color']} eyebrows")
            
            if feature_desc:
                base_desc += f" Character has {', '.join(feature_desc)}."
        
        # Add consistency requirements
        base_desc += (
            f" Character design: consistent appearance with {request.style.lower()} artistic style, "
            f"same facial features, hair style, clothing, and proportions throughout. "
            f"Story theme: {request.story_idea}"
        )
        
        return base_desc
    
    def _generate_cover_image_description(self, request: TextWithImageRequest) -> str:
        """Generate a book cover description based on story details."""
        base_character_desc = self._generate_base_character_description(request)
        
        # Create cover description using base character design
        cover_description = (
            f"Book cover design. {base_character_desc}. "
            f"Title '{self._generate_story_title(request.name)}' prominently displayed at the top. "
            f"Cover scene depicts the main story theme in an inviting and magical atmosphere. "
            f"Colorful, eye-catching design suitable for children's book"
        )
        
        return cover_description
    
    def _generate_cover_image_description_with_image(self, request: TextWithImageRequest, image_path: Optional[str] = None) -> str:
        """Generate a book cover description incorporating features from uploaded image."""
        base_character_desc = self._generate_base_character_description_with_image(request, image_path)
        
        # Create cover description using base character design
        cover_description = (
            f"Book cover design. {base_character_desc}. "
            f"Title '{self._generate_story_title(request.name)}' prominently displayed at the top. "
            f"Cover scene depicts the main story theme in an inviting and magical atmosphere. "
            f"Colorful, eye-catching design suitable for children's book"
        )
        
        return cover_description
    
    def _generate_story_title(self, character_name: str) -> str:
        """Generate story title based on character name."""
        return f"The Amazing Adventures of {character_name}"
    
    def _generate_template_story(self, request: TextWithImageRequest, uploaded_image_path: Optional[str] = None) -> List[StoryPage]:
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
            
            page_title = f"The Adventure of {request.name}"
            pages.append(StoryPage(
                page_number=1,
                title=page_title,
                content=content,
                image_description=self._generate_image_description(content, request.name, request.style, 1, request, page_title, uploaded_image_path)
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
                
                page_title = f"Chapter {i + 1}"
                pages.append(StoryPage(
                    page_number=i + 1,
                    title=page_title,
                    content=content,
                    image_description=self._generate_image_description(content, request.name, request.style, i + 1, request, page_title, uploaded_image_path)
                ))
        
        return pages

    def generate_story_with_images(self, request: TextWithImageRequest, uploaded_image_path: Optional[str] = None) -> GeneratedStory:
        """Generate a complete story with images based on user input."""
        try:
            logger.info(f"Generating story for {request.name} with {request.chapter_number} chapters")
            
            # Generate story pages using OpenAI
            pages = self._generate_openai_story(request, uploaded_image_path)
            
            # Create the complete story
            story = GeneratedStory(
                story_title=self._generate_story_title(request.name),
                character_name=request.name,
                character_gender=request.gender,
                character_age=request.age,
                style=request.style,
                language=request.language,
                total_chapters=self._determine_pages_count(request.chapter_number),
                cover_image_description=self._generate_cover_image_description_with_image(request, uploaded_image_path),
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
