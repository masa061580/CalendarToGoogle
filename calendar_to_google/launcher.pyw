"""Silent launcher for Windows (no console window) with error logging."""

import sys
import os
from datetime import datetime

# Set up paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(SCRIPT_DIR)
LOG_FILE = os.path.join(APP_DIR, "startup_error.log")

def log_message(msg):
    """Write message to log file."""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    except:
        pass

try:
    # Add app directory to path
    sys.path.insert(0, APP_DIR)

    # Change working directory
    os.chdir(APP_DIR)

    log_message(f"Starting from: {APP_DIR}")
    log_message(f"Python: {sys.executable}")

    from calendar_to_google.tray_app import main
    log_message("Imported successfully, starting main()")
    main()

except Exception as e:
    import traceback
    log_message(f"ERROR: {e}")
    log_message(traceback.format_exc())
