"""
Post-processing and panel composition utilities
"""
from PIL import Image
from pathlib import Path
from typing import List, Tuple
import json

from config import FRAMES_DIR, OUTPUT_DIR

class PostProcessor:
    """Handle post-processing of generated panels"""
    
    @staticmethod
    def create_vertical_preview(
        panel_dir: Path = FRAMES_DIR,
        output_path: Path = None,
        max_width: int = 1080
    ) -> Path:
        """
        Combine all panels into a single vertical scrolling image
        
        Args:
            panel_dir: Directory containing panel images
            output_path: Where to save preview (default: output/vertical_preview.png)
            max_width: Maximum width for preview
            
        Returns:
            Path to saved preview image
        """
        if output_path is None:
            output_path = OUTPUT_DIR / "vertical_preview.png"
        
        # Get all panel images sorted by name
        panel_files = sorted(panel_dir.glob("panel_*.png"))
        
        if not panel_files:
            print("⚠ No panels found to create preview")
            return None
        
        print(f"\nCreating vertical preview from {len(panel_files)} panels...")
        
        # Load all images
        images = [Image.open(f) for f in panel_files]
        
        # Calculate dimensions
        widths, heights = zip(*(img.size for img in images))
        
        # Scale if needed
        if max(widths) > max_width:
            scale_factor = max_width / max(widths)
            images = [
                img.resize(
                    (int(img.width * scale_factor), int(img.height * scale_factor)),
                    Image.Resampling.LANCZOS
                )
                for img in images
            ]
            widths, heights = zip(*(img.size for img in images))
        
        # Create canvas
        total_height = sum(heights)
        canvas_width = max(widths)
        
        preview = Image.new('RGB', (canvas_width, total_height), (255, 255, 255))
        
        # Paste panels
        current_y = 0
        for img in images:
            # Center horizontally if image is narrower than canvas
            x_offset = (canvas_width - img.width) // 2
            preview.paste(img, (x_offset, current_y))
            current_y += img.height
        
        # Save
        preview.save(output_path, "PNG", optimize=True)
        print(f"✓ Saved vertical preview: {output_path}")
        print(f"  Dimensions: {canvas_width}x{total_height}px")
        
        return output_path
    
    @staticmethod
    def create_thumbnail(
        image_path: Path,
        size: Tuple[int, int] = (270, 480)
    ) -> Image.Image:
        """
        Create a thumbnail of a panel
        
        Args:
            image_path: Path to source image
            size: Thumbnail size (width, height)
            
        Returns:
            PIL Image thumbnail
        """
        img = Image.open(image_path)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        return img
    
    @staticmethod
    def add_metadata(
        image_path: Path,
        metadata: dict
    ):
        """
        Add metadata to an image file
        
        Args:
            image_path: Path to image
            metadata: Dictionary of metadata to add
        """
        # Save metadata as JSON sidecar
        json_path = image_path.with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def create_grid(
        images: List[Image.Image],
        cols: int = 3,
        output_path: Path = None
    ) -> Path:
        """
        Create a grid layout of panels
        
        Args:
            images: List of PIL Images
            cols: Number of columns
            output_path: Where to save grid
            
        Returns:
            Path to saved grid image
        """
        if output_path is None:
            output_path = OUTPUT_DIR / "panel_grid.png"
        
        if not images:
            return None
        
        # Calculate grid dimensions
        rows = (len(images) + cols - 1) // cols
        
        # Get max dimensions
        max_width = max(img.width for img in images)
        max_height = max(img.height for img in images)
        
        # Create canvas
        grid_width = max_width * cols
        grid_height = max_height * rows
        
        grid = Image.new('RGB', (grid_width, grid_height), (240, 240, 240))
        
        # Place images
        for idx, img in enumerate(images):
            row = idx // cols
            col = idx % cols
            
            x = col * max_width
            y = row * max_height
            
            # Center image in cell
            x_offset = (max_width - img.width) // 2
            y_offset = (max_height - img.height) // 2
            
            grid.paste(img, (x + x_offset, y + y_offset))
        
        grid.save(output_path, "PNG", optimize=True)
        print(f"✓ Saved grid: {output_path}")
        
        return output_path


# ============================================================================
# USAGE EXAMPLE
# ============================================================================
if __name__ == "__main__":
    # Test vertical preview creation
    processor = PostProcessor()
    
    # This will work after you've generated some panels
    # processor.create_vertical_preview()
    
    print("PostProcessor ready. Generate panels first, then run create_vertical_preview()")
