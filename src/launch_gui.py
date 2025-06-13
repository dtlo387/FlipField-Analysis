#!/usr/bin/env python3
"""
🚀 FLIP FIELD GUI LAUNCHER
=========================

Simple launcher script that checks dependencies and starts the GUI application.
"""

import sys
import os
import subprocess
import importlib.util

# Add src directory to Python path
src_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, src_dir)

def check_dependency(package_name, install_name=None):
    """Check if a package is installed."""
    if install_name is None:
        install_name = package_name
    
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        print(f"❌ Missing dependency: {package_name}")
        print(f"   Install with: pip install {install_name}")
        return False
    else:
        print(f"✅ {package_name} is available")
        return True

def main():
    """Main launcher function."""
    print("🧬 Bead Flip Detection System - GUI Launcher")
    print("=" * 50)
    print("\nChecking dependencies...")
    
    # Check required packages
    dependencies = [
        ("matplotlib", "matplotlib>=3.5.0"),
        ("pandas", "pandas>=1.3.0"),
        ("numpy", "numpy>=1.20.0"),
        ("tkinter", None)  # Usually comes with Python
    ]
    
    all_good = True
    for package, install_cmd in dependencies:
        if not check_dependency(package, install_cmd):
            all_good = False
    
    if not all_good:
        print("\n❌ Some dependencies are missing.")
        print("Please install them using:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    print("\n✅ All dependencies satisfied!")
    print("🚀 Launching GUI application...")
    
    # Try to import and run the GUI
    try:
        from FlipFieldGUI import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"❌ Failed to import GUI module: {e}")
        print("Make sure FlipFieldGUI.py is in the src/ directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 