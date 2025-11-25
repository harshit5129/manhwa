"""
Lightweight test of core functionality without heavy ML imports
"""
import sys
print("Testing core modules...", flush=True)

# Test text processor
print("1. Testing text_processor...", flush=True)
from text_processor import ChapterParser, Scene
parser = ChapterParser()
parser.load_from_string("Elena stood at the cliff. The wind blew.")
scenes = parser.split_scenes(use_ai=False)
print(f"   [OK] Created {len(scenes)} scenes", flush=True)

# Test character manager
print("2. Testing character_manager...", flush=True)
from character_manager import CharacterProfile, CharacterLibrary
char = CharacterProfile("Test Character")
char.gender = "female"
char.hair_color = "blue"
print(f"   [OK] Created character: {char.name}", flush=True)

# Test prompt builder
print("3. Testing prompt_builder...", flush=True)
from prompt_builder import PromptBuilder
builder = PromptBuilder()
prompt = builder.build_prompt(scenes[0], char, use_ai=False)
print(f"   [OK] Generated prompt: {prompt[:50]}...", flush=True)

# Test AI helper
print("4. Testing ai_helper...", flush=True)
from ai_helper import ai_helper
print(f"   Ollama available: {ai_helper.is_available()}", flush=True)

# Test project manager
print("5. Testing project_manager...", flush=True)
from project_manager import project_manager
projects = project_manager.list_projects()
print(f"   [OK] Found {len(projects)} projects", flush=True)

# Test panel editor
print("6. Testing panel_editor...", flush=True)
from panel_editor import PanelEditor
editor = PanelEditor()
print(f"   [OK] Panel editor created", flush=True)

print("\n" + "="*60, flush=True)
print("ALL CORE MODULES WORKING!", flush=True)
print("="*60, flush=True)
