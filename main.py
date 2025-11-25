#!/usr/bin/env python3
"""
Manhwa Auto-Panel Generator - Main Entry Point

Converts novel chapter text into vertical manhwa panels using Stable Diffusion.
"""
import argparse
import sys
from pathlib import Path
from datetime import datetime
import colorama
from colorama import Fore, Style

# Initialize colorama for Windows support
colorama.init(autoreset=True)

# Import local modules
from config import (
    create_directories, print_config, OUTPUT_DIR,
    FRAMES_DIR, PROMPTS_DIR, INCLUDE_VERTICAL_PREVIEW
)
from text_processor import ChapterParser
from character_manager import CharacterManager, CharacterProfile
from prompt_builder import PromptBuilder
from generator import ManhwaGenerator
from post_processor import PostProcessor
from bundler import Bundler


def print_banner():
    """Print application banner"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║     MANHWA AUTO-PANEL GENERATOR v1.0                         ║
║     Transform Your Novel into Beautiful Manhwa Panels        ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)


def main():
    """Main application flow"""
    print_banner()
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Generate manhwa panels from chapter text"
    )
    parser.add_argument(
        '--chapter', '-c',
        type=str,
        default='chapter.txt',
        help='Path to chapter text file (default: chapter.txt)'
    )
    parser.add_argument(
        '--character', '-ch',
        type=str,
        help='Path to character profile JSON (optional)'
    )
    parser.add_argument(
        '--reference', '-r',
        type=str,
        help='Path to character reference image (optional)'
    )
    parser.add_argument(
        '--draft', '-d',
        action='store_true',
        help='Generate draft quality (faster, lower resolution)'
    )
    parser.add_argument(
        '--seed', '-s',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    parser.add_argument(
        '--no-bundle',
        action='store_true',
        help='Skip creating ZIP bundle'
    )
    
    args = parser.parse_args()
    
    # Setup
    print(f"{Fore.YELLOW}[1/7] Setting up directories...{Style.RESET_ALL}")
    create_directories()
    print_config()
    
    # Load chapter
    print(f"\n{Fore.YELLOW}[2/7] Loading chapter text...{Style.RESET_ALL}")
    chapter_path = Path(args.chapter)
    
    if not chapter_path.exists():
        print(f"{Fore.RED}✗ Chapter file not found: {chapter_path}{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Tip: Create a file called 'chapter.txt' with your novel text,")
        print(f"or use --chapter to specify a different file.{Style.RESET_ALL}")
        return 1
    
    parser_obj = ChapterParser()
    parser_obj.load_from_file(str(chapter_path))
    
    # Split into scenes
    print(f"\n{Fore.YELLOW}[3/7] Analyzing scenes...{Style.RESET_ALL}")
    scenes = parser_obj.split_scenes()
    
    if not scenes:
        print(f"{Fore.RED}✗ No scenes found. Check your chapter text.{Style.RESET_ALL}")
        return 1
    
    # Save scene breakdown
    parser_obj.save_scenes(OUTPUT_DIR / "scenes.txt")
    
    # Setup character
    print(f"\n{Fore.YELLOW}[4/7] Loading character profile...{Style.RESET_ALL}")
    char_manager = CharacterManager()
    
    if args.character:
        # Load from file
        character = CharacterProfile.load(args.character)
        char_manager.add_character(character)
    else:
        # Try Gemini auto-detection
        try:
            from gemini_helper import gemini
            
            if gemini.is_available():
                print(f"{Fore.CYAN}  Attempting Gemini character detection...{Style.RESET_ALL}")
                char_info = gemini.extract_character_info(parser_obj.raw_text)
                
                if char_info:
                    character = CharacterProfile(char_info.get('name', 'protagonist'))
                    character.gender = char_info.get('gender', 'unknown')
                    character.age = char_info.get('age', 'young adult')
                    character.hair = char_info.get('hair', 'default hair')
                    character.eyes = char_info.get('eyes', 'default eyes')
                    character.outfit = char_info.get('outfit', 'default outfit')
                    character.vibe = char_info.get('vibe', 'neutral expression')
                    char_manager.add_character(character)
                    print(f"{Fore.GREEN}✓ Auto-detected character: {character.name}{Style.RESET_ALL}")
                else:
                    # Fallback to default
                    character = char_manager.create_default_character("protagonist")
                    print(f"{Fore.CYAN}  Using default character profile{Style.RESET_ALL}")
            else:
                # No Gemini, use default
                character = char_manager.create_default_character("protagonist")
                print(f"{Fore.CYAN}  Using default character profile{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Character auto-detection failed: {e}{Style.RESET_ALL}")
            character = char_manager.create_default_character("protagonist")
            print(f"{Fore.CYAN}  Using default character profile{Style.RESET_ALL}")
    
    # Load reference image if provided
    if args.reference:
        print(f"  Loading reference image: {args.reference}")
        character.load_reference_image(args.reference)
    
    # Save character profile
    character.save(OUTPUT_DIR / "character_profile.json")
    
    # Build prompts
    print(f"\n{Fore.YELLOW}[5/7] Building prompts...{Style.RESET_ALL}")
    prompt_builder = PromptBuilder()
    prompts = prompt_builder.build_batch_prompts(scenes, character)
    print(f"{Fore.GREEN}✓ Created {len(prompts)} prompts{Style.RESET_ALL}")
    
    # Generate panels
    print(f"\n{Fore.YELLOW}[6/7] Generating panels...{Style.RESET_ALL}")
    
    if args.draft:
        print(f"{Fore.CYAN}  Running in DRAFT mode (faster, lower quality){Style.RESET_ALL}")
    
    generator = ManhwaGenerator(draft_mode=args.draft)
    
    try:
        generator.load_pipeline()
        
        # Generate all panels
        start_time = datetime.now()
        images = generator.batch_generate(
            prompts,
            output_dir=FRAMES_DIR,
            save_prompts=True,
            seed=args.seed
        )
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n{Fore.GREEN}✓ Generation complete in {elapsed:.1f}s{Style.RESET_ALL}")
        print(f"  Average: {elapsed/len(images):.1f}s per panel")
        
    except Exception as e:
        print(f"\n{Fore.RED}✗ Generation failed: {e}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Troubleshooting:{Style.RESET_ALL}")
        print("  1. Check that Stable Diffusion model is installed")
        print("  2. Verify GPU/CUDA setup (or use CPU mode)")
        print("  3. Try --draft mode for faster/smaller generation")
        return 1
    
    finally:
        generator.unload()
    
    # Post-process
    print(f"\n{Fore.YELLOW}[7/7] Post-processing...{Style.RESET_ALL}")
    
    # Create vertical preview
    if INCLUDE_VERTICAL_PREVIEW:
        processor = PostProcessor()
        preview_path = processor.create_vertical_preview()
        if preview_path:
            print(f"{Fore.GREEN}✓ Vertical preview created{Style.RESET_ALL}")
    
    # Create bundle
    if not args.no_bundle:
        bundler = Bundler()
        bundle_path = bundler.create_bundle()
        
        if bundle_path:
            print(f"\n{Fore.GREEN}╔══════════════════════════════════════════════════════════════╗")
            print(f"║  SUCCESS! Your manhwa bundle is ready!                      ║")
            print(f"╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
            print(f"\n📦 Bundle: {Fore.CYAN}{bundle_path}{Style.RESET_ALL}")
            print(f"📁 Panels: {Fore.CYAN}{FRAMES_DIR}{Style.RESET_ALL}")
            print(f"📄 Preview: {Fore.CYAN}{OUTPUT_DIR / 'vertical_preview.png'}{Style.RESET_ALL}")
            
            print(f"\n{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
            print("  1. Review the vertical preview")
            print("  2. Check individual panels in output/frames/")
            print("  3. Share the ZIP bundle with friends or upload to platforms")
            
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠ Generation interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}✗ Unexpected error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
