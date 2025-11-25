# 🎨 Manhwa Generator Pro

**Transform your novel into stunning manhwa panels with AI**

[![Free](https://img.shields.io/badge/100%25-Free-success)](https://github.com)
[![No API Keys](https://img.shields.io/badge/API%20Keys-Not%20Required-blue)](https://github.com)
[![Ollama Powered](https://img.shields.io/badge/Ollama-Powered-purple)](https://ollama.ai)

---

## ✨ Features

- 🎨 **8 Art Styles** - Manhwa, Manga, Anime, Realistic, Watercolor, Dark Fantasy, Chibi, Comic
- 🤖 **Free AI** - Ollama/Llama2 or rule-based processing (no API keys!)
- 📁 **Multi-Project** - Organize different manhwa series
- 👤 **Character Library** - Save profiles with reference images
- ✏️ **Panel Editor** - Preview and edit prompts before generating
- 📦 **Multiple Exports** - PDF, CBZ, PNG, MP4, ZIP

---

## 🚀 Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Setup
setup.bat  # Windows
./setup.sh # Mac/Linux

# 3. Run
python app.py
```

Open **http://localhost:5000** and start creating!

---

## 📖 Full Documentation

See **[GUIDE.md](GUIDE.md)** for complete documentation including:
- Detailed installation
- Usage guide
- Ollama setup
- Advanced features
- Troubleshooting
- Production deployment

---

## 🎯 Basic Usage

### Web Dashboard (Recommended)

1. Paste your chapter text
2. Choose art style & settings
3. Click "Generate"
4. Download your manhwa panels!

### Command Line

```bash
python main.py chapter.txt --style manhwa --quality high
```

---

## 📋 Requirements

- Python 3.8+
- 8GB+ RAM (16GB for SDXL)
- GPU with 4GB+ VRAM (optional)

---

## 🤖 Optional: Ollama AI

For enhanced features, install [Ollama](https://ollama.ai):

```bash
# Download Ollama, then:
ollama pull llama2
```

Benefits:
- Smarter scene detection
- Better character extraction  
- AI-optimized prompts

---

## 📂 Project Structure

```
manhwa/
├── app.py              # Web dashboard
├── main.py             # CLI interface
├── requirements.txt    # Dependencies
├── GUIDE.md           # Full documentation
├── OLLAMA_SETUP.md    # Ollama guide
├── setup.bat          # Windows setup
└── templates/         # Web UI
```

---

## 🆘 Help

- 📖 Read [GUIDE.md](GUIDE.md)
- 🔧 Run `python validate_system.py`
- 📝 Check `manhwa_app.log` for errors

---

## 🎉 Example

**Input:**
```
Elena stood at the edge of the cliff, her silver hair dancing 
in the wind. "Are you ready?" Marcus asked. She turned to face 
him, determination burning in her bright blue eyes.
```

**Output:**
- 3 manhwa panels
- Vertical scroll format
- Ready to use!

---

## 📄 License

Free for personal and commercial use.

---

**Happy Creating! 🎨**
