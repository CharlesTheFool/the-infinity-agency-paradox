@echo off
REM ====================================
REM Outer Wilds CLI Game Launcher
REM Windows Batch Script
REM ====================================

REM Change to script directory (makes paths relative to launcher location)
cd /d "%~dp0"

echo.
echo ========================================
echo  Outer Wilds CLI Game Launcher
echo ========================================
echo.

REM ====================================
REM Step 1: Check if Python is installed
REM ====================================
echo [1/4] Checking for Python installation...

REM Try modern py launcher first (Python 3.3+)
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    echo Found Python via py launcher
    goto :python_found
)

REM Fallback to python command
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    echo Found Python via python command
    goto :python_found
)

REM Python not found
echo.
echo ERROR: Python is not installed or not in PATH
echo.
echo Please install Python 3.8 or higher from:
echo https://www.python.org/downloads/
echo.
echo Make sure to check "Add Python to PATH" during installation
echo.
pause
exit /b 1

:python_found

REM ====================================
REM Step 2: Create virtual environment if needed
REM ====================================
echo [2/4] Setting up virtual environment...

REM Check if venv exists but is from wrong platform (Linux/macOS)
if exist "venv" (
    if not exist "venv\Scripts\activate.bat" (
        echo Detected venv from different platform - recreating...
        rmdir /s /q venv
    )
)

if exist "venv\Scripts\activate.bat" (
    echo Virtual environment already exists
) else (
    echo Creating new virtual environment...
    %PYTHON_CMD% -m venv venv
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Failed to create virtual environment
        echo Make sure you have venv module installed
        echo.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)

REM ====================================
REM Step 3: Activate venv and install requirements
REM ====================================
echo [3/4] Installing dependencies...

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip first (silently)
python -m pip install --upgrade pip >nul 2>&1

REM Install/update requirements
python -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Some dependencies may have failed to install
    echo The game may not work correctly
    echo.
    pause
)

echo Dependencies installed

REM ====================================
REM Step 4: Launch the game
REM ====================================
echo [4/4] Starting game...
echo.
echo ========================================
echo.

REM Run the game
python main_outerwilds.py

REM Capture exit code
set GAME_EXIT_CODE=%errorlevel%

REM ====================================
REM Cleanup and exit handling
REM ====================================
echo.
echo ========================================

if %GAME_EXIT_CODE% neq 0 (
    echo.
    echo Game exited with error code: %GAME_EXIT_CODE%
    echo.
    echo Press any key to close this window...
    pause >nul
) else (
    echo.
    echo Thanks for playing!
    echo.
    timeout /t 3 >nul
)

exit /b %GAME_EXIT_CODE%
