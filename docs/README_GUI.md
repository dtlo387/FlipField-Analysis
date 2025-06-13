# 🧬 Bead Flip Detection System - Desktop GUI

A powerful, cross-platform desktop application for analyzing bead flip events from video tracking data with real-time progress monitoring and advanced visualization.

## ✨ Features

### 🎯 **Core Analysis**
- **Customizable Parameters**: Adjust analysis start frame, video duration, detection sensitivity
- **Real-time Progress**: Live progress tracking with detailed status updates
- **Intelligent Filtering**: Removes false positives using biological constraints
- **Quality Assessment**: Automatic quality scoring (PERFECT/EXCELLENT/GOOD/NEEDS IMPROVEMENT)

### 📊 **Visualization & Results**
- **Interactive Timeline**: Visual timeline of flip events vs. magnetic field strength
- **Comprehensive Dashboard**: Field-by-field results with success rates
- **Detailed Analysis**: Complete breakdown of detection statistics and parameters
- **Real-time Updates**: Progress visualization during analysis

### 💾 **Export Options**
- **CSV Data Export**: Complete dataframe with tracking and flip data
- **Field Categorization**: Mapping of field strengths to flip events
- **Analysis Summary**: Comprehensive report with all statistics
- **Timeline Plots**: High-resolution PNG exports of visualizations

### 🖥️ **Cross-Platform Compatibility**
- **Windows**: Native tkinter support
- **macOS**: Optimized for Retina displays
- **Linux**: Full compatibility with major distributions

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Quick Install
```bash
# Clone the repository
git clone <your-repo-url>
cd FlipField-Code

# Install dependencies
pip install -r requirements.txt

# Run the application
python FlipFieldGUI.py
```

### Alternative: Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv flipfield_env

# Activate (Windows)
flipfield_env\Scripts\activate

# Activate (macOS/Linux)
source flipfield_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python FlipFieldGUI.py
```

## 📖 Usage Guide

### 1️⃣ **Loading Data**
1. Click **"Browse..."** to select your tracking data file (`.txt` format)
2. Adjust **video duration** to match your recording length
3. Set **analysis window** (start frame and end skip frames)

### 2️⃣ **Parameter Tuning**
- **Min Position Change**: Sensitivity threshold (1-10 pixels)
- **Pair Spacing**: Expected frame separation between flip pairs (40-50 frames typical)
- **Detection Parameters**: Fine-tune for your specific experimental conditions

### 3️⃣ **Running Analysis**
1. Click **🔍 Analyze Flips** to start
2. Monitor real-time progress in the progress bar
3. View live updates in the analysis log
4. Analysis typically completes in 10-30 seconds

### 4️⃣ **Reviewing Results**
- **Field Strength Results**: Table view of all tested field strengths
- **Flip Timeline**: Visual representation of successful flips
- **Detailed Analysis**: Comprehensive statistics and parameters

### 5️⃣ **Exporting Data**
1. Select desired export options (CSV, Categorization, Summary)
2. Click **💾 Export Results**
3. Choose export directory
4. Files are saved with timestamps for organization

## 🔧 Advanced Configuration

### Input File Format
Expected format for tracking data:
```
Frame   X Position (px)   Y Position (px)   Angle (deg)
1       245.67           189.34            45.2
2       246.12           189.78            46.1
...
```

### Parameter Guidelines

| Parameter | Typical Range | Description |
|-----------|---------------|-------------|
| Video Duration | 0.5-5.0 min | Total recording length |
| Start Frame | 50-100 | Skip initial stabilization |
| End Skip | 50-100 | Skip final frames |
| Min Position Change | 1-5 px | Detection sensitivity |
| Pair Spacing Min | 35-45 frames | Minimum flip separation |
| Pair Spacing Max | 45-55 frames | Maximum flip separation |

### Quality Assessment
- **PERFECT**: ≥90% success rate - Excellent experimental conditions
- **EXCELLENT**: 70-89% success rate - Good data quality
- **GOOD**: 50-69% success rate - Acceptable with some noise
- **NEEDS IMPROVEMENT**: <50% success rate - Check parameters/data quality

## 📊 Understanding Results

### Field Strength Results Table
Shows each tested magnetic field strength with:
- ✅ **FLIPPED**: Successful flip detection
- ❌ **NO FLIP**: No valid flip detected
- **Frame Number**: Center frame of detected flip
- **Success Rate**: Individual field performance

### Timeline Visualization
- **Green dots**: Successful flip events
- **Red X marks**: Failed detections
- **Blue dashed lines**: Connection between consecutive flips
- **Statistics box**: Overall success metrics

### Detailed Analysis
Comprehensive breakdown including:
- Input parameters and file information
- Field-by-field results with frame numbers
- Raw detection statistics
- Group analysis and pairing results
- Noise filtering statistics
- Quality assessment explanation

## 🐛 Troubleshooting

### Common Issues

**"No analysis results to export"**
- Ensure analysis completed successfully
- Check that file was loaded properly

**"Analysis failed" errors**
- Verify input file format matches expected structure
- Check file permissions and path accessibility
- Ensure all required columns are present

**Poor detection results**
- Adjust sensitivity parameters (Min Position Change)
- Modify pair spacing range for your experimental setup
- Check video duration matches actual recording length

**GUI not responding**
- Analysis runs in background - wait for completion
- Check system resources (memory/CPU usage)
- Restart application if needed

### Performance Tips
- Use SSD storage for faster file access
- Close other applications during analysis
- For large files (>100MB), increase system RAM allocation

## 🔬 Technical Details

### Analysis Pipeline
1. **Data Loading**: Parse tracking data with frame rate calculation
2. **Raw Detection**: Basic flip detection with noise filtering
3. **Group Formation**: Cluster nearby detections into coherent events
4. **Exclusive Pairing**: Match groups using biological spacing patterns
5. **Field Categorization**: Map paired groups to magnetic field strengths
6. **Quality Assessment**: Calculate success rates and generate reports

### Threading Architecture
- **Main Thread**: GUI updates and user interaction
- **Analysis Thread**: Background processing with progress callbacks
- **Queue Communication**: Thread-safe progress updates

## 📝 Output Files

### CSV Data Export
Complete dataframe with columns:
- Frames, X Position, Y Position, Angle
- Velocities, Speed, Time formatting
- Flip detection booleans (X and Y axes)

### Field Categorization
Text report mapping field strengths to flip events with frame numbers and success statistics.

### Analysis Summary
Comprehensive report including all parameters, results, and metadata for reproducibility.

### Timeline Plots
High-resolution PNG exports suitable for publications and presentations.

## 📞 Support

For issues, questions, or feature requests:
- Check this README for common solutions
- Review parameter guidelines for optimization
- Ensure input data format matches specifications

## 🏗️ Development

Built with:
- **Python 3.7+**: Core language
- **tkinter**: Cross-platform GUI framework
- **matplotlib**: Scientific plotting and visualization
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing

---

*Developed for advanced bead flip detection analysis with focus on usability, accuracy, and cross-platform compatibility.* 