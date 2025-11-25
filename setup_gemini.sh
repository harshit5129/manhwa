#!/bin/bash
echo "========================================"
echo " Manhwa Generator - Gemini Setup"
echo "========================================"
echo ""

echo "Installing Gemini SDK and dependencies..."
pip install google-generativeai python-dotenv

echo ""
echo "Testing Gemini connection..."
python gemini_helper.py

echo ""
echo "========================================"
echo " Setup complete!"
echo "========================================"
