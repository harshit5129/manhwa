"""
Configuration settings for Manhwa Auto-Panel Generator
"""
import os
from pathlib import Path

# ============================================================================
# PROJECT PATHS
# ============================================================================
PROJECT_ROOT = Path(__file__).parent
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUT_DIR = PROJECT_ROOT / "output"
EXAMPLES_DIR = PROJECT_ROOT / "examples"

# Output subdirectories
FRAMES_DIR = OUTPUT_DIR / "frames"
PROMPTS_DIR = OUTPUT_DIR / "prompts"
REFERENCE_DIR = OUTPUT_DIR / "reference"

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================
# Default Stable Diffusion model
# Options:
#   - "runwayml/stable-diffusion-v1-5" (smaller, faster)
#   - "stabilityai/stable-diffusion-2-1" (better quality)
#   - "stabilityai/stable-diffusion-xl-base-1.0" (best quality, needs more VRAM)
MODEL_ID = "runwayml/stable-diffusion-v1-5"

# Local model path (if you downloaded models manually)
LOCAL_MODEL_PATH = MODELS_DIR / "stable-diffusion-v1-5"

# Use local model if it exists, otherwise download from HuggingFace
USE_LOCAL_MODEL = LOCAL_MODEL_PATH.exists()

# ============================================================================
# GENERATION PARAMETERS
# ============================================================================
# Panel dimensions (vertical manhwa format)
PANEL_WIDTH = 1080
PANEL_HEIGHT = 1920

# For draft/preview mode (faster generation)
DRAFT_WIDTH = 540
DRAFT_HEIGHT = 960

# Generation settings
NUM_INFERENCE_STEPS = 30  # 20-30 for speed, 50+ for quality
GUIDANCE_SCALE = 7.5      # 7-9 recommended for SD 1.5
DRAFT_STEPS = 15          # Faster for previews

# ============================================================================
# PROMPT TEMPLATES
# ============================================================================
BASE_STYLE = "Korean manhwa webtoon style, clean lineart, full color, highly detailed, professional digital art"

NEGATIVE_PROMPT = (
    "low quality, blurry, distorted, deformed, ugly, bad anatomy, "
    "bad proportions, watermark, text, signature, low resolution, "
    "jpeg artifacts, duplicate, cropped, out of frame"
)

# Camera angles for variety
CAMERA_ANGLES = [
    "eye level view",
    "slightly low angle",
    "dynamic angle",
    "close-up shot",
    "medium shot",
    "wide shot"
]

# Lighting moods
LIGHTING_MOODS = [
    "dramatic lighting",
    "soft natural light",
    "cinematic lighting",
    "moody shadows",
    "bright daylight"
]

# ============================================================================
# DEVICE & PERFORMANCE
# ============================================================================
# Device detection is lazy-loaded to avoid importing torch at module level
# This prevents 30-60 second startup delay

def get_device():
    """Lazy device detection"""
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"

def get_dtype():
    """Lazy dtype detection"""
    try:
        import torch
        device = get_device()
        return torch.float16 if device == "cuda" else torch.float32
    except ImportError:
        return None

# For backward compatibility, set defaults
DEVICE = "cpu"  # Will be updated when generator loads
DTYPE = None  # Will be updated when generator loads

# Memory optimization
ENABLE_ATTENTION_SLICING = True
ENABLE_VAE_SLICING = True
ENABLE_XFORMERS = False  # Set to True if you have xformers installed

# ============================================================================
# SCENE SPLITTING PARAMETERS
# ============================================================================
# How to detect scene boundaries
SCENE_MARKERS = [
    "\n\n",           # Paragraph breaks
    "Meanwhile,",     # Transition words
    "Suddenly,",
    "Later,",
    "***",            # Manual scene breaks
    "---"
]

# Minimum words per scene (avoid tiny fragments)
MIN_SCENE_LENGTH = 30
MAX_SCENE_LENGTH = 150  # Split long scenes for better panels

# ============================================================================
# CHARACTER PROFILES
# ============================================================================
# Default character profile template
DEFAULT_CHARACTER = {
    "name": "protagonist",
    "gender": "male",
    "age": "young adult",
    "hair": "short black hair",
    "eyes": "dark eyes",
    "outfit": "modern casual clothing",
    "vibe": "determined expression",
    "reference_image": None
}

# ============================================================================
# LOGGING & DEBUG
# ============================================================================
VERBOSE = True
SAVE_PROMPTS = True
SAVE_METADATA = True

# Log file
LOG_FILE = OUTPUT_DIR / "generation.log"

# ============================================================================
# BUNDLE SETTINGS
# ============================================================================
BUNDLE_NAME = "manhwa_bundle.zip"
INCLUDE_VERTICAL_PREVIEW = True

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def create_directories():
    """Create all required output directories"""
    for dir_path in [OUTPUT_DIR, FRAMES_DIR, PROMPTS_DIR, REFERENCE_DIR, MODELS_DIR, EXAMPLES_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Directories created at {OUTPUT_DIR}")

def get_model_path():
    """Returns the model path to use"""
    if USE_LOCAL_MODEL and LOCAL_MODEL_PATH.exists():
        return str(LOCAL_MODEL_PATH)
    return MODEL_ID

def print_config():
    """Print current configuration"""
    print("=" * 60)
    print("MANHWA AUTO-PANEL GENERATOR - Configuration")
    print("=" * 60)
    print(f"Device: {DEVICE}")
    print(f"Model: {get_model_path()}")
    print(f"Panel Size: {PANEL_WIDTH}x{PANEL_HEIGHT}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Inference Steps: {NUM_INFERENCE_STEPS}")
    print("=" * 60)

if __name__ == "__main__":
    # Test configuration
    create_directories()
    print_config()
