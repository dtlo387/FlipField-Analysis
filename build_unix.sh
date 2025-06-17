#!/bin/bash

# FlipField Analysis - Unix Build Script (macOS/Linux)
# This script builds executables using PyInstaller

echo "============================================"
echo "FlipField Analysis - Unix Build Script"
echo "============================================"

# Detect platform
PLATFORM=$(uname)
echo "Platform detected: $PLATFORM"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

echo "Python version: $(python3 --version)"

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" &> /dev/null; then
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install PyInstaller"
        exit 1
    fi
fi

# Check if source file exists
if [ ! -f "src/FlipFieldGUI.py" ]; then
    echo "ERROR: src/FlipFieldGUI.py not found"
    echo "Please run this script from the FlipField Code directory"
    exit 1
fi

echo "Building executable for $PLATFORM..."
echo "This may take several minutes..."
echo

# Platform-specific build commands
if [ "$PLATFORM" = "Darwin" ]; then
    # macOS - create universal binary
    pyinstaller --onefile --windowed --name=FlipField_Analysis --target-arch=universal2 --icon=src/flip612x612.png src/FlipFieldGUI.py
    BUILD_RESULT=$?
    
    if [ $BUILD_RESULT -eq 0 ]; then
        echo
        echo "========================================"
        echo "BUILD SUCCESSFUL!"
        echo "========================================"
        echo
        echo "Your executables are ready:"
        echo "  dist/FlipField_Analysis.app  (double-click to run)"
        echo "  dist/FlipField_Analysis      (command-line executable)"
        echo
        echo "To distribute:"
        echo "  1. Copy the .app bundle to other Macs"
        echo "  2. Users may need to allow 'unidentified developer'"
        echo "     (System Preferences → Security & Privacy)"
        echo
    fi
else
    # Linux
    pyinstaller --onefile --windowed --name=FlipField_Analysis --icon=src/flip612x612.png src/FlipFieldGUI.py
    BUILD_RESULT=$?
    
    if [ $BUILD_RESULT -eq 0 ]; then
        # Make sure it's executable
        chmod +x dist/FlipField_Analysis
        
        echo
        echo "========================================"
        echo "BUILD SUCCESSFUL!"
        echo "========================================"
        echo
        echo "Your executable is ready:"
        echo "  dist/FlipField_Analysis"
        echo
        echo "To run: ./dist/FlipField_Analysis"
        echo "To distribute: Copy the FlipField_Analysis file to other Linux systems"
        echo
    fi
fi

if [ $BUILD_RESULT -ne 0 ]; then
    echo
    echo "ERROR: Build failed!"
    echo "Check the error messages above for details."
    exit 1
fi

echo "Build completed successfully!" 