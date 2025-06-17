# FlipField Analysis - Executable Build Guide

## Overview
This guide shows how to create standalone executables for FlipField Analysis that work on Mac, Windows, and Linux without requiring Python to be installed.

## Prerequisites
- Python 3.8+ installed on your system
- All dependencies from `requirements.txt` installed
- PyInstaller installed (`pip install pyinstaller`)

## Quick Build (Any Platform)

### Option 1: Simple Build
```bash
# For macOS/Linux:
python3 build_simple.py

# For Windows:
python build_simple.py
```

### Option 2: Advanced Build
```bash
# For macOS/Linux:
python3 build_executable.py

# For Windows:
python build_executable.py
```

## Platform-Specific Instructions

### 🍎 macOS
```bash
# Install PyInstaller
pip3 install pyinstaller

# Build executable
python3 build_simple.py

# Result: dist/FlipField_Analysis.app (double-click to run)
# Alternative: dist/FlipField_Analysis (command-line executable)
```

**macOS Notes:**
- Creates both a `.app` bundle and a standalone executable
- May show "unidentified developer" warning (see Code Signing section)
- Works on both Intel and Apple Silicon Macs (universal binary)

### 🪟 Windows
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
python build_simple.py

# Result: dist/FlipField_Analysis.exe
```

**Windows Notes:**
- Creates a single `.exe` file
- May trigger Windows Defender (see Code Signing section)
- Compatible with Windows 7/8/10/11

### 🐧 Linux
```bash
# Install PyInstaller
pip3 install pyinstaller

# Build executable
python3 build_simple.py

# Result: dist/FlipField_Analysis (executable binary)
```

**Linux Notes:**
- Creates a standalone binary
- Make executable: `chmod +x dist/FlipField_Analysis`
- Compatible with most Linux distributions

## Advanced Configuration

### Custom .spec File
For advanced customization, generate a `.spec` file:

```bash
python3 build_executable.py
# Choose option 2 or 3 to create FlipField_Analysis.spec

# Then build with:
pyinstaller FlipField_Analysis.spec
```

### Command-Line Build (Manual)
```bash
pyinstaller --onefile --windowed --name=FlipField_Analysis src/FlipFieldGUI.py
```

### Build Options Explained
- `--onefile`: Creates a single executable file
- `--windowed`: Hides the console window (GUI apps only)
- `--name=NAME`: Sets the executable name
- `--icon=FILE`: Adds an icon (optional)
- `--add-data=SRC:DEST`: Includes additional files

## Distribution

### What to Include
- The executable from `dist/` folder
- A README file with usage instructions
- Example input files (optional)

### File Sizes (Approximate)
- **macOS**: ~80MB (.app bundle) + ~70MB (standalone)
- **Windows**: ~70MB (.exe)
- **Linux**: ~70MB (binary)

## Code Signing (Recommended for Distribution)

### macOS Code Signing
```bash
# Sign the app bundle
codesign --force --deep --sign "Developer ID Application: Your Name" dist/FlipField_Analysis.app

# Or create a self-signed certificate for testing
codesign --force --deep --sign - dist/FlipField_Analysis.app
```

### Windows Code Signing
- Use `signtool.exe` with a valid certificate
- Or use third-party services like SignPath

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Add missing modules to the build script with `--hidden-import=MODULE`
   - Check that all dependencies are installed

2. **Large file sizes**
   - Use `--exclude-module=MODULE` to remove unused packages
   - Consider using `--onedir` instead of `--onefile` for faster startup

3. **macOS "damaged" warnings**
   - Code sign the application
   - Users can bypass with: System Preferences → Security & Privacy → Allow anyway

4. **Windows Defender warnings**
   - Code sign the executable
   - Submit to Microsoft for analysis
   - Users can add exception in Windows Defender

5. **Linux compatibility issues**
   - Build on the oldest supported Linux version
   - Check glibc version compatibility

### Debug Build
For troubleshooting, create a debug build:
```bash
pyinstaller --onefile --console --name=FlipField_Analysis_Debug src/FlipFieldGUI.py
```

## Testing Your Executable

1. **Move the executable** to a clean machine without Python
2. **Test all features**: file selection, analysis, export
3. **Check file associations** and error handling
4. **Verify output files** are created correctly

## Build Automation

### For Multiple Platforms
Create executables for all platforms using:
- GitHub Actions (automated builds)
- Docker containers (Linux builds)
- Virtual machines (Windows/macOS builds)

### Example GitHub Actions Workflow
```yaml
name: Build Executables
on: [push]
jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - run: pip install -r requirements.txt pyinstaller
    - run: python build_simple.py
    - uses: actions/upload-artifact@v2
      with:
        name: FlipField-${{ matrix.os }}
        path: dist/
```

## Tips for Distribution

1. **Test thoroughly** on clean systems
2. **Provide clear installation instructions**
3. **Include example files** and documentation
4. **Consider creating an installer** (NSIS for Windows, .dmg for macOS)
5. **Update regularly** as dependencies change

## Support

If you encounter issues:
1. Check the PyInstaller documentation
2. Review the build logs in `build/` folder
3. Test on a clean virtual machine
4. Consider using alternatives like cx_Freeze or Nuitka

---

**Note**: Executables are platform-specific. You need to build on each target platform (Windows, macOS, Linux) to create native executables for that platform. 