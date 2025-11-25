"""
Chapter text processing and intelligent scene splitting
"""
import re
from typing import List, Dict, Tuple
from pathlib import Path
from config import SCENE_MARKERS, MIN_SCENE_LENGTH, MAX_SCENE_LENGTH

class Scene:
    """Represents a single visual scene/panel"""
    
    def __init__(self, text: str, index: int):
        self.text = text.strip()
        self.index = index
        self.characters = []
        self.location = "unknown"
        self.mood = "neutral"
        self.action_type = "dialogue"  # dialogue, action, description
        
    def analyze(self):
        """Extract metadata from scene text"""
        text_lower = self.text.lower()
        
        # Detect action vs dialogue
        if '"' in self.text or '"' in self.text or "said" in text_lower:
            self.action_type = "dialogue"
        elif any(verb in text_lower for verb in ["rush", "run", "fight", "jump", "strike", "dodge"]):
            self.action_type = "action"
        else:
            self.action_type = "description"
        
        # Detect mood
        mood_keywords = {
            "tense": ["danger", "fear", "tension", "threat", "dark"],
            "peaceful": ["calm", "gentle", "serene", "quiet", "peaceful"],
            "exciting": ["excitement", "thrilling", "amazing", "wonderful"],
            "sad": ["tear", "cry", "sorrow", "sad", "grief"],
            "angry": ["anger", "rage", "furious", "mad", "shouted"]
        }
        
        for mood, keywords in mood_keywords.items():
            if any(kw in text_lower for kw in keywords):
                self.mood = mood
                break
        
        return self
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "index": self.index,
            "text": self.text,
            "characters": self.characters,
            "location": self.location,
            "mood": self.mood,
            "action_type": self.action_type
        }
    
    def __str__(self):
        return f"Scene {self.index} ({self.action_type}, {self.mood}): {self.text[:50]}..."


class ChapterParser:
    """Parse and split chapter text into visual scenes"""
    
    def __init__(self):
        self.raw_text = ""
        self.scenes: List[Scene] = []
    
    def load_from_file(self, filepath: str) -> str:
        """
        Load chapter from text file
        
        Args:
            filepath: Path to chapter text file
            
        Returns:
            Loaded text content
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.raw_text = f.read()
            print(f"[OK] Loaded chapter: {len(self.raw_text)} characters")
            return self.raw_text
        except Exception as e:
            print(f"[ERROR] Failed to load chapter: {e}")
            return ""
    
    def load_from_string(self, text: str):
        """Load chapter from string"""
        self.raw_text = text
        print(f"[OK] Loaded chapter: {len(self.raw_text)} characters")
    
    def clean_text(self) -> str:
        """Clean and normalize chapter text"""
        text = self.raw_text
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common issues
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        
        # Remove multiple consecutive newlines (keep paragraph breaks)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def split_scenes(self, use_ai: bool = True) -> List[Scene]:
        """
        Split chapter into visual scenes
        
        Strategy:
        1. Try AI helper for intelligent scene detection (if available)
        2. Fallback to rule-based splitting
        3. Merge small fragments
        4. Split overly long sections
        5. Analyze each scene for metadata
        
        Args:
            use_ai: Use AI helper for smart scene detection
        
        Returns:
            List of Scene objects
        """
        # Try AI helper first
        if use_ai:
            try:
                from ai_helper import ai_helper
                
                if ai_helper.is_available():
                    print("Using AI helper for scene detection...")
                    scenes_data = ai_helper.analyze_chapter_scenes(self.raw_text)
                    
                    if scenes_data:
                        self.scenes = []
                        for idx, scene_dict in enumerate(scenes_data):
                            scene = Scene(scene_dict.get('text', ''), idx + 1)
                            scene.mood = scene_dict.get('mood', 'neutral')
                            scene.action_type = 'action' if scene_dict.get('action_level') == 'high' else 'description'
                            self.scenes.append(scene)
                        
                        print(f"[OK] AI detected {len(self.scenes)} scenes")
                        return self.scenes
            except Exception as e:
                print(f"⚠ AI scene detection failed, using fallback: {e}")
        
        # Fallback to rule-based splitting
        print("Using rule-based scene detection...")
        text = self.clean_text()
        
        # First pass: split by markers
        segments = [text]
        for marker in SCENE_MARKERS:
            new_segments = []
            for seg in segments:
                parts = seg.split(marker)
                new_segments.extend([p.strip() for p in parts if p.strip()])
            segments = new_segments
        
        # Second pass: merge small scenes and split large ones
        merged_scenes = []
        current_buffer = ""
        
        for segment in segments:
            word_count = len(segment.split())
            
            # If segment is too short, buffer it
            if word_count < MIN_SCENE_LENGTH:
                current_buffer += " " + segment
                continue
            
            # Add buffered content if any
            if current_buffer:
                segment = current_buffer.strip() + " " + segment
                current_buffer = ""
            
            # If segment is too long, split it
            if word_count > MAX_SCENE_LENGTH:
                sentences = re.split(r'(?<=[.!?])\s+', segment)
                temp_scene = ""
                
                for sent in sentences:
                    temp_scene += sent + " "
                    if len(temp_scene.split()) >= MIN_SCENE_LENGTH:
                        merged_scenes.append(temp_scene.strip())
                        temp_scene = ""
                
                if temp_scene:
                    current_buffer = temp_scene
            else:
                merged_scenes.append(segment)
        
        # Add any remaining buffer
        if current_buffer:
            merged_scenes.append(current_buffer.strip())
        
        # Create Scene objects and analyze
        self.scenes = []
        for idx, scene_text in enumerate(merged_scenes):
            scene = Scene(scene_text, idx + 1)
            scene.analyze()
            self.scenes.append(scene)
        
        print(f"[OK] Split into {len(self.scenes)} scenes")
        return self.scenes
    
    def get_scenes(self) -> List[Scene]:
        """Get all scenes"""
        return self.scenes
    
    def save_scenes(self, filepath: str):
        """Save scene breakdown to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"CHAPTER SCENE BREAKDOWN\n")
            f.write(f"Total scenes: {len(self.scenes)}\n")
            f.write("=" * 80 + "\n\n")
            
            for scene in self.scenes:
                f.write(f"SCENE {scene.index}\n")
                f.write(f"Type: {scene.action_type} | Mood: {scene.mood}\n")
                f.write(f"Text: {scene.text}\n")
                f.write("-" * 80 + "\n\n")
        
        print(f"[OK] Saved scene breakdown: {filepath}")
    
    def __len__(self):
        return len(self.scenes)


# ============================================================================
# USAGE EXAMPLE
# ============================================================================
if __name__ == "__main__":
    # Example chapter text
    sample_chapter = """
    Elena stood at the edge of the cliff, her silver hair dancing in the wind. 
    The ancient city sprawled below, its towers reaching toward the darkening sky.
    
    "Are you ready?" Marcus asked, placing a gentle hand on her shoulder.
    
    She turned to face him, determination burning in her bright blue eyes. 
    "I've been ready for this my entire life."
    
    Suddenly, a massive shadow swept across the valley. The dragon had arrived.
    
    Elena drew her sword, the blade gleaming with ethereal light. 
    This was the moment everything had led to.
    
    Marcus readied his bow, silver arrows catching the last rays of sunlight. 
    "Together," he whispered.
    
    "Together," Elena echoed, and they charged forward.
    """
    
    # Parse the chapter
    parser = ChapterParser()
    parser.load_from_string(sample_chapter)
    scenes = parser.split_scenes()
    
    # Display results
    print(f"\nFound {len(scenes)} scenes:\n")
    for scene in scenes:
        print(scene)
        print()
