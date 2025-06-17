# FlipField Analysis - Standalone Application

## Overview
FlipField Analysis is a standalone application for analyzing bead flip detection in magnetic field experiments. This executable version doesn't require Python to be installed.

## System Requirements

### 🍎 macOS
- macOS 10.13 (High Sierra) or later
- Intel or Apple Silicon Mac
- ~100MB free disk space

### 🪟 Windows
- Windows 7/8/10/11 (64-bit)
- ~80MB free disk space

### 🐧 Linux
- Most modern Linux distributions
- glibc 2.17 or later
- ~80MB free disk space

## Installation

### macOS
1. Download `FlipField_Analysis.app`
2. Move to Applications folder (optional)
3. Double-click to run
4. If you see a security warning:
   - Go to System Preferences → Security & Privacy
   - Click "Open Anyway" when prompted

### Windows
1. Download `FlipField_Analysis.exe`
2. Save to desired location
3. Double-click to run
4. If Windows Defender shows a warning:
   - Click "More info" then "Run anyway"

### Linux
1. Download `FlipField_Analysis`
2. Make executable: `chmod +x FlipField_Analysis`
3. Run: `./FlipField_Analysis`

## Usage

1. **Choose Input File**: Select your bead tracking data file (.txt format)
2. **Choose Output Folder**: Select where to save analysis results
3. **Enter Video Length**: Input video duration in minutes and seconds
4. **Configure Settings** (optional): Click Settings to choose export formats
5. **Click Analyze**: Start the analysis process

### Input File Format
The application expects tab-separated data with columns:
- Frame number
- X Position (px)
- Y Position (px)  
- Angle (deg)

### Output Files
The analysis creates several files:
- **Flip Summary**: Simple overview of detected flip events
- **Full Analysis** (optional): Complete data with flip markers
- **Debug Log**: Technical details for troubleshooting

## Features

- **Automated Flip Detection**: Identifies bead flip events automatically
- **Pairing Algorithm**: Matches flip pairs using spacing criteria
- **False Positive Filtering**: Eliminates noise and isolated detections
- **Multiple Export Formats**: CSV, TXT, and summary files
- **User-Friendly Interface**: Simple GUI for easy operation

## Troubleshooting

### Application Won't Start
- **macOS**: Check security settings, try right-click → Open
- **Windows**: Check Windows Defender, add exception if needed
- **Linux**: Ensure file has execute permissions

### Analysis Errors
- Verify input file format (tab-separated values)
- Check that output folder has write permissions
- Ensure video length is entered correctly
- Review debug log file for technical details

### Performance
- Analysis time depends on file size (typically 1-5 minutes)
- Larger files may require more memory
- Close other applications if running low on RAM

## File Locations

After analysis, files are saved to your chosen output folder:
- `[filename]_flipfield_summary.txt` - Main results
- `[filename]_flip_field_analysis.csv` - Full data (if enabled)
- `[filename]_flipfield_analysis_debug_log.txt` - Technical log

## Support

For technical support or questions:
1. Check the debug log file first
2. Verify input file format
3. Try with a smaller test file
4. Contact the development team with:
   - Your operating system
   - Error messages
   - Debug log file

## Version Information

This is a standalone executable version that includes all necessary dependencies. No additional software installation is required.

---

**Note**: This application processes scientific data for magnetic bead flip analysis. Results should be validated against known controls and experimental conditions. 