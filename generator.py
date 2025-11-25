"""
Image generation pipeline using Stable Diffusion
"""
# Lightweight imports only
from PIL import Image
from pathlib import Path
from typing import Optional, List, Tuple, Callable
import gc

# Heavy ML imports moved to load_pipeline() for lazy loading
# This prevents 30-60 second startup delay

from config import (
    DEVICE, DTYPE, get_model_path,
    PANEL_WIDTH, PANEL_HEIGHT, DRAFT_WIDTH, DRAFT_HEIGHT,
    NUM_INFERENCE_STEPS, GUIDANCE_SCALE, DRAFT_STEPS,
    ENABLE_ATTENTION_SLICING, ENABLE_VAE_SLICING,
    FRAMES_DIR
)

class ManhwaGenerator:
    """Manages the Stable Diffusion pipeline for manhwa panel generation"""
    
    def __init__(self, draft_mode: bool = False):
        self.pipeline = None
        self.draft_mode = draft_mode
        
        # Use lazy device detection
        from config import get_device, get_dtype
        self.device = get_device()
        self.dtype = get_dtype()
        
        # Set dimensions based on mode
        if draft_mode:
            self.width = DRAFT_WIDTH
            self.height = DRAFT_HEIGHT
            self.steps = DRAFT_STEPS
        else:
            self.width = PANEL_WIDTH
            self.height = PANEL_HEIGHT
            self.steps = NUM_INFERENCE_STEPS
        
        print(f"Initializing generator: {self.width}x{self.height}, {self.steps} steps")
    
    def load_pipeline(self):
        """
        Load and configure the Stable Diffusion pipeline
        """
        # Lazy import heavy ML libraries only when needed
        import torch
        from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
        from tqdm import tqdm
        
        print(f"\nLoading model on {self.device}...")
        model_path = get_model_path()
        
        try:
            # Load pipeline
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                model_path,
                torch_dtype=self.dtype,
                safety_checker=None,  # Disable for speed
                requires_safety_checker=False
            )
            
            # Move to device
            self.pipeline = self.pipeline.to(self.device)
            
            # Optimize for memory
            if ENABLE_ATTENTION_SLICING:
                self.pipeline.enable_attention_slicing()
                print("[OK] Enabled attention slicing")
            
            if ENABLE_VAE_SLICING:
                self.pipeline.enable_vae_slicing()
                print("[OK] Enabled VAE slicing")
            
            # Use faster scheduler
            self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipeline.scheduler.config
            )
            print("[OK] Using DPM++ scheduler")
            
            print(f"[OK] Pipeline loaded successfully on {self.device}")
            
        except Exception as e:
            print(f"[ERROR] Failed to load pipeline: {e}")
            print("\nTroubleshooting:")
            print("1. Make sure you have downloaded a Stable Diffusion model")
            print("2. Check your GPU drivers if using CUDA")
            print("3. Try setting USE_LOCAL_MODEL = False in config.py to auto-download")
            raise
    
    def generate_panel(
        self,
        prompt: str,
        negative_prompt: str,
        seed: Optional[int] = None,
        progress_callback: Optional[Callable] = None
    ) -> Image.Image:
        """
        Generate a single manhwa panel
        
        Args:
            prompt: Positive prompt
            negative_prompt: Negative prompt
            seed: Random seed for reproducibility
            progress_callback: Optional callback for progress updates
            
        Returns:
            Generated PIL Image
        """
        if self.pipeline is None:
            raise RuntimeError("Pipeline not loaded. Call load_pipeline() first.")
        
        import torch  # Lazy import
        
        # Set seed if provided
        generator = None
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        
        # Generate
        with torch.inference_mode():
            output = self.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=self.width,
                height=self.height,
                num_inference_steps=self.steps,
                guidance_scale=GUIDANCE_SCALE,
                generator=generator,
                callback=progress_callback
            )
        
        image = output.images[0]
        
        # Clear cache
        if self.device == "cuda":
            torch.cuda.empty_cache()
        
        return image
    
    def batch_generate(
        self,
        prompts: List[Tuple[str, str]],
        output_dir: Optional[Path] = None,
        save_prompts: bool = True,
        seed: Optional[int] = None
    ) -> List[Image.Image]:
        """
        Generate multiple panels in sequence
        
        Args:
            prompts: List of (positive, negative) prompt tuples
            output_dir: Directory to save images (if None, returns only)
            save_prompts: Whether to save prompt text files
            seed: Base seed (incremented for each image)
            
        Returns:
            List of generated images
        """
        if output_dir is None:
            output_dir = FRAMES_DIR
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        images = []
        
        print(f"\nGenerating {len(prompts)} panels...")
        
        for idx, (positive, negative) in enumerate(tqdm(prompts, desc="Generating")):
            # Calculate seed
            current_seed = seed + idx if seed else None
            
            # Generate
            print(f"\nPanel {idx + 1}/{len(prompts)}")
            print(f"Prompt: {positive[:100]}...")
            
            image = self.generate_panel(positive, negative, current_seed)
            images.append(image)
            
            # Save image
            img_path = output_dir / f"panel_{idx+1:03d}.png"
            image.save(img_path, "PNG", optimize=True)
            print(f"[OK] Saved: {img_path}")
            
            # Save prompt
            if save_prompts:
                from config import PROMPTS_DIR
                PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
                
                prompt_path = PROMPTS_DIR / f"panel_{idx+1:03d}_prompt.txt"
                with open(prompt_path, 'w', encoding='utf-8') as f:
                    f.write(f"POSITIVE PROMPT:\n{positive}\n\n")
                    f.write(f"NEGATIVE PROMPT:\n{negative}\n\n")
                    f.write(f"SEED: {current_seed}\n")
                    f.write(f"SIZE: {self.width}x{self.height}\n")
                    f.write(f"STEPS: {self.steps}\n")
        
        print(f"\n[OK] Generated {len(images)} panels")
        return images
    
    def unload(self):
        """Unload pipeline to free memory"""
        if self.pipeline is not None:
            del self.pipeline
            self.pipeline = None
            
            if self.device == "cuda":
                import torch  # Lazy import
                torch.cuda.empty_cache()
            
            gc.collect()
            print("[OK] Pipeline unloaded")


# ============================================================================
# USAGE EXAMPLE
# ============================================================================
if __name__ == "__main__":
    # Test the generator
    generator = ManhwaGenerator(draft_mode=True)
    
    try:
        generator.load_pipeline()
        
        # Test prompt
        prompt = (
            "Korean manhwa webtoon style, clean lineart, full color, highly detailed, "
            "young woman with long silver hair, bright blue eyes, wearing elegant black dress, "
            "standing on cliff edge, dramatic lighting, vertical webtoon panel, "
            "masterpiece, best quality"
        )
        
        negative = (
            "low quality, blurry, distorted, deformed, ugly, bad anatomy, "
            "bad proportions, watermark, text"
        )
        
        print("\nGenerating test panel...")
        image = generator.generate_panel(prompt, negative, seed=42)
        
        test_output = Path("test_panel.png")
        image.save(test_output)
        print(f"[OK] Test panel saved: {test_output}")
        
    except Exception as e:
        print(f"Test failed: {e}")
    
    finally:
        generator.unload()
