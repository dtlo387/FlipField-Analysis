#!/usr/bin/env python3
"""
Build script for FlipField Analysis GUI
Creates executables for Mac, Windows, and Linux using PyInstaller
"""

import subprocess
import sys
import os
import platform

def run_pyinstaller():
    """Run PyInstaller with optimized settings for FlipField GUI."""
    
    # Base PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=FlipField_Analysis",  # Name of the executable
        "--onefile",                  # Create a single executable file
        "--windowed",                 # Hide console window (GUI app)
        "--icon=src/flip612x612.png", # Custom app icon
        "--add-data=requirements.txt:.",  # Include requirements file
        "src/FlipFieldGUI.py"        # Main GUI file
    ]
    
    # Remove empty icon argument if no icon
    cmd = [arg for arg in cmd if arg]
    
    # Platform-specific adjustments
    if platform.system() == "Darwin":  # macOS
        cmd.extend([
            "--target-arch=universal2",  # Create universal binary for Intel/Apple Silicon
        ])
    
    print(f"Building executable for {platform.system()}...")
    print(f"Command: {' '.join(cmd)}")
    
    # Run PyInstaller
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build successful!")
        print(f"Executable created in: dist/")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Build failed!")
        print(f"Error: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def create_spec_file():
    """Create a custom .spec file for advanced configuration."""
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/FlipFieldGUI.py'],
    pathex=[],
    binaries=[],
    datas=[('requirements.txt', '.')],
    hiddenimports=[
        'pandas',
        'numpy',
        'tkinter',
        'threading',
        'os',
        'sys'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FlipField_Analysis',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# macOS App Bundle (optional)
import platform
if platform.system() == 'Darwin':
    app = BUNDLE(
        exe,
        name='FlipField_Analysis.app',
        icon=None,
        bundle_identifier='com.flipfield.analysis',
    )
'''
    
    with open('FlipField_Analysis.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created FlipField_Analysis.spec file")
    print("You can now run: pyinstaller FlipField_Analysis.spec")

def main():
    """Main build function."""
    print("🧬 FlipField Analysis - Executable Builder")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('src/FlipFieldGUI.py'):
        print("❌ Error: src/FlipFieldGUI.py not found!")
        print("Please run this script from the FlipField Code directory")
        sys.exit(1)
    
    # Show current platform
    print(f"Building for: {platform.system()} {platform.machine()}")
    
    # Ask user what they want to do
    print("\nOptions:")
    print("1. Build executable with default settings")
    print("2. Create custom .spec file for advanced configuration")
    print("3. Both")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice in ['1', '3']:
        success = run_pyinstaller()
        if not success:
            print("\n💡 Try option 2 to create a custom .spec file for troubleshooting")
    
    if choice in ['2', '3']:
        create_spec_file()
    
    print("\n" + "=" * 50)
    print("📝 Build Notes:")
    print("- The executable will be created in the 'dist/' folder")
    print("- For distribution, copy the entire contents of 'dist/' folder")
    print("- Test the executable on the target platform before distribution")
    print("- For code signing (recommended for distribution):")
    print("  • macOS: Use codesign command")
    print("  • Windows: Use signtool or similar")

if __name__ == "__main__":
    main() 