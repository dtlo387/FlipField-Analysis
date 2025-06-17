#!/usr/bin/env python3
"""
Simple build script for FlipField Analysis GUI
Quick one-liner to create executable
"""

import subprocess
import platform

# Simple PyInstaller command
cmd = [
    "pyinstaller",
    "--onefile",                    # Single executable
    "--windowed",                   # No console (GUI only)
    "--name=FlipField_Analysis",    # Executable name
    "--icon=src/flip612x612.png",   # Custom app icon
    "src/FlipFieldGUI.py"          # Main file
]

print(f"Building FlipField Analysis for {platform.system()}...")
print("This may take a few minutes...")

try:
    subprocess.run(cmd, check=True)
    print("✅ Build complete! Check the 'dist/' folder for your executable.")
except subprocess.CalledProcessError as e:
    print(f"❌ Build failed: {e}")
    print("Try running: python build_executable.py for more options") 