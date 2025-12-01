#!/bin/bash

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLIST_NAME="com.user.calendartogoogle.plist"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_NAME"
PYTHON_PATH="$DIR/.venv/bin/python"
LAUNCHER_PATH="$DIR/calendar_to_google/launcher.py"

echo "========================================"
echo " Calendar to Google - Mac Startup Setup"
echo "========================================"
echo ""

# Check if .venv exists
if [ ! -f "$PYTHON_PATH" ]; then
    echo "[ERROR] Python virtual environment not found."
    echo "Please run 'install_setup.command' first."
    exit 1
fi

echo "Creating LaunchAgent plist..."

# Create the plist file
cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.calendartogoogle</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$LAUNCHER_PATH</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>$DIR</string>
    <key>StandardErrorPath</key>
    <string>/tmp/com.user.calendartogoogle.err</string>
    <key>StandardOutPath</key>
    <string>/tmp/com.user.calendartogoogle.out</string>
</dict>
</plist>
EOF

echo "Registering with launchd..."
# Unload if already exists to force update
launchctl unload "$PLIST_PATH" 2>/dev/null
launchctl load "$PLIST_PATH"

echo ""
echo "[OK] Startup configuration complete!"
echo "The app will start automatically when you log in."
echo ""
