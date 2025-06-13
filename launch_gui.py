#!/usr/bin/env python3
"""
FLIP FIELD GUI LAUNCHER - Top Level
===================================

Launcher script that calls the main launcher in src/ directory.
"""

import sys
import os

# Add src directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

if __name__ == "__main__":
    try:
        # Import and run the launcher from src
        from launch_gui import main
        main()
    except ImportError as e:
        print(f"Failed to import launcher: {e}")
        print("Make sure the src/ directory contains launch_gui.py")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 