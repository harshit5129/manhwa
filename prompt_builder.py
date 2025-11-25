"""
Prompt building system for manhwa-style image generation
"""
import random
from typing import Optional, List
from text_processor import Scene
from character_manager import CharacterProfile
from config import (
    BASE_STYLE, NEGATIVE_PROMPT, CAMERA_ANGLES, 
    LIGHTING_MOODS
)

class PromptBuilder:
    """Build optimized prompts for manhwa panel generation"""
    
    def __init__(self):
        self.base_style = BASE_STYLE
        self.negative_prompt = NEGATIVE_PROMPT
    
    def build_prompt(
        self, 
        scene: Scene, 
        character: Optional[CharacterProfile] = None,
        camera_angle: Optional[str] = None,
        lighting: Optional[str] = None,
        use_ai: bool = True
    ) -> str:
        """
        Build a complete generation prompt
        
        Args:
            scene: Scene object with text and metadata
            character: Main character profile (if any)
            camera_angle: Specific camera angle (auto-selected if None)
            lighting: Specific lighting mood (auto-selected if None)
            use_ai: Use AI for prompt enhancement
            
        Returns:
            Formatted prompt string
        """
        # Try AI enhancement first
        if use_ai:
            try:
                from ai_helper import ai_helper
                
                if ai_helper.is_available() and character:
                    char_desc = character.get_description()
                    enhanced = ai_helper.enhance_prompt(
                        self.base_style,
                        scene.text
                    )
                    
                    # Add character description if not present
                    if char_desc not in enhanced:
                        enhanced = f"{enhanced}, {char_desc}"
                    
                    # Add quality tags
                    enhanced += ", vertical webtoon panel, masterpiece, best quality, sharp focus"
                    
                    print(f"[OK] AI enhanced prompt for scene {scene.index}")
                    return enhanced
            except Exception as e:
                print(f"⚠ Prompt enhancement failed, using template: {e}")
        
        # Fallback to template-based prompt
        prompt_parts = []
        
        # 1. Base style
        prompt_parts.append(self.base_style)
        
        # 2. Camera angle (match to scene type)
        if camera_angle is None:
            if scene.action_type == "action":
                camera_angle = random.choice(["dynamic angle", "slightly low angle"])
            elif scene.action_type == "dialogue":
                camera_angle = random.choice(["eye level view", "medium shot", "close-up shot"])
            else:
                camera_angle = random.choice(CAMERA_ANGLES)
        prompt_parts.append(camera_angle)
        
        # 3. Lighting (match to mood)
        if lighting is None:
            mood_lighting_map = {
                "tense": "dramatic lighting, deep shadows",
                "peaceful": "soft natural light, warm tones",
                "exciting": "cinematic lighting, vibrant colors",
                "sad": "moody shadows, desaturated colors",
                "angry": "harsh lighting, high contrast"
            }
            lighting = mood_lighting_map.get(scene.mood, random.choice(LIGHTING_MOODS))
        prompt_parts.append(lighting)
        
        # 4. Character description
        if character:
            char_desc = character.get_description()
            prompt_parts.append(f"main character: {char_desc}")
            
            # Add consistency hint if reference image exists
            if character.reference_image_path:
                prompt_parts.append("consistent character design")
        
        # 5. Scene content
        # Extract key visual elements from scene text
        scene_desc = self._extract_visual_elements(scene.text)
        prompt_parts.append(scene_desc)
        
        # 6. Quality and format tags
        prompt_parts.append("vertical webtoon panel")
        prompt_parts.append("masterpiece, best quality, sharp focus")
        
        # Join all parts
        final_prompt = ", ".join(prompt_parts)
        
        return final_prompt
    
    def _extract_visual_elements(self, scene_text: str, max_length: int = 100) -> str:
        """
        Extract key visual elements from scene text
        
        Args:
            scene_text: Raw scene text
            max_length: Maximum character length
            
        Returns:
            Condensed visual description
        """
        # Remove dialogue (text in quotes)
        import re
        no_dialogue = re.sub(r'"[^"]*"', '', scene_text)
        no_dialogue = re.sub(r'"[^"]*"', '', no_dialogue)
        
        # Clean up
        no_dialogue = no_dialogue.strip()
        
        # If still too long, take first sentence or truncate
        if len(no_dialogue) > max_length:
            sentences = re.split(r'(?<=[.!?])\s+', no_dialogue)
            if sentences:
                no_dialogue = sentences[0]
            
            if len(no_dialogue) > max_length:
                no_dialogue = no_dialogue[:max_length].rsplit(' ', 1)[0] + "..."
        
        return no_dialogue if no_dialogue else scene_text[:max_length]
    
    def get_negative_prompt(self) -> str:
        """Get negative prompt for generation"""
        return self.negative_prompt
    
    def build_batch_prompts(
        self, 
        scenes: List[Scene], 
        character: Optional[CharacterProfile] = None,
        use_ai: bool = True
    ) -> List[tuple]:
        """
        Build prompts for multiple scenes
        
        Args:
            scenes: List of Scene objects
            character: Main character profile
            
        Returns:
            List of (positive_prompt, negative_prompt) tuples
        """
        prompts = []
        
        for scene in scenes:
            positive = self.build_prompt(scene, character, use_ai=use_ai)
            negative = self.get_negative_prompt()
            prompts.append((positive, negative))
        
        return prompts
    
    def save_prompt(self, prompt: str, filepath: str):
        """Save prompt to text file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(prompt)


# ============================================================================
# USAGE EXAMPLE
# ============================================================================
if __name__ == "__main__":
    from text_processor import Scene
    from character_manager import CharacterProfile
    
    # Create a sample scene
    scene = Scene(
        '"Are you ready for this?" Marcus asked, his voice steady despite the danger ahead.',
        1
    )
    scene.action_type = "dialogue"
    scene.mood = "tense"
    
    # Create a character
    char = CharacterProfile("Elena")
    char.hair = "long silver hair"
    char.eyes = "bright blue eyes"
    char.outfit = "elegant black combat armor"
    
    # Build prompt
    builder = PromptBuilder()
    prompt = builder.build_prompt(scene, char)
    
    print("POSITIVE PROMPT:")
    print(prompt)
    print("\n" + "=" * 80 + "\n")
    print("NEGATIVE PROMPT:")
    print(builder.get_negative_prompt())
