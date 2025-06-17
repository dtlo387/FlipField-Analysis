@echo off
REM FlipField Analysis - Windows Build Script
REM This script builds a Windows executable using PyInstaller

echo ============================================
echo FlipField Analysis - Windows Build Script
echo ============================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Check if source file exists
if not exist "src\FlipFieldGUI.py" (
    echo ERROR: src\FlipFieldGUI.py not found
    echo Please run this script from the FlipField Code directory
    pause
    exit /b 1
)

echo Building executable for Windows...
echo This may take several minutes...
echo.

REM Run PyInstaller
pyinstaller --onefile --windowed --name=FlipField_Analysis --icon=src\flip612x612.png src\FlipFieldGUI.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the error messages above for details.
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Your executable is ready:
    echo   dist\FlipField_Analysis.exe
    echo.
    echo You can now distribute this .exe file to other Windows computers.
    echo No Python installation is required on target machines.
    echo.
)

pause 