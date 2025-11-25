@echo off
REM ============================================================================
REM Manhwa Generator - Complete Windows Setup Script
REM Combines: Environment setup, dependencies, Gemini configuration, validation
REM ============================================================================

echo.
echo ================================================================================
echo          MANHWA AUTO-PANEL GENERATOR - COMPLETE SETUP
echo ================================================================================
echo.

REM Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.10+ from python.org
    pause
    exit /b 1
)
python --version
echo [OK] Python found
echo.

REM Create virtual environment
echo [2/6] Creating virtual environment...
if exist venv (
    echo [OK] Virtual environment already exists
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)
echo.

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo [4/6] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK] Pip upgraded
echo.

REM Install dependencies
echo [5/6] Installing dependencies...
echo This may take 5-10 minutes on first run...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    echo.
    echo Trying with verbose output:
    pip install -r requirements.txt
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Setup Gemini API
echo [6/6] Configuring Gemini API...
echo.

REM Check if .env exists
if exist .env (
    echo [OK] .env file already exists
    echo.
    echo Current Gemini configuration:
    findstr "GEMINI" .env
    echo.
    choice /C YN /M "Do you want to update Gemini API key?"
    if errorlevel 2 goto :skip_gemini
)

:setup_gemini
echo.
echo Please enter your Gemini API key:
echo (Get it from: https://aistudio.google.com/app/apikey)
echo.
set /p GEMINI_KEY="Gemini API Key: "

if "%GEMINI_KEY%"=="" (
    echo [WARNING] No API key provided. Gemini features will be disabled.
    echo You can add it later to .env file
    goto :skip_gemini
)

REM Create or update .env file
if exist .env (
    findstr /V "GEMINI_API_KEY GEMINI_MODEL" .env > .env.tmp
    move /Y .env.tmp .env >nul
)

echo GEMINI_API_KEY=%GEMINI_KEY% >> .env
echo GEMINI_MODEL=gemini-1.5-flash >> .env

echo [OK] Gemini API key configured
echo.

REM Test Gemini connection
echo Testing Gemini API connection...
python -c "from gemini_helper import gemini; print('✓ Gemini API: CONNECTED' if gemini.is_available() else '✗ Gemini API: FAILED')" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Gemini API test failed. Check your API key.
)

:skip_gemini
echo.

REM System Validation
echo.
echo ================================================================================
echo                         RUNNING SYSTEM VALIDATION
echo ================================================================================
echo.

python validate_system.py
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Some validation checks failed
    echo The system may still work, but some features might be disabled
)

echo.
echo ================================================================================
echo                            SETUP COMPLETE!
echo ================================================================================
echo.
echo Next steps:
echo   1. Edit .env file to configure settings (optional)
echo   2. Run the web dashboard: python app.py
echo   3. Or use CLI: python main.py
echo.
echo Documentation: See COMPLETE_GUIDE.md for full reference
echo.
echo To activate environment later:
echo   venv\Scripts\activate
echo.
pause
