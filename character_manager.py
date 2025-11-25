"""
Enhanced character manager with reference image support and detailed profiles
"""
from pathlib import Path
import json
from typing import Optional, List, Dict
from PIL import Image
import uuid


class CharacterProfile:
    """Detailed character profile with reference images"""
    
    def __init__(self, name: str):
        self.name = name
        self.character_id = str(uuid.uuid4())[:8]
        
        # Physical attributes
        self.gender = "unknown"
        self.age = "young adult"
        self.height = ""
        self.build = ""
        
        # Appearance
        self.hair_color = ""
        self.hair_style = ""
        self.eye_color = ""
        self.skin_tone = ""
        self.distinguishing_features = ""
        
        # Clothing
        self.default_outfit = ""
        self.outfit_variations = []
        
        # Personality & Style
        self.personality = ""
        self.vibe = ""
        self.expressions = []  # ['happy', 'sad', 'angry', etc.]
        
        # Reference images
        self.reference_images = []  # List of image paths
        self.face_reference = None  # Primary face reference
        
        # Metadata
        self.notes = ""
        self.tags = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for saving"""
        return {
            'character_id': self.character_id,
            'name': self.name,
            'gender': self.gender,
            'age': self.age,
            'height': self.height,
            'build': self.build,
            'hair_color': self.hair_color,
            'hair_style': self.hair_style,
            'eye_color': self.eye_color,
            'skin_tone': self.skin_tone,
            'distinguishing_features': self.distinguishing_features,
            'default_outfit': self.default_outfit,
            'outfit_variations': self.outfit_variations,
            'personality': self.personality,
            'vibe': self.vibe,
            'expressions': self.expressions,
            'reference_images': self.reference_images,
            'face_reference': self.face_reference,
            'notes': self.notes,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary"""
        char = cls(data.get('name', 'Character'))
        char.character_id = data.get('character_id', char.character_id)
        char.gender = data.get('gender', 'unknown')
        char.age = data.get('age', 'young adult')
        char.height = data.get('height', '')
        char.build = data.get('build', '')
        char.hair_color = data.get('hair_color', '')
        char.hair_style = data.get('hair_style', '')
        char.eye_color = data.get('eye_color', '')
        char.skin_tone = data.get('skin_tone', '')
        char.distinguishing_features = data.get('distinguishing_features', '')
        char.default_outfit = data.get('default_outfit', '')
        char.outfit_variations = data.get('outfit_variations', [])
        char.personality = data.get('personality', '')
        char.vibe = data.get('vibe', '')
        char.expressions = data.get('expressions', [])
        char.reference_images = data.get('reference_images', [])
        char.face_reference = data.get('face_reference')
        char.notes = data.get('notes', '')
        char.tags = data.get('tags', [])
        return char
    
    def get_description(self) -> str:
        """Get full character description for prompts"""
        parts = [self.name]
        
        if self.gender and self.gender != 'unknown':
            parts.append(self.gender)
        
        if self.age:
            parts.append(f"{self.age} years old")
        
        if self.hair_color and self.hair_style:
            parts.append(f"{self.hair_color} {self.hair_style} hair")
        elif self.hair_color:
            parts.append(f"{self.hair_color} hair")
        
        if self.eye_color:
            parts.append(f"{self.eye_color} eyes")
        
        if self.default_outfit:
            parts.append(f"wearing {self.default_outfit}")
        
        if self.distinguishing_features:
            parts.append(self.distinguishing_features)
        
        if self.vibe:
            parts.append(f"{self.vibe} expression")
        
        return ", ".join(parts)


class CharacterLibrary:
    """Manage character library with reference images"""
    
    def __init__(self, library_dir: str = "character_library"):
        self.library_dir = Path(library_dir)
        self.library_dir.mkdir(exist_ok=True)
        self.characters = {}
        self.load_all()
    
    def add_character(self, character: CharacterProfile):
        """Add character to library"""
        self.characters[character.character_id] = character
        self.save_character(character)
    
    def save_character(self, character: CharacterProfile):
        """Save character profile"""
        char_file = self.library_dir / f"{character.character_id}.json"
        
        with open(char_file, 'w', encoding='utf-8') as f:
            json.dump(character.to_dict(), f, indent=2)
    
    def load_character(self, character_id: str) -> Optional[CharacterProfile]:
        """Load character from file"""
        char_file = self.library_dir / f"{character_id}.json"
        
        if not char_file.exists():
            return None
        
        with open(char_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return CharacterProfile.from_dict(data)
    
    def load_all(self):
        """Load all characters from library"""
        for char_file in self.library_dir.glob("*.json"):
            with open(char_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                character = CharacterProfile.from_dict(data)
                self.characters[character.character_id] = character
    
    def list_characters(self) -> List[Dict]:
        """List all characters"""
        return [
            {
                'character_id': char.character_id,
                'name': char.name,
                'gender': char.gender,
                'has_reference': bool(char.face_reference),
                'ref_images': len(char.reference_images)
            }
            for char in self.characters.values()
        ]
    
    def delete_character(self, character_id: str) -> bool:
        """Delete character"""
        char_file = self.library_dir / f"{character_id}.json"
        
        if char_file.exists():
            char_file.unlink()
            if character_id in self.characters:
                del self.characters[character_id]
            return True
        
        return False
    
    def add_reference_image(
        self, 
        character_id: str, 
        image_path: str,
        set_as_face: bool = False
    ) -> bool:
        """Add reference image to character"""
        character = self.characters.get(character_id)
        
        if not character:
            return False
        
        # Copy image to library
        image_path = Path(image_path)
        if not image_path.exists():
            return False
        
        # Create character images directory
        char_images_dir = self.library_dir / character_id
        char_images_dir.mkdir(exist_ok=True)
        
        # Copy image
        new_image_name = f"ref_{len(character.reference_images) + 1}{image_path.suffix}"
        new_image_path = char_images_dir / new_image_name
        
        import shutil
        shutil.copy(image_path, new_image_path)
        
        # Update character
        character.reference_images.append(str(new_image_path))
        
        if set_as_face or character.face_reference is None:
            character.face_reference = str(new_image_path)
        
        self.save_character(character)
        
        return True


# Global instance
character_library = CharacterLibrary()


if __name__ == "__main__":
    # Test character library
    lib = CharacterLibrary()
    
    # Create character
    elena = CharacterProfile("Elena")
    elena.gender = "female"
    elena.age = "25"
    elena.hair_color = "silver"
    elena.hair_style = "long flowing"
    elena.eye_color = "bright blue"
    elena.default_outfit = "black combat armor with silver details"
    elena.vibe = "confident and determined"
    elena.distinguishing_features = "scar on left cheek"
    elena.personality = "brave, determined, loyal"
    elena.expressions = ["determined", "fierce", "gentle smile"]
    
    lib.add_character(elena)
    
    print(f"Character created: {elena.character_id}")
    print(f"Description: {elena.get_description()}")
    
    # List characters
    chars = lib.list_characters()
    print(f"\nCharacters in library: {len(chars)}")
    for c in chars:
        print(f"  - {c['name']} ({c['character_id']})")
