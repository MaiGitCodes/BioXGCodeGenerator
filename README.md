# BIOX G-Code Generator
# v1.3.0
# Author: Maria Teresa Alameda Felgueiras
A specialized application for generating G-code scripts for Cellink BIOX bioprinters, supporting multiple printhead types and well plate configurations.

## Features

- 🖨️ **Multi-Printhead Support**:
  - EMD
  - Pneumatic
  - Thermo-controlled
  - Syringe Pump

- 🧪 **Well Plate Templates**:
  - Single drop deposition
  - 96-well plate (8×12)
  - 48-well plate (6×8)
  - u-Slide 8 Well
  - u-Slide Spheroid Perfusion
  - u-Slide 15 Well 3D
  - u-Slide 18 Well

- ⚙️ **Advanced Controls**:
  - Pressure, temperature, and time sweeps
  - Printhead and bed temperature control
  - Layer height adjustment
  - Printhead cleaning routine

- 📁 **Output Options**:
  - Generate G-code preview
  - Copy to clipboard
  - Export to .gcode file

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup
```bash
# Clone the repository
git clone https://github.com/MaiGitCodes/BioXGCodeGenerator.git
# Enter in the folder of the cloned repository
cd bio_x_gcode_generator
# Install the files in the repository
pip install -e .

# Install dependencies (in case Numpy or Customtkinter are not installed)
pip install -r requirements.txt

# To execute the application, for example in Spyder:
from BioXGCodeGenerator import main
main.main()
