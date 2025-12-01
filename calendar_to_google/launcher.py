import os
import sys

# Add the parent directory to sys.path to allow importing calendar_to_google
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from calendar_to_google.tray_app import main

if __name__ == "__main__":
    main()
