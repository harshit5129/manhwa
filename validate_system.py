"""
System validation and testing script
"""
import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python_version():
    """Check Python version"""
    print("\n[1/8] Checking Python version...")
    version = sys.version_info
    
    if version.major >= 3 and version.minor >= 10:
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"[FAIL] Python {version.major}.{version.minor} - Need 3.10+")
        return False

def check_dependencies():
    """Check if all dependencies are installed"""
    print("\n[2/8] Checking dependencies...")
    
    required = [
        ('torch', 'PyTorch'),
        ('diffusers', 'Diffusers'),
        ('transformers', 'Transformers'),
        ('PIL', 'Pillow'),
        ('flask', 'Flask'),
        ('google.generativeai', 'Gemini SDK'),
        ('dotenv', 'python-dotenv')
    ]
    
    missing = []
    
    for module, name in required:
        try:
            __import__(module)
            print(f"[OK] {name}")
        except ImportError:
            print(f"[MISSING] {name}")
            missing.append(name)
    
    if missing:
        print(f"\nMissing: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def check_torch_cuda():
    """Check PyTorch CUDA availability"""
    print("\n[3/8] Checking GPU/CUDA...")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"[OK] CUDA Available")
            print(f"  Device: {device_name}")
            print(f"  VRAM: {vram:.1f} GB")
            return True
        else:
            print("[WARN] CUDA not available - Will use CPU (slower)")
            return True
    except Exception as e:
        print(f"[FAIL] Error checking CUDA: {e}")
        return False

def check_gemini_config():
    """Check Gemini API configuration"""
    print("\n[4/8] Checking Gemini API...")
    
    env_file = Path('.env')
    
    if not env_file.exists():
        print("[WARN] .env file not found")
        print("  Gemini features will not work")
        return True  # Non-critical
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('GEMINI_API_KEY')
        
        if api_key:
            print(f"[OK] API Key configured: {api_key[:10]}...")
            
            # Test connection
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content("Hello")
                print("[OK] Gemini API connection works!")
                return True
            except Exception as e:
                print(f"[WARN] API configured but connection failed: {e}")
                return True  # Non-critical
        else:
            print("[WARN] GEMINI_API_KEY not set in .env")
            return True  # Non-critical
            
    except Exception as e:
        print(f"[WARN] Error checking Gemini: {e}")
        return True  # Non-critical

def check_directories():
    """Check required directories exist"""
    print("\n[5/8] Checking directories...")
    
    dirs = ['models', 'output', 'examples', 'templates', 'static', 'uploads']
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"[OK] {dir_name}/")
        else:
            print(f"[CREATE] {dir_name}/")
            dir_path.mkdir(parents=True, exist_ok=True)
    
    return True

def check_core_modules():
    """Check if core modules can be imported"""
    print("\n[6/8] Checking core modules...")
    
    modules = [
        ('config', 'Configuration'),
        ('text_processor', 'Text Processing'),
        ('character_manager', 'Character Manager'),
        ('prompt_builder', 'Prompt Builder'),
        ('generator', 'Image Generator'),
        ('post_processor', 'Post Processor'),
        ('bundler', 'Bundler'),
        ('gemini_helper', 'Gemini Helper'),
        ('app', 'Flask App')
    ]
    
    errors = []
    
    for module, name in modules:
        try:
            __import__(module)
            print(f"[OK] {name}")
        except Exception as e:
            print(f"[FAIL] {name} - {str(e)[:40]}")
            errors.append((module, e))
    
    if errors:
        print(f"\n{len(errors)} module(s) have errors:")
        for mod, err in errors:
            print(f"  - {mod}: {err}")
        return False
    
    return True

def test_text_processing():
    """Test text processing pipeline"""
    print("\n[7/8] Testing text processing...")
    
    try:
        from text_processor import ChapterParser
        
        parser = ChapterParser()
        test_text = "Test paragraph one.\n\nTest paragraph two."
        parser.load_from_string(test_text)
        scenes = parser.split_scenes(use_gemini=False)
        
        if len(scenes) > 0:
            print(f"[OK] Scene splitting works ({len(scenes)} scenes)")
            return True
        else:
            print("[FAIL] No scenes detected")
            return False
            
    except Exception as e:
        print(f"[FAIL] Text processing failed: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\n[8/8] Testing configuration...")
    
    try:
        import config
        
        print(f"[OK] Device: {config.DEVICE}")
        print(f"[OK] Panel size: {config.PANEL_WIDTH}x{config.PANEL_HEIGHT}")
        print(f"[OK] Model: {config.get_model_path()}")
        
        # Create directories
        config.create_directories()
        print("[OK] Output directories created")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Config test failed: {e}")
        return False

def main():
    print_header("MANHWA GENERATOR - SYSTEM VALIDATION")
    
    tests = [
        check_python_version,
        check_dependencies,
        check_torch_cuda,
        check_gemini_config,
        check_directories,
        check_core_modules,
        test_text_processing,
        test_config
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n[CRASH] Test crashed: {e}")
            results.append(False)
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n[SUCCESS] ALL CHECKS PASSED!")
        print("\nSystem is ready to use!")
        print("\nNext steps:")
        print("  1. CLI: python main.py")
        print("  2. Dashboard: python app.py")
        print("  3. Open: http://localhost:5000")
        return 0
    else:
        print("\n[WARNING] SOME CHECKS FAILED")
        print("\nPlease fix the issues above.")
        print("\nCommon fixes:")
        print("  - pip install -r requirements.txt")
        print("  - Check .env file for Gemini API key")
        print("  - Update GPU drivers for CUDA")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        input("\nPress Enter to exit...")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nValidation interrupted")
        sys.exit(1)
