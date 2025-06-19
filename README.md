# **Flip Field Analysis**

> **Application that analyzes the Flip Field for MyOne Dynabeads.**

This program takes the output text files from [@benonymity's Dynabeads Tracking Program](https://github.com/benonymity/dynabeads) and identifies when a bead flips based on pixel distance, speed calculations, and pattern recognition. The program will also provide a confidence rating based on the parameters mentioned above.

## Usage

You can download the latest executable for your OS from [releases](https://github.com/dtlo387/FlipField-Analysis/releases). Please note that the startup times can be ... less than ideal due to it running on Python. Just give it some patience. Once it finishes initializing, you should see a simple and self-explanatory GUI. 

If you need further help, download the DISTRIBUTION_README.md under [releases](https://github.com/dtlo387/FlipField-Analysis/releases). 

## Develop
If you're having trouble downloading the executable or you just want to play with the source code, you can run the script in your own Python environment.

### **Installation**
```bash
# Clone the repository
git clone https://github.com/dtlo387/FlipField-Analysis.git

# Install dependencies
pip install -r requirements.txt

# Change the directory to the /src
cd FlipField-Analysis/src

# Launch the application
python3 FlipFieldGUI.py
```

## **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
