#!/bin/bash

# Calendar to Google Installer for Mac/Linux

echo "========================================================"
echo " Calendar to Google Installer"
echo "========================================================"
echo ""

# Change to the directory where the script is located
cd "$(dirname "$0")"

# 1. Check Python Installation
echo "[1/4] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed."
    echo "Please install Python 3.10 or later."
    echo "macOS: brew install python"
    echo "Linux: sudo apt install python3 python3-pip python3-tk"
    exit 1
fi
echo "Python is installed."

# 2. Install uv (Package Manager)
echo ""
echo "[2/4] Installing/Updating uv package manager..."
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Add uv to PATH for this session
    export PATH="$HOME/.cargo/bin:$PATH"
else
    echo "uv is already installed."
    uv self update
fi

# 3. Sync Dependencies
echo ""
echo "[3/4] Installing dependencies..."
uv sync
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies."
    exit 1
fi

# 4. Setup Permissions
echo ""
echo "[4/4] Setting up permissions..."
chmod +x start.command
chmod +x start.sh

# 5. Check Configuration
echo ""
echo "Checking configuration..."
CONFIG_DIR="$HOME/.calendar-to-google"
if [ ! -f "$CONFIG_DIR/credentials.json" ]; then
    echo ""
    echo "[IMPORTANT] Google Calendar API credentials are required."
    echo "Please place 'credentials.json' in:"
    echo "$CONFIG_DIR/"
    echo ""
    echo "You can also register it from the app menu later."
fi

echo ""
echo "========================================================"
echo " Installation Complete!"
echo "========================================================"
echo ""
echo "You can start the app by double-clicking 'start.command'"
echo ""
