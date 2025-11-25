"""
Bundle output files into a distributable ZIP package
"""
import shutil
from pathlib import Path
from datetime import datetime
import json

from config import OUTPUT_DIR, FRAMES_DIR, PROMPTS_DIR, REFERENCE_DIR, BUNDLE_NAME

class Bundler:
    """Create ZIP bundles of generated manhwa content"""
    
    def __init__(self, output_dir: Path = OUTPUT_DIR):
        self.output_dir = Path(output_dir)
        self.bundle_path = self.output_dir / BUNDLE_NAME
    
    def create_bundle(
        self,
        include_prompts: bool = True,
        include_reference: bool = True,
        include_preview: bool = True
    ) -> Path:
        """
        Create a ZIP bundle of all output files
        
        Args:
            include_prompts: Include prompt text files
            include_reference: Include reference images
            include_preview: Include vertical preview
            
        Returns:
            Path to created ZIP file
        """
        print("\nCreating manhwa bundle...")
        
        # Collect files to bundle
        files_to_bundle = []
        
        # 1. Panel images (required)
        panel_files = list(FRAMES_DIR.glob("*.png"))
        if not panel_files:
            print("⚠ No panels found. Generate panels first.")
            return None
        
        files_to_bundle.extend(panel_files)
        print(f"  Adding {len(panel_files)} panels")
        
        # 2. Prompts
        if include_prompts and PROMPTS_DIR.exists():
            prompt_files = list(PROMPTS_DIR.glob("*.txt"))
            files_to_bundle.extend(prompt_files)
            print(f"  Adding {len(prompt_files)} prompts")
        
        # 3. Reference images
        if include_reference and REFERENCE_DIR.exists():
            ref_files = list(REFERENCE_DIR.glob("*"))
            files_to_bundle.extend(ref_files)
            print(f"  Adding {len(ref_files)} reference files")
        
        # 4. Vertical preview
        preview_path = self.output_dir / "vertical_preview.png"
        if include_preview and preview_path.exists():
            files_to_bundle.append(preview_path)
            print("  Adding vertical preview")
        
        # 5. Create README for bundle
        readme_path = self.output_dir / "BUNDLE_README.txt"
        self._create_bundle_readme(readme_path, len(panel_files))
        files_to_bundle.append(readme_path)
        
        # 6. Create metadata
        metadata_path = self.output_dir / "metadata.json"
        self._create_metadata(metadata_path, len(panel_files))
        files_to_bundle.append(metadata_path)
        
        # Create ZIP archive
        # Remove .zip extension as make_archive adds it
        base_name = str(self.bundle_path.with_suffix(''))
        
        print(f"\nPacking {len(files_to_bundle)} files...")
        
        # Create temporary directory structure
        temp_dir = self.output_dir / "temp_bundle"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Copy files with proper structure
            for file in files_to_bundle:
                rel_path = file.relative_to(self.output_dir)
                dest = temp_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, dest)
            
            # Create archive
            shutil.make_archive(base_name, 'zip', temp_dir)
            
            # Clean up temp
            shutil.rmtree(temp_dir)
            
            print(f"✓ Bundle created: {self.bundle_path}")
            print(f"  Size: {self.bundle_path.stat().st_size / 1024 / 1024:.1f} MB")
            
            return self.bundle_path
            
        except Exception as e:
            print(f"✗ Failed to create bundle: {e}")
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            return None
    
    def _create_bundle_readme(self, path: Path, num_panels: int):
        """Create README file for the bundle"""
        content = f"""
╔══════════════════════════════════════════════════════════════╗
║         MANHWA AUTO-PANEL GENERATOR - Output Bundle         ║
╚══════════════════════════════════════════════════════════════╝

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total Panels: {num_panels}

═══════════════════════════════════════════════════════════════

CONTENTS:

📁 frames/
   - panel_001.png, panel_002.png, etc.
   - Individual manhwa panels in vertical format
   - Size: 1080×1920px (or draft size)

📁 prompts/
   - panel_001_prompt.txt, panel_002_prompt.txt, etc.
   - Text prompts used to generate each panel
   - Includes positive/negative prompts and settings

📁 reference/
   - Character reference images used for consistency
   - Original files copied for your records

📄 vertical_preview.png
   - All panels stitched into a single scrollable image
   - Use this to preview the full chapter flow

📄 metadata.json
   - Generation parameters and settings
   - Timestamps and configuration used

═══════════════════════════════════════════════════════════════

USAGE TIPS:

1. Upload panels to webtoon platforms in sequence
2. Use vertical_preview.png for quick review
3. Check prompts/ to see what worked well
4. Save reference/ images for future chapters

═══════════════════════════════════════════════════════════════

EDITING:

If you want to regenerate specific panels:
1. Check the prompt file for that panel
2. Modify the scene text or character description
3. Re-run the generator for just that scene

═══════════════════════════════════════════════════════════════

Generated by Manhwa Auto-Panel Generator
https://github.com/yourusername/manhwa-generator

"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_metadata(self, path: Path, num_panels: int):
        """Create metadata JSON file"""
        from config import (
            MODEL_ID, PANEL_WIDTH, PANEL_HEIGHT,
            NUM_INFERENCE_STEPS, GUIDANCE_SCALE
        )
        
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "generator_version": "1.0.0",
            "num_panels": num_panels,
            "settings": {
                "model": MODEL_ID,
                "panel_size": f"{PANEL_WIDTH}x{PANEL_HEIGHT}",
                "inference_steps": NUM_INFERENCE_STEPS,
                "guidance_scale": GUIDANCE_SCALE
            }
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)


# ============================================================================
# USAGE EXAMPLE
# ============================================================================
if __name__ == "__main__":
    bundler = Bundler()
    bundler.create_bundle()
