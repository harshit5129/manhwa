"""
Enhanced Gemini integration for advanced image generation support
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List, Dict, Optional
import json

# Load environment
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class GeminiEnhanced:
    """Advanced Gemini features for image generation"""
    
    def __init__(self):
        self.model = None
        if GEMINI_API_KEY:
            self.model = genai.GenerativeModel(GEMINI_MODEL)
    
    def is_available(self) -> bool:
        return self.model is not None
    
    def suggest_composition(self, scene_text: str, character: str) -> Dict:
        """
        Get Gemini's suggestions for panel composition
        
        Returns:
            {
                'camera_angle': str,
                'framing': str,
                'focal_point': str,
                'lighting': str,
                'mood': str
            }
        """
        if not self.is_available():
            return {}
        
        prompt = f"""
Analyze this scene and suggest optimal visual composition for a manhwa panel:

Scene: {scene_text}
Character: {character}

Provide suggestions in JSON format:
{{
  "camera_angle": "eye-level/low-angle/high-angle/dutch-angle",
  "framing": "close-up/medium-shot/wide-shot",
  "focal_point": "what should be the focus",
  "lighting": "dramatic/soft/bright/moody",
  "mood": "tense/peaceful/exciting/sad",
  "color_palette": "warm/cool/vibrant/muted",
  "composition_notes": "brief advice"
}}

Respond with ONLY the JSON object.
"""
        
        try:
            response = self.model.generate_content(prompt)
            suggestions = json.loads(response.text.strip())
            return suggestions
        except Exception as e:
            print(f"Composition suggestion failed: {e}")
            return {}
    
    def suggest_style(self, scene_text: str, current_style: str = "manhwa") -> Dict:
        """
        Get style recommendations based on scene content
        
        Returns:
            {
                'primary_style': str,
                'style_mix': dict,
                'reasoning': str
            }
        """
        if not self.is_available():
            return {}
        
        prompt = f"""
Based on this scene, suggest the best art style:

Scene: {scene_text}
Current style: {current_style}

Available styles:
- manhwa: Korean webtoon style
- manga: Japanese manga style
- anime: Japanese anime style
- realistic: Photorealistic
- painterly: Digital painting
- watercolor: Watercolor art

Suggest in JSON:
{{
  "primary_style": "style name",
  "style_mix": {{"style1": 0.7, "style2": 0.3}},
  "reasoning": "why this works",
  "tags": ["tag1", "tag2"]
}}

ONLY JSON response.
"""
        
        try:
            response = self.model.generate_content(prompt)
            suggestions = json.loads(response.text.strip())
            return suggestions
        except Exception as e:
            print(f"Style suggestion failed: {e}")
            return {}
    
    def analyze_panel_quality(self, panel_description: str) -> Dict:
        """
        Analyze if a generated panel description will work well
        
        Returns quality score and suggestions
        """
        if not self.is_available():
            return {}
        
        prompt = f"""
Analyze this panel description for visual quality:

Description: {panel_description}

Rate and suggest improvements in JSON:
{{
  "quality_score": 0-10,
  "clarity": "how clear the prompt is",
  "improvements": ["suggestion1", "suggestion2"],
  "missing_elements": ["what's missing"],
  "potential_issues": ["possible problems"]
}}

ONLY JSON response.
"""
        
        try:
            response = self.model.generate_content(prompt)
            analysis = json.loads(response.text.strip())
            return analysis
        except Exception as e:
            print(f"Quality analysis failed: {e}")
            return {}
    
    def suggest_panel_layout(self, scenes: List[str]) -> Dict:
        """
        Suggest panel layout for a page
        
        Returns:
            {
                'layout_type': '3-panel/4-panel/dynamic',
                'panel_sizes': [sizes],
                'flow': 'reading order'
            }
        """
        if not self.is_available():
            return {}
        
        scenes_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(scenes)])
        
        prompt = f"""
Suggest optimal panel layout for these scenes:

{scenes_text}

Provide layout in JSON:
{{
  "layout_type": "3-panel/4-panel/dynamic",
  "panel_arrangement": "vertical/horizontal/mixed",
  "panel_sizes": ["large", "medium", "small"],
  "emphasis": "which panel should be largest",
  "flow": "reading order explanation"
}}

ONLY JSON response.
"""
        
        try:
            response = self.model.generate_content(prompt)
            layout = json.loads(response.text.strip())
            return layout
        except Exception as e:
            print(f"Layout suggestion failed: {e}")
            return {}
    
    def enhance_prompt_with_style(
        self, 
        base_prompt: str, 
        style: str = "manhwa",
        mood: str = "neutral"
    ) -> str:
        """
        Enhance prompt with specific style characteristics
        """
        if not self.is_available():
            return base_prompt
        
        prompt = f"""
Enhance this image generation prompt with {style} style characteristics:

Base prompt: {base_prompt}
Mood: {mood}

Add appropriate:
- Visual style tags
- Color palette descriptions
- Artistic techniques
- Quality enhancers

Return ONLY the enhanced prompt text, no explanations.
"""
        
        try:
            response = self.model.generate_content(prompt)
            enhanced = response.text.strip()
            
            # Remove quotes if present
            enhanced = enhanced.strip('"\'')
            
            return enhanced
        except Exception as e:
            print(f"Prompt enhancement failed: {e}")
            return base_prompt
    
    def generate_speech_bubble_text(
        self, 
        dialogue: str, 
        character_emotion: str
    ) -> Dict:
        """
        Format dialogue for speech bubbles with style suggestions
        
        Returns:
            {
                'formatted_text': str,
                'bubble_style': str,
                'font_size': str,
                'emphasis': list
            }
        """
        if not self.is_available():
            return {'formatted_text': dialogue}
        
        prompt = f"""
Format this dialogue for a manhwa speech bubble:

Dialogue: {dialogue}
Emotion: {character_emotion}

Suggest in JSON:
{{
  "formatted_text": "text with line breaks",
  "bubble_style": "normal/thought/shout/whisper",
  "font_suggestions": "bold/italic/normal",
  "emphasis_words": ["words", "to", "emphasize"],
  "sfx_suggestions": ["sound effects if any"]
}}

ONLY JSON response.
"""
        
        try:
            response = self.model.generate_content(prompt)
            formatting = json.loads(response.text.strip())
            return formatting
        except Exception as e:
            print(f"Dialogue formatting failed: {e}")
            return {'formatted_text': dialogue}


# Global instance
gemini_enhanced = GeminiEnhanced()


if __name__ == "__main__":
    enhancer = GeminiEnhanced()
    
    if enhancer.is_available():
        print("✓ Gemini Enhanced features available!\n")
        
        # Test composition suggestion
        scene = "Elena draws her sword as the dragon approaches"
        comp = enhancer.suggest_composition(scene, "Elena - silver hair, determined")
        print(f"Composition: {comp}\n")
        
        # Test style suggestion
        style = enhancer.suggest_style(scene)
        print(f"Style: {style}\n")
        
    else:
        print("✗ Gemini not configured")
