# 🎨 Manhwa Generator Pro - Complete Guide

> **Transform your novel text into stunning manhwa panels with AI**

**100% Free • No API Keys • Powered by Ollama + Stable Diffusion**

---

## 📖 Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Features](#features)
4. [Usage Guide](#usage-guide)
5. [Ollama Setup (Optional AI)](#ollama-setup)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)
8. [Production Deployment](#production-deployment)

---

## 🚀 Quick Start

### 3 Simple Steps

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run setup
setup.bat  # Windows
./setup.sh # Linux/Mac

# 3. Start the dashboard
python app.py
```

Then open **http://localhost:5000** in your browser!

---

## 📦 Installation

### Prerequisites

- Python 3.8+
- 8GB+ RAM (16GB recommended for SDXL)
- GPU with 4GB+ VRAM (optional, CPU works too)

### Step-by-Step Setup

**Windows:**
```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Validate system
python validate_system.py
```

**Linux/Mac:**
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Validate system
python validate_system.py
```

### What Gets Installed

- **Stable Diffusion** - Image generation
- **Flask** - Web interface
- **Pillow/OpenCV** - Image processing
- **Optional: Ollama/Llama2** - Free local AI

---

## ✨ Features

### Core Features
- ✅ **Text to Panels** - Paste chapter text, get manhwa panels
- ✅ **8 Art Styles** - Manhwa, Manga, Anime, Realistic, Watercolor, Dark Fantasy, Chibi, Western Comic
- ✅ **Multiple Projects** - Organize different series
- ✅ **Character Library** - Save character profiles with reference images
- ✅ **Panel Editor** - Preview and edit prompts before generating
- ✅ **Free AI** - Ollama/Llama2 or rule-based processing

### AI Capabilities
- 🧠 **Smart Scene Detection** - Automatically split chapters into visual moments
- 👤 **Character Extraction** - Auto-detect character details from text
- ✨ **Prompt Enhancement** - AI-optimized image prompts
- 📷 **Composition Advisor** - Camera angles, lighting, mood suggestions

### Export Options
- 📄 PDF
- 📚 CBZ (Comic Book ZIP)
- 📱 Vertical Scroll PNG (Webtoon format)
- 🎬 MP4 Video (Slideshow)
- 📦 ZIP Bundle

---

## 📘 Usage Guide

### Using the Web Dashboard

#### 1. Generate Panels (Main Tab)

**Basic Workflow:**
```
1. Paste your chapter text
2. Choose art style (Manhwa, Manga, etc.)
3. Select quality (Draft/Normal/High)
4. Click "Generate Manhwa Panels"
5. Download results!
```

**Example Chapter Text:**
```
Elena stood at the edge of the cliff, her silver hair dancing in the wind. 
The ancient city sprawled below, its towers reaching toward the darkening sky.

"Are you ready?" Marcus asked, placing a gentle hand on her shoulder.

She turned to face him, determination burning in her bright blue eyes. 
"I've been ready for this my entire life."

Suddenly, a massive shadow swept across the valley. The dragon had arrived.
```

#### 2. Projects Tab

**Create a Project:**
- Click "New Project"
- Enter project name (e.g., "Chapter 1: The Awakening")
- All related panels saved together

**Benefits:**
- Keep different manhwa series organized
- Track progress per project
- Easy to find and manage

#### 3. Characters Tab

**Add a Character:**
- Click "Add Character"
- Fill in details:
  - Name
  - Hair color
  - Eye color
  - Default outfit
  - Gender, age
- Upload reference image (optional)

**Why Use Character Library:**
- Consistent character appearance across panels
- Reuse profiles across projects
- Better AI understanding

#### 4. Panel Editor Tab

**Edit Before Generating:**
```
1. Select a project
2. Click "Analyze Chapter"
3. Preview all detected panels
4. Click "Edit" on any panel
5. Customize:
   - Custom prompt
   - Camera angle (close-up, wide shot, etc.)
   - Lighting (natural, dramatic, sunset)
   - Mood (tense, peaceful, exciting)
6. Save changes
7. Generate with edited prompts!
```

### Using CLI (Command Line)

```bash
# Generate from chapter file
python main.py chapter.txt

# With custom settings
python main.py chapter.txt --style manhwa --quality high --max-panels 15

# Interactive mode
python main.py --interactive
```

**Available Options:**
- `--style` - manhwa, manga, anime, realistic, watercolor, dark, chibi, comic
- `--quality` - draft, normal, high
- `--model` - sd15, sdxl
- `--max-panels` - 1 to 50

---

## 🤖 Ollama Setup

### What is Ollama?

Ollama provides **FREE local AI** (Llama2) - no internet, no API keys!

### Installation

**Windows:**
1. Download from https://ollama.ai/download/windows
2. Run installer
3. Open PowerShell:
```bash
ollama pull llama2
```

**Mac/Linux:**
```bash
curl https://ollama.ai/install.sh | sh
ollama pull llama2
```

### Verify Installation

```bash
ollama list          # Check installed models
ollama run llama2 "Hello!"  # Test it
```

### Benefits with Ollama

- ✅ **Smarter Scene Detection** - Better understanding of story structure
- ✅ **Character Extraction** - More accurate character details
- ✅ **Prompt Enhancement** - AI-optimized prompts for better images
- ✅ **100% Free & Offline** - No internet needed after download

### Available Models

```bash
# Default (recommended)
ollama pull llama2

# Faster
ollama pull llama2:7b

# Better quality
ollama pull llama2:13b

# Latest
ollama pull llama3
```

### Performance

| Model | Speed | Quality | RAM |
|-------|-------|---------|-----|
| llama2:7b | Fast | Good | 8GB |
| llama2 (13b) | Medium | Better | 16GB |
| llama3 | Slow | Best | 16GB+ |

---

## 🎯 Advanced Features

### Style Mixing

Combine multiple art styles:
```python
from styles import StyleManager

manager = StyleManager()
mixed = manager.mix_styles(['manhwa', 'watercolor'], weights=[0.7, 0.3])
```

### Image Upscaling

Enhance output quality:
```python
from upscaler import Upscaler

upscaler = Upscaler()
upscaler.upscale_image('panel.png', 'panel_4x.png', scale=4)
```

### Custom Style Presets

Create your own style:
```python
custom_style = {
    'name': 'my_style',
    'prompt_prefix': 'noir detective comic, high contrast',
    'negative_prompt': 'colorful, bright',
    'color_palette': 'grayscale'
}
```

### Batch Processing

Generate multiple chapters:
```bash
python main.py chapter1.txt chapter2.txt chapter3.txt --batch
```

---

## 🔧 Troubleshooting

### Common Issues

#### "CUDA out of memory"
**Solution:**
- Use SD 1.5 instead of SDXL
- Lower quality setting
- Close other GPU applications
- Or use CPU (slower but works)

#### "Ollama not available"
**Solution:**
```bash
# Start Ollama service
ollama serve

# Check it's running
curl http://localhost:11434/api/tags
```

#### "Poor quality panels"
**Solutions:**
- Use "High" quality setting
- Enable Ollama AI enhancement
- Add more descriptive scene text
- Edit prompts in Panel Editor
- Use SDXL model for better quality

#### "Slow generation"
**Solutions:**
- Use SD 1.5 (faster than SDXL)
- Use Draft quality
- Reduce max panels
- Use GPU instead of CPU
- Close other applications

### System Requirements

**Minimum:**
- CPU: Any modern CPU
- RAM: 8GB
- Storage: 10GB free
- GPU: Not required (CPU works)

**Recommended:**
- CPU: 4+ cores
- RAM: 16GB
- Storage: 20GB+ SSD
- GPU: 6GB+ VRAM (NVIDIA)

### Getting Help

1. Check this guide
2. Run `python validate_system.py`
3. Check logs in `manhwa_app.log`
4. Review error messages in terminal

---

## 🚀 Production Deployment

### Using Gunicorn (Linux)

```bash
# Install
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With configuration
gunicorn -c gunicorn.conf.py app:app
```

**gunicorn.conf.py:**
```python
workers = 4
threads = 2
bind = "0.0.0.0:5000"
timeout = 300
accesslog = "access.log"
errorlog = "error.log"
```

### Docker Deployment

**Dockerfile included - just run:**
```bash
# Build image
docker build -t manhwa-generator .

# Run container
docker run -p 5000:5000 -v ./models:/app/models manhwa-generator

# With GPU
docker run --gpus all -p 5000:5000 manhwa-generator
```

### Environment Variables

Create `.env` file:
```bash
SECRET_KEY=your-very-secret-random-key-here
FLASK_ENV=production
RATE_LIMIT=20
ALLOWED_ORIGINS=https://yourdomain.com
```

### Security Checklist

- ✅ Set strong SECRET_KEY
- ✅ Use HTTPS in production
- ✅ Set ALLOWED_ORIGINS
- ✅ Enable rate limiting
- ✅ Regular backups
- ✅ Update dependencies

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📂 Project Structure

```
manhwa/
├── app.py                  # Web dashboard (Flask)
├── main.py                 # CLI interface
├── config.py              # Settings
├── requirements.txt       # Dependencies
│
├── Core Modules
│   ├── text_processor.py      # Scene splitting
│   ├── character_manager.py   # Character profiles
│   ├── prompt_builder.py      # Prompt generation
│   ├── generator.py           # Stable Diffusion
│   ├── post_processor.py      # Image composition
│   └── bundler.py            # ZIP packaging
│
├── New Features
│   ├── ai_helper.py           # Ollama/Rule-based AI
│   ├── project_manager.py     # Multi-project support
│   ├── panel_editor.py        # Panel editing
│   ├── styles.py             # Style presets
│   ├── upscaler.py           # Image upscaling
│   └── exporter.py           # Export formats
│
├── Web Interface
│   ├── templates/
│   │   └── index.html        # Dashboard UI
│   └── static/
│       ├── style.css         # Styles
│       └── app.js            # JavaScript
│
├── Data
│   ├── models/               # Downloaded AI models
│   ├── output/               # Generated panels
│   ├── projects/             # Project data
│   └── character_library/    # Character profiles
│
└── Documentation
    └── GUIDE.md              # This file!
```

---

## 🎓 Tips & Best Practices

### Writing Good Chapter Text

✅ **Do:**
- Use paragraph breaks to separate scenes
- Include physical descriptions
- Mention emotions and actions
- Use dialogue naturally

❌ **Don't:**
- Write one giant paragraph
- Be too vague or generic
- Skip visual details
- Use complex formatting

### Getting Better Results

1. **Use Descriptive Text**
   ```
   Good: "Elena's silver hair whipped in the wind as she stood on the cliff"
   Bad: "She was there"
   ```

2. **Enable Ollama** - Much smarter scene analysis

3. **Edit Prompts** - Use Panel Editor to fine-tune

4. **Choose Right Style** - Manhwa for Korean, Manga for Japanese, etc.

5. **Use Character Library** - Consistent character appearance

### Prompt Engineering

**Good Prompts:**
- Be specific: "silver-haired woman in black armor"
- Add quality: "highly detailed, professional digital art"
- Set mood: "dramatic lighting, tense atmosphere"

**Avoid:**
- Too generic: "woman"
- Conflicting: "bright dark scene"
- Too complex: 100+ word prompts

---

## 📊 Performance Metrics

### Generation Speed (Approximate)

| Model | Quality | Time per Panel | GPU |
|-------|---------|---------------|-----|
| SD 1.5 | Draft | 5-10s | 4GB |
| SD 1.5 | Normal | 10-15s | 4GB |
| SD 1.5 | High | 20-30s | 4GB |
| SDXL | Draft | 15-20s | 8GB |
| SDXL | Normal | 30-40s | 8GB |
| SDXL | High | 60-90s | 8GB |

*Times on NVIDIA RTX 3060. CPU is 10-20x slower.*

---

## 🆘 Support

### Resources

- 📖 This Guide
- 🔧 `validate_system.py` - System check
- 📝 `manhwa_app.log` - Error logs
- 💬 Community support (if available)

### Reporting Issues

Include:
1. Error message (full text)
2. Steps to reproduce
3. System info from `validate_system.py`
4. Log excerpt from `manhwa_app.log`

---

## 🎉 You're All Set!

**Start creating amazing manhwa panels!**

```bash
# Quick start
python app.py

# Open browser
# http://localhost:5000

# Paste your story
# Click Generate
# Download your manhwa!
```

---

## 📝 Version History

- **v2.0** - Ollama integration, UI redesign, multi-project support
- **v1.5** - Panel editor, character library, export formats
- **v1.0** - Initial release with basic generation

---

## 📄 License

This project is provided as-is for personal and commercial use.

**Status: Production Ready! 🚀**
