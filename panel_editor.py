"""
Panel Editor - Preview and edit prompts before generation
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class PanelPrompt:
    """Individual panel with editable prompt"""
    panel_id: int
    scene_text: str
    generated_prompt: str
    edited_prompt: Optional[str] = None
    negative_prompt: str = ""
    character_ids: List[str] = None
    mood: str = "neutral"
    camera_angle: str = "medium shot"
    lighting: str = "natural"
    composition: str = "centered"
    
    def __post_init__(self):
        if self.character_ids is None:
            self.character_ids = []
    
    def get_final_prompt(self) -> str:
        """Get the prompt to use for generation"""
        return self.edited_prompt if self.edited_prompt else self.generated_prompt
    
    def to_dict(self) -> Dict:
        return {
            'panel_id': self.panel_id,
            'scene_text': self.scene_text,
            'generated_prompt': self.generated_prompt,
            'edited_prompt': self.edited_prompt,
            'negative_prompt': self.negative_prompt,
            'character_ids': self.character_ids,
            'mood': self.mood,
            'camera_angle': self.camera_angle,
            'lighting': self.lighting,
            'composition': self.composition
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            panel_id=data['panel_id'],
            scene_text=data['scene_text'],
            generated_prompt=data['generated_prompt'],
            edited_prompt=data.get('edited_prompt'),
            negative_prompt=data.get('negative_prompt', ''),
            character_ids=data.get('character_ids', []),
            mood=data.get('mood', 'neutral'),
            camera_angle=data.get('camera_angle', 'medium shot'),
            lighting=data.get('lighting', 'natural'),
            composition=data.get('composition', 'centered')
        )


class PanelEditor:
    """Manage panel editing workflow"""
    
    def __init__(self):
        self.panels: List[PanelPrompt] = []
        self.current_panel = 0
    
    def create_panels_from_scenes(
        self,
        scenes: List[Dict],
        prompt_builder,
        character_library=None
    ) -> List[PanelPrompt]:
        """
        Create editable panels from scenes
        
        Args:
            scenes: List of scene dicts from text_processor
            prompt_builder: PromptBuilder instance
            character_library: Optional CharacterLibrary for character info
        """
        self.panels = []
        
        for idx, scene in enumerate(scenes):
            # Build initial prompt
            if hasattr(scene, 'to_dict'):
                scene_dict = scene.to_dict()
            else:
                scene_dict = scene
            
            scene_text = scene_dict.get('text', '')
            mood = scene_dict.get('mood', 'neutral')
            
            # Generate prompt
            prompt = prompt_builder.build(scene_text)
            
            # Add mood and quality tags
            if mood != 'neutral':
                prompt = f"{prompt}, {mood} atmosphere"
            
            # Create panel
            panel = PanelPrompt(
                panel_id=idx + 1,
                scene_text=scene_text,
                generated_prompt=prompt,
                mood=mood,
                negative_prompt="ugly, blurry, low quality, bad anatomy, worst quality"
            )
            
            # Auto-detect characters if library provided
            if character_library:
                for char in character_library.characters.values():
                    if char.name.lower() in scene_text.lower():
                        panel.character_ids.append(char.character_id)
            
            self.panels.append(panel)
        
        return self.panels
    
    def get_panel(self, panel_id: int) -> Optional[PanelPrompt]:
        """Get panel by ID"""
        for panel in self.panels:
            if panel.panel_id == panel_id:
                return panel
        return None
    
    def update_panel(
        self,
        panel_id: int,
        edited_prompt: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        character_ids: Optional[List[str]] = None,
        mood: Optional[str] = None,
        camera_angle: Optional[str] = None,
        lighting: Optional[str] = None,
        composition: Optional[str] = None
    ) -> bool:
        """Update panel settings"""
        panel = self.get_panel(panel_id)
        
        if not panel:
            return False
        
        if edited_prompt is not None:
            panel.edited_prompt = edited_prompt
        if negative_prompt is not None:
            panel.negative_prompt = negative_prompt
        if character_ids is not None:
            panel.character_ids = character_ids
        if mood is not None:
            panel.mood = mood
        if camera_angle is not None:
            panel.camera_angle = camera_angle
        if lighting is not None:
            panel.lighting = lighting
        if composition is not None:
            panel.composition = composition
        
        return True
    
    def reset_panel(self, panel_id: int) -> bool:
        """Reset panel to original generated prompt"""
        panel = self.get_panel(panel_id)
        
        if not panel:
            return False
        
        panel.edited_prompt = None
        return True
    
    def apply_style_preset(self, panel_id: int, style_name: str) -> bool:
        """Apply style preset to panel"""
        panel = self.get_panel(panel_id)
        
        if not panel:
            return False
        
        style_tags = {
            'manhwa': 'manhwa style, korean webtoon, digital art, vibrant colors',
            'manga': 'manga style, black and white, screentones, japanese comic',
            'anime': 'anime style, cel shading, vibrant, japanese animation',
            'realistic': 'photorealistic, detailed, cinematic lighting, realistic',
            'watercolor': 'watercolor painting, soft colors, artistic, painterly',
            'dark_fantasy': 'dark fantasy, gothic, dramatic lighting, mysterious',
            'chibi': 'chibi style, cute, super deformed, big eyes, kawaii',
            'western': 'western comic book style, bold lines, dynamic, marvel style'
        }
        
        style = style_tags.get(style_name, '')
        
        if style:
            current = panel.get_final_prompt()
            panel.edited_prompt = f"{current}, {style}"
            return True
        
        return False
    
    def get_all_panels_for_generation(self) -> List[Dict]:
        """Get all panels ready for generation"""
        return [
            {
                'panel_id': panel.panel_id,
                'prompt': panel.get_final_prompt(),
                'negative_prompt': panel.negative_prompt,
                'character_ids': panel.character_ids,
                'metadata': {
                    'scene_text': panel.scene_text,
                    'mood': panel.mood,
                    'camera_angle': panel.camera_angle,
                    'lighting': panel.lighting,
                    'composition': panel.composition
                }
            }
            for panel in self.panels
        ]
    
    def save(self, filepath: str):
        """Save panel configuration"""
        data = {
            'panels': [p.to_dict() for p in self.panels],
            'current_panel': self.current_panel
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filepath: str):
        """Load panel configuration"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.panels = [PanelPrompt.from_dict(p) for p in data['panels']]
        self.current_panel = data.get('current_panel', 0)


