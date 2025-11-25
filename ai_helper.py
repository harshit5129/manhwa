"""
Free AI Helper - Using Ollama with Llama2!
No API keys required - completely free local AI
"""
import re
from typing import List, Dict, Optional
import json

# Ollama for local AI
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ Install requests: pip install requests")


class OllamaAI:
    """
    Ollama AI integration with Llama2
    Completely free local AI - no API keys!
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
        self.available = self._check_ollama()
        
        if self.available:
            print(f"[OK] Ollama connected with model: {self.model}")
        else:
            print(f"⚠️ Ollama not available. Install from: https://ollama.ai")
            print(f"   Then run: ollama pull {self.model}")
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is running"""
        if not REQUESTS_AVAILABLE:
            return False
        
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def generate(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """Generate text using Ollama"""
        if not self.available:
            return None
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.7
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('response', '').strip()
        except Exception as e:
            print(f"Ollama error: {e}")
        
        return None


class FreeAIHelper:
    """
    Free AI helper using Ollama + rule-based processing
    """
    
    def __init__(self):
        self.ollama = OllamaAI()
    
    def is_available(self) -> bool:
        """Always returns True - rule-based processing always works"""
        return True
    
    def extract_character_info(self, text: str) -> Dict:
        """
        Extract character information using Ollama AI + pattern matching
        
        Args:
            text: Chapter text
            
        Returns:
            Character info dict
        """
        # Try Ollama first for smarter extraction
        if self.ollama.available:
            ollama_result = self._extract_character_with_ollama(text)
            if ollama_result:
                return ollama_result
        
        # Fallback to rule-based extraction
        character_info = {
            'name': 'protagonist',
            'gender': 'unknown',
            'age': 'young adult',
            'hair': '',
            'eyes': '',
            'outfit': '',
            'vibe': ''
        }
        
        # Try to extract name from common patterns
        name_patterns = [
            r'(?:My name is|I am|I\'m|They call me)\s+([A-Z][a-z]+)',
            r'([A-Z][a-z]+)(?:\s+said|\s+thought|\s+walked)',
            r'"([A-Z][a-z]+)!?"',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                character_info['name'] = match.group(1)
                break
        
        # Extract physical descriptions
        if 'silver hair' in text.lower() or 'white hair' in text.lower():
            character_info['hair'] = 'silver hair'
        elif 'black hair' in text.lower():
            character_info['hair'] = 'black hair'
        elif 'blonde' in text.lower() or 'golden hair' in text.lower():
            character_info['hair'] = 'blonde hair'
        elif 'red hair' in text.lower():
            character_info['hair'] = 'red hair'
        elif 'brown hair' in text.lower():
            character_info['hair'] = 'brown hair'
        
        # Extract eye color
        if 'blue eyes' in text.lower():
            character_info['eyes'] = 'blue eyes'
        elif 'green eyes' in text.lower():
            character_info['eyes'] = 'green eyes'
        elif 'brown eyes' in text.lower():
            character_info['eyes'] = 'brown eyes'
        elif 'gray eyes' in text.lower() or 'grey eyes' in text.lower():
            character_info['eyes'] = 'gray eyes'
        
        # Extract gender hints
        pronouns = re.findall(r'\b(he|she|his|her|him)\b', text.lower())
        if pronouns:
            male_count = sum(1 for p in pronouns if p in ['he', 'his', 'him'])
            female_count = sum(1 for p in pronouns if p in ['she', 'her'])
            if male_count > female_count:
                character_info['gender'] = 'male'
            elif female_count > male_count:
                character_info['gender'] = 'female'
        
        return character_info
    
    def _extract_character_with_ollama(self, text: str) -> Optional[Dict]:
        """Use Ollama to extract character info"""
        prompt = f"""Extract the main character information from this text. Return ONLY a JSON object with these fields: name, gender, age, hair, eyes, outfit, vibe.

Text: {text[:1000]}

JSON:"""
        
        response = self.ollama.generate(prompt, max_tokens=200)
        
        if response:
            try:
                # Try to parse JSON from response
                json_match = re.search(r'\{[^}]+\}', response)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass
        
        return None
    
    def analyze_chapter_scenes(self, text: str, max_scenes: int = 15) -> List[Dict]:
        """
        Analyze chapter and split into scenes using Ollama AI + rule-based approach
        
        Args:
            text: Chapter text
            max_scenes: Maximum number of scenes
            
        Returns:
            List of scene dicts with text and metadata
        """
        # Try Ollama first for intelligent scene detection
        if self.ollama.available:
            ollama_scenes = self._analyze_scenes_with_ollama(text, max_scenes)
            if ollama_scenes:
                return ollama_scenes
        
        # Fallback to rule-based splitting
        scenes = []
        
        # Split by paragraph breaks (common scene boundaries)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        current_scene = []
        
        for para in paragraphs:
            # Scene boundary indicators
            is_boundary = any([
                para.startswith(('Chapter', 'Scene', '***', '---')),
                len(current_scene) >= 3,  # Max 3 paragraphs per scene
                len(' '.join(current_scene)) > 500,  # Max 500 chars
            ])
            
            if is_boundary and current_scene:
                # Save current scene
                scene_text = ' '.join(current_scene)
                scenes.append({
                    'text': scene_text,
                    'mood': self._detect_mood(scene_text),
                    'action_level': self._detect_action(scene_text)
                })
                current_scene = []
                
                if len(scenes) >= max_scenes:
                    break
            
            current_scene.append(para)
        
        # Add final scene
        if current_scene and len(scenes) < max_scenes:
            scene_text = ' '.join(current_scene)
            scenes.append({
                'text': scene_text,
                'mood': self._detect_mood(scene_text),
                'action_level': self._detect_action(scene_text)
            })
        
        return scenes
    
    def _analyze_scenes_with_ollama(self, text: str, max_scenes: int) -> Optional[List[Dict]]:
        """Use Ollama to intelligently split scenes"""
        prompt = f"""Split this chapter into {max_scenes} visual scenes for a manhwa/comic. For each scene, provide:
1. The scene text (key moment)
2. Mood (tense/peaceful/exciting/sad/neutral)
3. Action level (high/medium/low)

Format as JSON array.

Chapter: {text[:2000]}

JSON:"""
        
        response = self.ollama.generate(prompt, max_tokens=1000)
        
        if response:
            try:
                # Try to extract JSON array
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass
        
        return None
    
    def _detect_mood(self, text: str) -> str:
        """Detect mood from text using keyword matching"""
        text_lower = text.lower()
        
        # Mood keywords
        moods = {
            'tense': ['danger', 'threat', 'afraid', 'nervous', 'tense', 'worried'],
            'peaceful': ['calm', 'peaceful', 'serene', 'quiet', 'gentle'],
            'exciting': ['exciting', 'thrilling', 'adventure', 'rushed', 'fast'],
            'sad': ['sad', 'tears', 'crying', 'sorrow', 'grief', 'loss'],
            'happy': ['happy', 'joy', 'smile', 'laugh', 'delight', 'cheerful'],
            'mysterious': ['mysterious', 'strange', 'unknown', 'shadow', 'hidden']
        }
        
        mood_scores = {}
        for mood, keywords in moods.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                mood_scores[mood] = score
        
        return max(mood_scores, key=mood_scores.get) if mood_scores else 'neutral'
    
    def _detect_action(self, text: str) -> str:
        """Detect action level from text"""
        text_lower = text.lower()
        
        action_words = [
            'fight', 'battle', 'attack', 'run', 'chase', 'strike',
            'dodge', 'jump', 'rushed', 'sprinted', 'charged'
        ]
        
        action_count = sum(1 for word in action_words if word in text_lower)
        
        if action_count >= 3:
            return 'high'
        elif action_count >= 1:
            return 'medium'
        else:
            return 'low'
    
    def enhance_prompt(self, base_prompt: str, scene_text: str = "") -> str:
        """
        Enhance image generation prompt with Ollama AI + quality tags
        
        Args:
            base_prompt: Base prompt
            scene_text: Scene text for context
            
        Returns:
            Enhanced prompt
        """
        # Try Ollama for intelligent enhancement
        if self.ollama.available and scene_text:
            ollama_enhanced = self._enhance_prompt_with_ollama(base_prompt, scene_text)
            if ollama_enhanced:
                return ollama_enhanced
        
        # Fallback to rule-based enhancement
        quality_tags = [
            "highly detailed",
            "professional digital art",
            "best quality",
            "8k resolution"
        ]
        
        # Detect if dialogue/action scene
        if scene_text:
            if any(word in scene_text.lower() for word in ['said', 'asked', 'shouted', '"']):
                quality_tags.append("expressive face")
            if any(word in scene_text.lower() for word in ['fight', 'battle', 'run']):
                quality_tags.append("dynamic action pose")
        
        enhanced = f"{base_prompt}, {', '.join(quality_tags)}"
        
        return enhanced
    
    def _enhance_prompt_with_ollama(self, base_prompt: str, scene_text: str) -> Optional[str]:
        """Use Ollama to enhance image prompt"""
        prompt = f"""Enhance this Stable Diffusion prompt for a manhwa/comic panel based on the scene.
Add artistic details, camera angles, lighting, mood. Keep it under 75 words.

Scene: {scene_text[:200]}
Base prompt: {base_prompt}

Enhanced prompt:"""
        
        response = self.ollama.generate(prompt, max_tokens=150)
        
        if response and len(response) < 500:
            # Clean up the response
            enhanced = response.strip().strip('"\'')
            if enhanced and not enhanced.startswith('Enhanced'):
                return enhanced
        
        return None


# Global instance
ai_helper = FreeAIHelper()


# ============================================================================
# TESTING
# ============================================================================
if __name__ == "__main__":
    helper = FreeAIHelper()
    
    print("Free AI Helper Test")
    print("=" * 60)
    print(f"Available: {helper.is_available()}")
    print(f"Ollama: {helper.ollama_available}")
    print()
    
    # Test character extraction
    sample_text = """
    Elena stood at the edge of the cliff, her silver hair dancing in the wind.
    Her bright blue eyes scanned the horizon. She wore black combat armor.
    "Are you ready?" Marcus asked.
    """
    
    print("Character Extraction:")
    char_info = helper.extract_character_info(sample_text)
    print(json.dumps(char_info, indent=2))
    print()
    
    # Test scene analysis
    print("Scene Analysis:")
    scenes = helper.analyze_chapter_scenes(sample_text)
    for i, scene in enumerate(scenes):
        print(f"Scene {i+1}:")
        print(f"  Mood: {scene['mood']}")
        print(f"  Action: {scene['action_level']}")
        print()
    
    # Test prompt enhancement
    print("Prompt Enhancement:")
    base = "warrior woman on mountain"
    enhanced = helper.enhance_prompt(base, sample_text)
    print(f"Base: {base}")
    print(f"Enhanced: {enhanced}")
