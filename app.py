
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from pathlib import Path
import os
import uuid
import json
from datetime import datetime
import threading
import shutil
import logging
from functools import wraps
import time

# Import generator modules
from config import create_directories, OUTPUT_DIR, FRAMES_DIR
from text_processor import ChapterParser
from character_manager import character_library, CharacterProfile
from prompt_builder import PromptBuilder
from generator import ManhwaGenerator
from post_processor import PostProcessor
from bundler import Bundler
from project_manager import project_manager
from panel_editor import PanelEditor

# ============================================================================
# LOGGING SETUP
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('manhwa_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# APP INITIALIZATION
# ============================================================================
app = Flask(__name__)

# Load secret key from environment
app.secret_key = os.getenv('SECRET_KEY', 'change-this-in-production-to-random-string')
if app.secret_key == 'change-this-in-production-to-random-string':
    logger.warning("Using default secret key! Set SECRET_KEY environment variable in production")

# CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv('ALLOWED_ORIGINS', '*').split(','),
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})

# Create necessary directories
create_directories()

# Upload folder with size limit
UPLOAD_FOLDER = Path('uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Store generation jobs (in production, use Redis or database)
generation_jobs = {}
MAX_JOBS = 100  # Limit stored jobs

# Rate limiting (simple in-memory, use Redis in production)
request_counts = {}
RATE_LIMIT = int(os.getenv('RATE_LIMIT', '10'))  # requests per minute
RATE_WINDOW = 60  # seconds

# ============================================================================
# SECURITY & VALIDATION
# ============================================================================

def rate_limit(f):
    """Simple rate limiting decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        current_time = time.time()
        
        # Clean old entries
        request_counts[client_ip] = [
            req_time for req_time in request_counts.get(client_ip, [])
            if current_time - req_time < RATE_WINDOW
        ]
        
        # Check rate limit
        if len(request_counts.get(client_ip, [])) >= RATE_LIMIT:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return jsonify({'error': 'Rate limit exceeded. Try again later.'}), 429
        
        # Add current request
        request_counts.setdefault(client_ip, []).append(current_time)
        
        return f(*args, **kwargs)
    return decorated_function


def validate_text_input(text, max_length=50000):
    """Validate and sanitize text input"""
    if not text or not isinstance(text, str):
        raise ValueError("Invalid text input")
    
    if len(text) > max_length:
        raise ValueError(f"Text too long (max {max_length} characters)")
    
    return text.strip()


def validate_settings(settings):
    """Validate generation settings"""
    valid_models = ['sd15', 'sdxl', 'custom']
    valid_styles = ['manhwa', 'manga', 'anime', 'realistic', 'watercolor', 'dark', 'chibi', 'comic']
    valid_quality = ['draft', 'normal', 'high']
    
    if settings.get('model') not in valid_models:
        settings['model'] = 'sd15'
    
    if settings.get('style') not in valid_styles:
        settings['style'] = 'manhwa'
    
    if settings.get('quality') not in valid_quality:
        settings['quality'] = 'normal'
    
    try:
        max_panels = int(settings.get('max_panels', 10))
        settings['max_panels'] = max(1, min(50, max_panels))  # Clamp 1-50
    except:
        settings['max_panels'] = 10
    
    return settings


# ============================================================================
# GENERATION JOB CLASS
# ============================================================================

class GenerationJob:
    """Track generation job status"""
    
    def __init__(self, job_id):
        self.job_id = job_id
        self.status = 'queued'
        self.progress = 0
        self.current_step = ''
        self.total_panels = 0
        self.generated_panels = 0
        self.error = None
        self.output_path = None
        self.started_at = datetime.now()
        self.completed_at = None
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'job_id': self.job_id,
            'status': self.status,
            'progress': self.progress,
            'current_step': self.current_step,
            'total_panels': self.total_panels,
            'generated_panels': self.generated_panels,
            'error': self.error,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


# ============================================================================
# GENERATION WORKER
# ============================================================================

def run_generation(job_id, chapter_text, character_data, reference_image_path, settings):
    """Run generation in background thread with error handling"""
    job = generation_jobs[job_id]
    
    try:
        job.status = 'processing'
        logger.info(f"Starting job {job_id}")
        
        # Parse chapter
        job.current_step = 'Parsing chapter...'
        parser = ChapterParser()
        parser.load_from_string(chapter_text)
        
        # Detect scenes
        job.current_step = 'Detecting scenes...'
        use_ai = settings.get('ai_scenes', True)
        scenes = parser.split_scenes(use_ai=use_ai)
        
        # Limit panels
        max_panels = int(settings.get('max_panels', 10))
        scenes = scenes[:max_panels]
        job.total_panels = len(scenes)
        job.progress = 10
        
        if not scenes:
            raise ValueError("No scenes detected in chapter")
        
        # Setup character
        job.current_step = 'Setting up character...'
        
        # Helper to create default character
        def create_default_character():
            char = CharacterProfile("Protagonist")
            char.gender = "unknown"
            char.age = "young adult"
            return char

        if character_data:
            character = CharacterProfile(character_data.get('name', 'protagonist'))
            character.gender = character_data.get('gender', 'unknown')
            character.age = character_data.get('age', 'young adult')
            character.hair_color = character_data.get('hair', '')
            character.eye_color = character_data.get('eyes', '')
            character.default_outfit = character_data.get('outfit', '')
            character.vibe = character_data.get('vibe', '')
            
            if reference_image_path and Path(reference_image_path).exists():
                character.load_reference_image(reference_image_path)
            
            character_library.add_character(character)
        else:
            # Try AI auto-detection
            try:
                from ai_helper import ai_helper
                if ai_helper.is_available():
                    char_info = ai_helper.extract_character_info(chapter_text)
                    if char_info:
                        character = CharacterProfile(char_info.get('name', 'protagonist'))
                        character.gender = char_info.get('gender', 'unknown')
                        character.age = char_info.get('age', 'young adult')
                        character.hair_color = char_info.get('hair', '')
                        character.eye_color = char_info.get('eyes', '')
                        character.default_outfit = char_info.get('outfit', '')
                        character.vibe = char_info.get('vibe', '')
                        character_library.add_character(character)
                    else:
                        character = create_default_character()
                else:
                    character = create_default_character()
            except Exception as e:
                logger.warning(f"AI character detection failed: {e}")
                character = create_default_character()
        
        job.progress = 20
        
        # Build prompts
        job.current_step = 'Building prompts...'
        prompt_builder = PromptBuilder()
        
        # Apply style
        style = settings.get('style', 'manhwa')
        if style != 'manhwa':
            try:
                from styles import style_manager
                prompt_builder.style = style
            except Exception as e:
                logger.warning(f"Style application failed: {e}")
        
        # Build prompts with AI if enabled
        use_ai_prompts = settings.get('ai_prompts', True)
        prompts = prompt_builder.build_batch_prompts(scenes, character, use_ai=use_ai_prompts)
        job.progress = 30
        
        # Determine quality settings
        quality = settings.get('quality', 'normal')
        draft_mode = (quality == 'draft')
        upscale = (quality == 'high')
        
        # Generate panels
        job.current_step = 'Generating panels...'
        generator = ManhwaGenerator(draft_mode=draft_mode)
        
        # Load appropriate model
        model = settings.get('model', 'sd15')
        if model == 'sdxl':
            import config
            config.MODEL_ID = 'stabilityai/stable-diffusion-xl-base-1.0'
        
        generator.load_pipeline()
        
        # Generate with progress updates
        for idx, (positive, negative) in enumerate(prompts):
            job.current_step = f'Generating panel {idx+1}/{len(prompts)}...'
            job.generated_panels = idx
            job.progress = 30 + int((idx / len(prompts)) * 60)
            
            try:
                image = generator.generate_panel(positive, negative, seed=42 + idx)
                img_path = FRAMES_DIR / f"panel_{idx+1:03d}.png"
                image.save(img_path, "PNG", optimize=True)
            except Exception as e:
                logger.error(f"Panel {idx+1} generation failed: {e}")
                raise
        
        generator.unload()
        job.generated_panels = len(prompts)
        job.progress = 90
        
        # Upscale if high quality
        if upscale:
            try:
                job.current_step = 'Upscaling panels...'
                from upscaler import upscaler
                from PIL import Image
                
                upscale_dir = FRAMES_DIR.parent / 'upscaled'
                upscale_dir.mkdir(exist_ok=True)
                
                for panel_file in sorted(FRAMES_DIR.glob('panel_*.png')):
                    img = Image.open(panel_file)
                    upscaled = upscaler.upscale_and_enhance(img, scale=2)
                    upscaled.save(upscale_dir / panel_file.name, 'PNG', optimize=True)
                
                # Replace originals with upscaled
                for f in upscale_dir.glob('*.png'):
                    shutil.copy(f, FRAMES_DIR / f.name)
            except Exception as e:
                logger.warning(f"Upscaling failed: {e}")
        
        # Post-process
        job.current_step = 'Creating preview...'
        processor = PostProcessor()
        processor.create_vertical_preview()
        
        # Create bundle
        job.current_step = 'Creating bundle...'
        bundler = Bundler()
        bundle_path = bundler.create_bundle()
        
        job.status = 'completed'
        job.progress = 100
        job.current_step = 'Complete!'
        job.output_path = str(bundle_path)
        job.completed_at = datetime.now()
        
        logger.info(f"Job {job_id} completed successfully")
        
    except Exception as e:
        job.status = 'failed'
        job.error = str(e)
        job.completed_at = datetime.now()
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)


@app.route('/api/generate', methods=['POST'])
@rate_limit
def generate():
    """Start a new generation job"""
    try:
        data = request.get_json()
        
        # Validate input
        chapter_text = validate_text_input(data.get('chapter_text'))
        settings = validate_settings(data)
        
        # Create job
        job_id = str(uuid.uuid4())
        job = GenerationJob(job_id)
        generation_jobs[job_id] = job
        
        # Start background thread
        thread = threading.Thread(
            target=run_generation,
            args=(job_id, chapter_text, data.get('character'), data.get('reference_image'), settings)
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Generation started'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Generation request failed: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/progress/<job_id>')
def get_progress(job_id):
    """Get job progress"""
    job = generation_jobs.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
        
    return jsonify(job.to_dict())


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_jobs': sum(1 for j in generation_jobs.values() if j.status == 'processing')
    })


def get_panels(job_id):
    """Get list of generated panels"""
    panel_files = sorted(FRAMES_DIR.glob("panel_*.png"))
    
    panels = [{'filename': p.name, 'url': f'/api/panel/{p.name}'} for p in panel_files]
    
    return jsonify({'panels': panels})


@app.route('/api/panel/<filename>')
def get_panel(filename):
    """Serve individual panel image"""
    # Validate filename
    if not filename.startswith('panel_') or '..' in filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    panel_path = FRAMES_DIR / filename
    if panel_path.exists() and panel_path.is_file():
        return send_file(panel_path, mimetype='image/png')
    
    return jsonify({'error': 'Panel not found'}), 404


@app.route('/api/preview')
def get_preview():
    """Serve vertical preview"""
    preview_path = OUTPUT_DIR / 'vertical_preview.png'
    if preview_path.exists():
        return send_file(preview_path, mimetype='image/png')
    return jsonify({'error': 'Preview not found'}), 404


@app.route('/api/download/<job_id>')
def download_bundle(job_id):
    """Download the generated bundle"""
    job = generation_jobs.get(job_id)
    
    if not job or job.status != 'completed':
        return jsonify({'error': 'Bundle not ready'}), 404
    
    bundle_path = Path(job.output_path)
    if bundle_path.exists():
        return send_file(
            bundle_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name='manhwa_bundle.zip'
        )
    
    return jsonify({'error': 'Bundle not found'}), 404


@app.route('/api/export/<job_id>/<format>')
def export_file(job_id, format):
    """Export in different formats"""
    job = generation_jobs.get(job_id)
    
    if not job or job.status != 'completed':
        return jsonify({'error': 'Job not completed'}), 404
    
    # Validate format
    valid_formats = ['pdf', 'cbz', 'scroll', 'mp4']
    if format not in valid_formats:
        return jsonify({'error': 'Invalid format'}), 400
    
    try:
        from exporter import exporter
        export_dir = OUTPUT_DIR / 'exports'
        export_dir.mkdir(exist_ok=True)
        
        if format == 'pdf':
            output_file = export_dir / f'{job_id}.pdf'
            exporter.export_pdf(FRAMES_DIR, output_file)
            return send_file(output_file, mimetype='application/pdf', as_attachment=True, download_name='manhwa.pdf')
        
        elif format == 'cbz':
            output_file = export_dir / f'{job_id}.cbz'
            exporter.export_cbz(FRAMES_DIR, output_file)
            return send_file(output_file, mimetype='application/x-cbz', as_attachment=True, download_name='manhwa.cbz')
        
        elif format == 'scroll':
            output_file = export_dir / f'{job_id}_scroll.png'
            exporter.export_vertical_scroll(FRAMES_DIR, output_file)
            return send_file(output_file, mimetype='image/png', as_attachment=True, download_name='vertical_scroll.png')
        
        elif format == 'mp4':
            output_file = export_dir / f'{job_id}.mp4'
            exporter.export_video(FRAMES_DIR, output_file)
            return send_file(output_file, mimetype='video/mp4', as_attachment=True, download_name='manhwa.mp4')
    
    except Exception as e:
        logger.error(f"Export failed for {job_id}/{format}: {e}", exc_info=True)
        return jsonify({'error': f'Export failed: {str(e)}'}), 500


# ============================================================================
# NEW FEATURES - PROJECT MANAGEMENT
# ============================================================================

# Store active panel editors
panel_editors = {}


@app.route('/api/projects', methods=['GET'])
@rate_limit
def list_projects():
    """List all projects"""
    try:
        projects = project_manager.list_projects()
        return jsonify({'success': True, 'projects': projects})
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects', methods=['POST'])
@rate_limit
def create_project():
    """Create new project"""
    try:
        data = request.get_json()
        title = validate_text_input(data.get('title', 'New Manhwa'), max_length=200)
        project = project_manager.create_project(title)
        return jsonify({'success': True, 'project': project.to_dict()})
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>', methods=['GET', 'PUT', 'DELETE'])
@rate_limit
def manage_project(project_id):
    """Get, update, or delete a project"""
    try:
        if request.method == 'GET':
            project = project_manager.get_project(project_id)
            if not project:
                return jsonify({'error': 'Project not found'}), 404
            return jsonify({'success': True, 'project': project.to_dict()})
        
        elif request.method == 'PUT':
            data = request.get_json()
            project = project_manager.update_project(project_id, data)
            if not project:
                return jsonify({'error': 'Project not found'}), 404
            return jsonify({'success': True, 'project': project.to_dict()})
        
        elif request.method == 'DELETE':
            success = project_manager.delete_project(project_id)
            if not success:
                return jsonify({'error': 'Project not found'}), 404
            return jsonify({'success': True})
            
    except Exception as e:
        logger.error(f"Error managing project {project_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/characters', methods=['GET'])
@rate_limit
def list_characters():
    """List all characters in library"""
    try:
        characters = character_library.list_characters()
        return jsonify({'success': True, 'characters': characters})
    except Exception as e:
        logger.error(f"Error listing characters: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/characters', methods=['POST'])
@rate_limit
def create_character():
    """Create new character"""
    try:
        data = request.get_json()
        name = validate_text_input(data.get('name', 'Character'), max_length=100)
        char = CharacterProfile(name)
        char.gender = data.get('gender', '')
        char.age = data.get('age', '')
        char.hair_color = data.get('hair_color', '')
        char.eye_color = data.get('eye_color', '')
        char.default_outfit = data.get('default_outfit', '')
        character_library.add_character(char)
        return jsonify({'success': True, 'character': char.to_dict()})
    except Exception as e:
        logger.error(f"Error creating character: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/panels/preview', methods=['POST'])
@rate_limit
def preview_panels():
    """Generate panel prompts for preview/editing"""
    try:
        data = request.get_json()
        chapter_text = validate_text_input(data.get('chapter_text', ''))
        project_id = data.get('project_id', 'temp')
        parser = ChapterParser()
        parser.load_from_string(chapter_text)
        scenes = parser.split_scenes(use_ai=True)
        editor = PanelEditor()
        prompt_builder = PromptBuilder()
        panels = editor.create_panels_from_scenes(scenes, prompt_builder, character_library)
        panel_editors[project_id] = editor
        return jsonify({'success': True, 'panels': [p.to_dict() for p in panels]})
    except Exception as e:
        logger.error(f"Error previewing panels: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/panels/<project_id>/<int:panel_id>', methods=['PUT'])
@rate_limit
def update_panel(project_id, panel_id):
    """Update panel prompt and settings"""
    try:
        editor = panel_editors.get(project_id)
        if not editor:
            return jsonify({'error': 'Panel editor not found'}), 404
        data = request.get_json()
        success = editor.update_panel(
            panel_id,
            edited_prompt=data.get('edited_prompt'),
            negative_prompt=data.get('negative_prompt'),
            character_ids=data.get('character_ids'),
            mood=data.get('mood'),
            camera_angle=data.get('camera_angle'),
            lighting=data.get('lighting'),
            composition=data.get('composition')
        )
        if not success:
            return jsonify({'error': 'Panel not found'}), 404
        panel = editor.get_panel(panel_id)
        return jsonify({'success': True, 'panel': panel.to_dict()})
    except Exception as e:
        logger.error(f"Error updating panel: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large (max 50MB)'}), 413


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎨 Manhwa Generator Dashboard - Enhanced Edition")
    print("="*60)
    print(f"\n[OK] Projects & Multi-Manhwa Support")
    print(f"[OK] Character Library with References")
    print(f"[OK] Panel-by-Panel Editing")
    print(f"[OK]  Server: http://localhost:5000")
    print("\nPress Ctrl+C to stop\n")
    
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    
    if debug_mode:
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("⚠ For production, use: gunicorn -w 4 -b 0.0.0.0:5000 app:app")
        app.run(debug=False, host='0.0.0.0', port=5000)
