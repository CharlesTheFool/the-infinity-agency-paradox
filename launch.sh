#!/usr/bin/env bash
# ====================================
# Outer Wilds CLI Game Launcher
# Linux Shell Script
# ====================================

# Exit on error
set -e

# Change to script directory
cd "$(dirname "$0")"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "========================================"
echo " Outer Wilds CLI Game Launcher"
echo "========================================"
echo ""

# ====================================
# Step 1: Check if Python is installed
# ====================================
echo -e "${BLUE}[1/4] Checking for Python installation...${NC}"

PYTHON_CMD=""

# Try python3 first (preferred on Linux)
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_CMD="python3"
    echo -e "${GREEN}Found Python $PYTHON_VERSION${NC}"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    PYTHON_CMD="python"
    echo -e "${GREEN}Found Python $PYTHON_VERSION${NC}"
else
    echo ""
    echo -e "${RED}ERROR: Python is not installed${NC}"
    echo ""
    echo "Please install Python 3.8 or higher:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-venv"
    echo "  Fedora: sudo dnf install python3"
    echo "  Arch: sudo pacman -S python"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# ====================================
# Step 2: Create virtual environment if needed
# ====================================
echo -e "${BLUE}[2/4] Setting up virtual environment...${NC}"

# Check if venv exists but is from wrong platform (Windows)
if [ -d "venv" ] && [ ! -f "venv/bin/activate" ]; then
    echo -e "${YELLOW}Detected venv from different platform - recreating...${NC}"
    rm -rf venv
fi

if [ -f "venv/bin/activate" ]; then
    echo "Virtual environment already exists"
else
    echo "Creating new virtual environment..."
    $PYTHON_CMD -m venv venv

    if [ $? -ne 0 ]; then
        echo ""
        echo -e "${RED}ERROR: Failed to create virtual environment${NC}"
        echo ""
        echo "You may need to install python3-venv:"
        echo "  sudo apt install python3-venv"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi

    echo -e "${GREEN}Virtual environment created successfully${NC}"
fi

# ====================================
# Step 3: Activate venv and install requirements
# ====================================
echo -e "${BLUE}[3/4] Installing dependencies...${NC}"

# Activate virtual environment
source venv/bin/activate

# Upgrade pip first (silently)
python -m pip install --upgrade pip > /dev/null 2>&1

# Install/update requirements
python -m pip install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}WARNING: Some dependencies may have failed to install${NC}"
    echo "The game may not work correctly"
    echo ""
    read -p "Press Enter to continue anyway..."
fi

echo -e "${GREEN}Dependencies installed${NC}"

# ====================================
# Step 4: Launch the game
# ====================================
echo -e "${BLUE}[4/4] Starting game...${NC}"
echo ""
echo "========================================"
echo ""

# Run the game
python main_outerwilds.py

# Capture exit code
GAME_EXIT_CODE=$?

# ====================================
# Cleanup and exit handling
# ====================================
echo ""
echo "========================================"

if [ $GAME_EXIT_CODE -ne 0 ]; then
    echo ""
    echo -e "${RED}Game exited with error code: $GAME_EXIT_CODE${NC}"
    echo ""
    read -p "Press Enter to close..."
else
    echo ""
    echo -e "${GREEN}Thanks for playing!${NC}"
    echo ""
    sleep 2
fi

exit $GAME_EXIT_CODE
