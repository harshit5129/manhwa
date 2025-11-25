"""
Export utilities for different formats
"""
from PIL import Image
from pathlib import Path
from typing import List
import zipfile
import shutil

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠ ReportLab not available - PDF export disabled")


class Exporter:
    """Export panels to various formats"""
    
    def __init__(self):
        self.pdf_available = REPORTLAB_AVAILABLE
    
    def export_pdf(
        self,
        panel_dir: Path,
        output_path: Path,
        page_size: tuple = None
    ):
        """
        Export panels as PDF
        
        Args:
            panel_dir: Directory with panels
            output_path: Output PDF file
            page_size: (width, height) or None for auto
        """
        if not self.pdf_available:
            print("✗ PDF export requires reportlab: pip install reportlab")
            return False
        
        panels = sorted(panel_dir.glob("panel_*.png"))
        
        if not panels:
            print("✗ No panels found")
            return False
        
        # Create PDF
        c = canvas.Canvas(str(output_path))
        
        for panel_path in panels:
            img = Image.open(panel_path)
            
            # Determine page size
            if page_size is None:
                # Use panel size
                page_w, page_h = img.size
            else:
                page_w, page_h = page_size
            
            c.setPageSize((page_w, page_h))
            
            # Add image to page
            c.drawImage(
                str(panel_path),
                0, 0,
                width=page_w,
                height=page_h,
                preserveAspectRatio=True
            )
            
            c.showPage()
        
        c.save()
        print(f"✓ PDF saved: {output_path}")
        return True
    
    def export_cbz(
        self,
        panel_dir: Path,
        output_path: Path,
        metadata: dict = None
    ):
        """
        Export as CBZ (Comic Book ZIP)
        
        CBZ is just a ZIP file with images in reading order
        """
        panels = sorted(panel_dir.glob("panel_*.png"))
        
        if not panels:
            print("✗ No panels found")
            return False
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as cbz:
            for idx, panel in enumerate(panels):
                # Rename with zero-padded numbers for proper ordering
                arcname = f"{idx+1:04d}.png"
                cbz.write(panel, arcname)
            
            # Add metadata if provided
            if metadata:
                import json
                cbz.writestr("metadata.json", json.dumps(metadata, indent=2))
        
        print(f"✓ CBZ saved: {output_path}")
        return True
    
    def export_vertical_scroll(
        self,
        panel_dir: Path,
        output_path: Path,
        spacing: int = 0,
        background_color: tuple = (255, 255, 255)
    ):
        """
        Create single vertical scroll image (perfect for webtoons)
        """
        panels = sorted(panel_dir.glob("panel_*.png"))
        
        if not panels:
            print("✗ No panels found")
            return False
        
        # Load all images
        images = [Image.open(p) for p in panels]
        
        # Calculate total size
        max_width = max(img.width for img in images)
        total_height = sum(img.height for img in images) + (spacing * (len(images) - 1))
        
        # Create canvas
        scroll = Image.new('RGB', (max_width, total_height), background_color)
        
        # Paste panels
        current_y = 0
        for img in images:
            # Center horizontally if image is narrower
            x_offset = (max_width - img.width) // 2
            scroll.paste(img, (x_offset, current_y))
            current_y += img.height + spacing
        
        # Save
        scroll.save(output_path, "PNG", optimize=True)
        print(f"✓ Vertical scroll saved: {output_path}")
        print(f"  Size: {max_width}x{total_height}px")
        return True
    
    def export_video(
        self,
        panel_dir: Path,
        output_path: Path,
        duration_per_panel: float = 3.0,
        fps: int = 30
    ):
        """
        Export as video (vertical scroll animation)
        
        Requires opencv-python
        """
        try:
            import cv2
        except ImportError:
            print("✗ Video export requires opencv-python")
            return False
        
        panels = sorted(panel_dir.glob("panel_*.png"))
        
        if not panels:
            print("✗ No panels found")
            return False
        
        # Load first panel to get dimensions
        first_img = cv2.imread(str(panels[0]))
        height, width = first_img.shape[:2]
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(
            str(output_path),
            fourcc,
            fps,
            (width, height)
        )
        
        # Add each panel for specified duration
        frames_per_panel = int(duration_per_panel * fps)
        
        for panel_path in panels:
            frame = cv2.imread(str(panel_path))
            
            # Write frame multiple times for duration
            for _ in range(frames_per_panel):
                video.write(frame)
        
        video.release()
        print(f"✓ Video saved: {output_path}")
        return True
    
    def export_social_media(
        self,
        panel_dir: Path,
        output_dir: Path,
        platform: str = "instagram"
    ):
        """
        Export optimized for social media platforms
        
        Platforms: instagram, tiktok, youtube_shorts
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        panels = sorted(panel_dir.glob("panel_*.png"))
        
        # Platform specs
        specs = {
            "instagram": {"width": 1080, "height": 1920, "format": "PNG"},
            "tiktok": {"width": 1080, "height": 1920, "format": "PNG"},
            "youtube_shorts": {"width": 1080, "height": 1920, "format": "PNG"},
            "twitter": {"width": 1200, "height": 675, "format": "PNG"}
        }
        
        spec = specs.get(platform, specs["instagram"])
        
        for idx, panel_path in enumerate(panels):
            img = Image.open(panel_path)
            
            # Resize to platform specs (maintaining aspect ratio)
            img.thumbnail((spec["width"], spec["height"]), Image.Resampling.LANCZOS)
            
            # Create canvas with platform size
            canvas = Image.new('RGB', (spec["width"], spec["height"]), (0, 0, 0))
            
            # Center image
            x_offset = (spec["width"] - img.width) // 2
            y_offset = (spec["height"] - img.height) // 2
            canvas.paste(img, (x_offset, y_offset))
            
            # Save
            output_file = output_dir / f"{platform}_{idx+1:03d}.{spec['format'].lower()}"
            canvas.save(output_file, spec["format"], optimize=True)
        
        print(f"✓ Exported {len(panels)} panels for {platform}")
        print(f"  Location: {output_dir}")
        return True


# Global instance
exporter = Exporter()


# ============================================================================
# USAGE EXAMPLE
# ============================================================================
if __name__ == "__main__":
    from config import FRAMES_DIR, OUTPUT_DIR
    
    if FRAMES_DIR.exists() and list(FRAMES_DIR.glob("*.png")):
        print("Testing exporters...\n")
        
        # Export vertical scroll
        print("1. Creating vertical scroll...")
        exporter.export_vertical_scroll(
            FRAMES_DIR,
            OUTPUT_DIR / "vertical_scroll.png"
        )
        
        # Export CBZ
        print("\n2. Creating CBZ...")
        exporter.export_cbz(
            FRAMES_DIR,
            OUTPUT_DIR / "manhwa.cbz"
        )
        
        # Export PDF (if available)
        if exporter.pdf_available:
            print("\n3. Creating PDF...")
            exporter.export_pdf(
                FRAMES_DIR,
                OUTPUT_DIR / "manhwa.pdf"
            )
        
        print("\n✓ All exports complete!")
    else:
        print("No panels found. Generate some first.")
