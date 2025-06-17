# **Bead Flip Detection System**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/yourusername/FlipField-Analysis)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GUI](https://img.shields.io/badge/GUI-tkinter%20%7C%20matplotlib-orange.svg)](FlipFieldGUI.py)

> **Application that analyzes the Flip Field for MyOne Dynabeads.**

## **Quick Start**

### **Installation**
```bash
# Clone the repository
git clone https://github.com/dtlo387/FlipField-Analysis.git
cd FlipField-Analysis/src

# Install dependencies
pip install -r requirements.txt

# Launch the application
python3 launch_gui.py
```

### **Sample Analysis**
The repository includes sample data (`Movie_2601.aviNB2.txt`) for immediate testing:

1. **Launch GUI**: Run `python3 launch_gui.py`
2. **Load Sample**: Browse and select the included sample file
3. **Configure**: Adjust parameters for your analysis needs
4. **Analyze**: Click "Analyze Flips" and monitor real-time progress
5. **Explore**: Review results across multiple visualization tabs
6. **Export**: Generate publication-ready reports and data

## **Usage**

### **Input Data Format**
```
Frame   X Position (px)   Y Position (px)   Angle (deg)
1       245.67           189.34            45.2
2       246.12           189.78            46.1
...
```

### **Parameter Guidance**
| Parameter | Range | Description |
|-----------|-------|-------------|
| Video Duration | 0.5-5.0 min | Total recording length |
| Analysis Start | 50-100 frames | Skip initial stabilization |
| Min Position Change | 1-5 px | Detection sensitivity |
| Pair Spacing | 40-50 frames | Biological constraint window |

### **Quality Assessment**
- **PERFECT**: ≥90% success rate
- **EXCELLENT**: 70-89% success rate  
- **GOOD**: 50-69% success rate
- **NEEDS IMPROVEMENT**: <50% success rate

## **Development**

### **Architecture**
- **Core Analysis**: `AnalyzingFlipField_Clean.py` - Scientific analysis engine
- **GUI Application**: `FlipFieldGUI.py` - Desktop interface with real-time features
- **Smart Launcher**: `launch_gui.py` - Dependency validation and error handling

### **Dependencies**
- **Python 3.7+**: Core runtime environment
- **tkinter**: Cross-platform GUI framework (usually included with Python)
- **matplotlib ≥3.5.0**: Scientific plotting and visualization
- **pandas ≥1.3.0**: Data manipulation and analysis
- **numpy ≥1.20.0**: Numerical computing foundation

## **Results & Validation**

### **Example Analysis Results**
- **10 flip pairs detected** with perfect 40-50 frame biological spacing
- **4 false positives eliminated** through exclusive pairing logic
- **75 total frames marked** as legitimate flip events
- **100% success rate** achieved on validation data

## **Repository Structure**

```
FlipField-Analysis/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .gitignore                  # Git ignore patterns
├── launch_gui.py               # Top-level launcher script
├── src/                        # Source code directory
│   ├── FlipFieldGUI.py         # Main GUI application
│   ├── AnalyzingFlipField_Clean.py # Core analysis engine
│   └── launch_gui.py           # Main launcher with dependency checking
├── examples/                   # Sample data and examples
│   └── Movie_2601.aviNB2.txt   # Sample tracking data
└── docs/                       # Documentation
    ├── README_GUI.md           # Detailed GUI user guide
    └── GUI_FEATURES_SUMMARY.md # Complete feature overview
```

## **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## **Support**

- **Documentation**: Check the comprehensive [GUI Guide](docs/README_GUI.md)
- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: GitHub Discussions for general questions and usage tips