if __name__ == "__main__":
    # Test panel editor
    editor = PanelEditor()
    
    # Mock scenes
    scenes = [
        {
            'text': 'Elena stood at the cliff edge, silver hair flowing.',
            'mood': 'tense'
        },
        {
            'text': '"Are you ready?" Marcus asked.',
            'mood': 'neutral'
        }
    ]
    
    # Mock prompt builder
    class MockPromptBuilder:
        def build(self, text):
            return f"masterpiece, {text[:30]}"
    
    builder = MockPromptBuilder()
    
    panels = editor.create_panels_from_scenes(scenes, builder)
    
    print(f"Created {len(panels)} panels")
    for panel in panels:
        print(f"\nPanel {panel.panel_id}:")
        print(f"  Scene: {panel.scene_text[:50]}...")
        print(f"  Prompt: {panel.generated_prompt}")
        print(f"  Mood: {panel.mood}")
    
    # Edit panel
    editor.update_panel(
        1,
        edited_prompt="epic warrior woman on cliff, dramatic sunset",
        camera_angle="wide shot"
    )
    
    print(f"\nEdited Panel 1:")
    print(f"  New Prompt: {editor.get_panel(1).get_final_prompt()}")
    
    # Get generation data
    gen_data = editor.get_all_panels_for_generation()
    print(f"\nGeneration Data:")
    for item in gen_data:
        print(f"  Panel {item['panel_id']}: {item['prompt'][:50]}...")
