# Ollama Setup Guide

## What is Ollama?

Ollama is a FREE, LOCAL AI that runs on your computer. No internet needed, no API keys, completely free!

## Installation

### Windows
1. Download from: https://ollama.ai/download/windows
2. Run the installer
3. Open PowerShell and run:
```bash
ollama pull llama2
```

### Mac / Linux
```bash
curl https://ollama.ai/install.sh | sh
ollama pull llama2
```

## Verify Installation

```bash
# Check Ollama is running
ollama list

# Test it
ollama run llama2 "Hello!"
```

## Using with Manhwa Generator

Once Ollama is installed and running, the AI helper will automatically use it for:

1. **Smarter Scene Detection** - Better understanding of where scenes start/end
2. **Character Extraction** - Intelligent character detail extraction
3. **Prompt Enhancement** - AI-powered prompt optimization

## Models You Can Use

```bash
# Default (recommended)
ollama pull llama2

# Faster but less capable
ollama pull llama2:7b

# More capable but slower
ollama pull llama2:13b

# Latest (best quality)
ollama pull llama3
```

## Changing Models

Edit `ai_helper.py` line 18:
```python
def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
```

Change `"llama2"` to your preferred model.

## Troubleshooting

### "Ollama not available"
- Make sure Ollama is running:
  ```bash
  ollama serve
  ```
- Check it's on port 11434:
  ```bash
  curl http://localhost:11434/api/tags
  ```

### Slow responses
- Use a smaller model: `ollama pull llama2:7b`
- Or disable Ollama and use rule-based only (still works great!)

## Performance

| Model | Speed | Quality | RAM Needed |
|-------|-------|---------|------------|
| llama2:7b | Fast | Good | 8GB |
| llama2 (13b) | Medium | Better | 16GB |
| llama3 | Slow | Best | 16GB+ |

## FREE Forever!

✅ No API keys
✅ Runs offline  
✅ Unlimited usage
✅ Your data stays local
✅ No subscriptions

**Status: Ready to use! 🎉**
