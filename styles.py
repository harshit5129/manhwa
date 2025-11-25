"""
Style presets and customization system
"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class StylePreset:
    """Art style configuration"""
    name: str
    description: str
    base_prompt: str
    negative_prompt: str
    color_palette: str
    characteristics: List[str]
    cfg_scale: float = 7.5
    steps: int = 30


# ============================================================================
# PREDEFINED STYLE PRESETS
# ============================================================================

STYLE_PRESETS = {
    "manhwa": StylePreset(
        name="Korean Manhwa",
        description="Modern Korean webtoon style with clean lineart and vibrant colors",
        base_prompt="Korean manhwa webtoon style, clean lineart, full color, highly detailed, professional digital art, vibrant colors, smooth shading",
        negative_prompt="sketch, rough, messy lines, washed out colors, ugly, deformed",
        color_palette="vibrant, saturated, high contrast",
        characteristics=["clean lines", "cel shading", "detailed eyes", "modern fashion"],
        cfg_scale=7.5,
        steps=30
    ),
    
    "manga": StylePreset(
        name="Japanese Manga",
        description="Traditional Japanese manga style with screentones",
        base_prompt="Japanese manga style, detailed lineart, screentones, black and white, dynamic composition, professional manga art",
        negative_prompt="color, messy, low quality, blurry",
        color_palette="monochrome, grayscale",
        characteristics=["screentones", "speed lines", "dramatic angles", "expressive faces"],
        cfg_scale=8.0,
        steps=30
    ),
    
    "anime": StylePreset(
        name="Anime Style",
        description="Japanese anime aesthetic with soft colors",
        base_prompt="anime style, soft cel shading, pastel colors, large expressive eyes, detailed hair, anime art",
        negative_prompt="realistic, photo, western style, ugly",
        color_palette="soft, pastel, harmonious",
        characteristics=["large eyes", "colorful hair", "soft shading", "kawaii"],
        cfg_scale=7.0,
        steps=25
    ),
    
    "realistic": StylePreset(
        name="Semi-Realistic",
        description="Realistic style with artistic touches",
        base_prompt="semi-realistic digital art, detailed rendering, realistic proportions, professional illustration, painterly style",
        negative_prompt="cartoon, anime, low quality, bad anatomy",
        color_palette="natural, realistic lighting",
        characteristics=["realistic proportions", "detailed textures", "natural lighting", "painterly"],
        cfg_scale=8.5,
        steps=40
    ),
    
    "watercolor": StylePreset(
        name="Watercolor",
        description="Soft watercolor painting style",
        base_prompt="watercolor painting style, soft edges, flowing colors, artistic, dreamy atmosphere, traditional art",
        negative_prompt="digital, harsh lines, flat colors, low quality",
        color_palette="soft, flowing, transparent",
        characteristics=["soft edges", "color bleeding", "paper texture", "gentle"],
        cfg_scale=6.5,
        steps=35
    ),
    
    "dark": StylePreset(
        name="Dark Fantasy",
        description="Dark, moody aesthetic for dramatic scenes",
        base_prompt="dark fantasy art style, dramatic shadows, moody lighting, detailed lineart, gothic atmosphere, professional dark art",
        negative_prompt="bright, cheerful, light colors, low quality",
        color_palette="dark, desaturated, high contrast",
        characteristics=["heavy shadows", "dramatic lighting", "gothic elements", "intense mood"],
        cfg_scale=9.0,
        steps=35
    ),
    
    "chibi": StylePreset(
        name="Chibi/Cute",
        description="Super deformed cute style",
        base_prompt="chibi style, cute, super deformed proportions, kawaii, bright colors, simple but detailed, adorable",
        negative_prompt="realistic, serious, dark, low quality",
        color_palette="bright, cheerful, pastel",
        characteristics=["big head", "small body", "cute expressions", "simple details"],
        cfg_scale=6.0,
        steps=25
    ),
    
    "comic": StylePreset(
        name="Western Comic",
        description="American comic book style",
        base_prompt="western comic book style, bold lineart, dynamic poses, halftone shading, professional comic art, action-packed",
        negative_prompt="anime, manga, low quality, static",
        color_palette="bold, primary colors, high contrast",
        characteristics=["bold lines", "dynamic action", "halftones", "muscular proportions"],
        cfg_scale=8.0,
        steps=30
    )
}


class StyleManager:
    """Manage and apply style presets"""
    
    def __init__(self):
        self.presets = STYLE_PRESETS
        self.current_style = "manhwa"
    
    def get_style(self, style_name: str) -> StylePreset:
        """Get a style preset by name"""
        return self.presets.get(style_name, self.presets["manhwa"])
    
    def list_styles(self) -> List[str]:
        """Get list of available style names"""
        return list(self.presets.keys())
    
    def get_style_descriptions(self) -> Dict[str, str]:
        """Get dictionary of style names and descriptions"""
        return {name: preset.description for name, preset in self.presets.items()}
    
    def apply_style_to_prompt(
        self, 
        base_scene_prompt: str, 
        style_name: str = "manhwa"
    ) -> tuple:
        """
        Apply style to a scene prompt
        
        Returns:
            (enhanced_prompt, negative_prompt, cfg_scale, steps)
        """
        style = self.get_style(style_name)
        
        # Combine style base with scene
        enhanced = f"{style.base_prompt}, {base_scene_prompt}"
        
        return (
            enhanced,
            style.negative_prompt,
            style.cfg_scale,
            style.steps
        )
    
    def mix_styles(
        self, 
        style1: str, 
        style2: str, 
        ratio: float = 0.5
    ) -> StylePreset:
        """
        Mix two styles
        
        Args:
            style1: First style name
            style2: Second style name
            ratio: 0.0 = all style1, 1.0 = all style2
            
        Returns:
            Mixed StylePreset
        """
        s1 = self.get_style(style1)
        s2 = self.get_style(style2)
        
        # Mix prompts
        mixed_prompt = f"{s1.base_prompt}, {s2.base_prompt}"
        mixed_negative = f"{s1.negative_prompt}, {s2.negative_prompt}"
        
        # Interpolate numerical values
        mixed_cfg = s1.cfg_scale * (1 - ratio) + s2.cfg_scale * ratio
        mixed_steps = int(s1.steps * (1 - ratio) + s2.steps * ratio)
        
        return StylePreset(
            name=f"{s1.name}/{s2.name} Mix",
            description=f"Blend of {s1.name} and {s2.name}",
            base_prompt=mixed_prompt,
            negative_prompt=mixed_negative,
            color_palette=f"{s1.color_palette} + {s2.color_palette}",
            characteristics=s1.characteristics + s2.characteristics,
            cfg_scale=mixed_cfg,
            steps=mixed_steps
        )


# Global instance
style_manager = StyleManager()


# ============================================================================
# COLOR PALETTES
# ============================================================================

COLOR_PALETTES = {
    "warm": "warm colors, orange, red, yellow tones, cozy atmosphere",
    "cool": "cool colors, blue, cyan, purple tones, calm atmosphere",
    "vibrant": "vibrant saturated colors, high energy, eye-catching",
    "muted": "muted desaturated colors, subtle, professional",
    "pastel": "soft pastel colors, gentle, dreamy",
    "neon": "neon colors, glowing, cyberpunk aesthetic",
    "monochrome": "black and white, grayscale, classic",
    "earthy": "earthy natural colors, browns, greens, organic"
}


def apply_color_palette(prompt: str, palette: str) -> str:
    """Add color palette to prompt"""
    if palette in COLOR_PALETTES:
        return f"{prompt}, {COLOR_PALETTES[palette]}"
    return prompt


# ============================================================================
# USAGE EXAMPLE
# ============================================================================
if __name__ == "__main__":
    manager = StyleManager()
    
    print("Available Styles:")
    print("=" * 60)
    for name, desc in manager.get_style_descriptions().items():
        print(f"• {name}: {desc}")
    
    print("\n\nStyle Application Example:")
    print("=" * 60)
    
    scene = "warrior standing on mountain peak at sunset"
    
    prompt, neg, cfg, steps = manager.apply_style_to_prompt(scene, "manhwa")
    print(f"\nManhwa Style:")
    print(f"Prompt: {prompt[:100]}...")
    print(f"CFG: {cfg}, Steps: {steps}")
    
    prompt, neg, cfg, steps = manager.apply_style_to_prompt(scene, "realistic")
    print(f"\nRealistic Style:")
    print(f"Prompt: {prompt[:100]}...")
    print(f"CFG: {cfg}, Steps: {steps}")
