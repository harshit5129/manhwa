"""
Image upscaling and enhancement utilities
"""
from PIL import Image
import numpy as np
from pathlib import Path
from typing import Tuple

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠ OpenCV not available - some upscaling features disabled")


class ImageUpscaler:
    """Upscale and enhance generated panels"""
    
    def __init__(self):
        self.cv2_available = CV2_AVAILABLE
    
    def upscale_simple(
        self, 
        image: Image.Image, 
        scale: int = 2
    ) -> Image.Image:
        """
        Simple high-quality upscaling using Lanczos resampling
        
        Args:
            image: PIL Image
            scale: Upscale factor (2x, 4x, etc.)
            
        Returns:
            Upscaled PIL Image
        """
        new_size = (image.width * scale, image.height * scale)
        upscaled = image.resize(new_size, Image.Resampling.LANCZOS)
        return upscaled
    
    def upscale_opencv(
        self,
        image: Image.Image,
        scale: int = 2,
        method: str = "bicubic"
    ) -> Image.Image:
        """
        Upscale using OpenCV interpolation methods
        
        Methods: nearest, bilinear, bicubic, lanczos
        """
        if not self.cv2_available:
            return self.upscale_simple(image, scale)
        
        # Convert PIL to numpy
        img_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        if len(img_array.shape) == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Choose interpolation method
        interpolation = {
            "nearest": cv2.INTER_NEAREST,
            "bilinear": cv2.INTER_LINEAR,
            "bicubic": cv2.INTER_CUBIC,
            "lanczos": cv2.INTER_LANCZOS4
        }.get(method, cv2.INTER_CUBIC)
        
        # Calculate new size
        new_size = (image.width * scale, image.height * scale)
        
        # Upscale
        upscaled = cv2.resize(img_array, new_size, interpolation=interpolation)
        
        # Convert back to RGB
        if len(upscaled.shape) == 3:
            upscaled = cv2.cvtColor(upscaled, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL
        return Image.fromarray(upscaled)
    
    def sharpen(self, image: Image.Image, amount: float = 1.5) -> Image.Image:
        """
        Sharpen image after upscaling
        
        Args:
            image: PIL Image
            amount: Sharpening strength (1.0-3.0)
        """
        from PIL import ImageEnhance
        
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(amount)
    
    def enhance_quality(
        self,
        image: Image.Image,
        brightness: float = 1.0,
        contrast: float = 1.1,
        saturation: float = 1.1
    ) -> Image.Image:
        """
        Enhance image quality with multiple adjustments
        """
        from PIL import ImageEnhance
        
        # Brightness
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness)
        
        # Contrast
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
        
        # Color saturation
        if saturation != 1.0:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(saturation)
        
        return image
    
    def upscale_and_enhance(
        self,
        image: Image.Image,
        scale: int = 2,
        sharpen: bool = True,
        enhance: bool = True
    ) -> Image.Image:
        """
        Complete upscaling and enhancement pipeline
        """
        # Upscale
        if self.cv2_available:
            upscaled = self.upscale_opencv(image, scale, "lanczos")
        else:
            upscaled = self.upscale_simple(image, scale)
        
        # Sharpen
        if sharpen:
            upscaled = self.sharpen(upscaled, 1.3)
        
        # Enhance quality
        if enhance:
            upscaled = self.enhance_quality(
                upscaled,
                brightness=1.0,
                contrast=1.1,
                saturation=1.05
            )
        
        return upscaled
    
    def batch_upscale(
        self,
        input_dir: Path,
        output_dir: Path,
        scale: int = 2,
        pattern: str = "*.png"
    ):
        """
        Upscale all images in a directory
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        images = list(input_dir.glob(pattern))
        print(f"Upscaling {len(images)} images...")
        
        for img_path in images:
            print(f"  Processing {img_path.name}...")
            
            img = Image.open(img_path)
            upscaled = self.upscale_and_enhance(img, scale)
            
            output_path = output_dir / img_path.name
            upscaled.save(output_path, "PNG", optimize=True)
        
        print(f"✓ Done! Saved to {output_dir}")


# Global instance
upscaler = ImageUpscaler()


# ============================================================================
# USAGE EXAMPLE
# ============================================================================
if __name__ == "__main__":
    from config import FRAMES_DIR, OUTPUT_DIR
    
    # Test upscaling
    test_dir = FRAMES_DIR
    
    if test_dir.exists() and list(test_dir.glob("*.png")):
        print("Testing upscaler...")
        
        # Upscale first panel
        panels = list(test_dir.glob("panel_*.png"))
        if panels:
            img = Image.open(panels[0])
            print(f"Original size: {img.size}")
            
            upscaled = upscaler.upscale_and_enhance(img, scale=2)
            print(f"Upscaled size: {upscaled.size}")
            
            # Save test
            upscaled.save(OUTPUT_DIR / "test_upscaled.png")
            print(f"✓ Saved test to {OUTPUT_DIR / 'test_upscaled.png'}")
    else:
        print("No panels found. Generate some panels first.")
