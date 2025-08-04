# BIOX G-Code Generator
# v1.3.7
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

- 🧱 **Scaffold Structure Generator** (🔧 *Beta*):
  - Generate stripped scaffold patterns across multiple layers
  - Generate grid scaffold patterns across multiple layers
  - Current version includes support for linear scaffolds (e.g., striped/gridded)
  - Other geometries like honeycomb and circular are planned but not yet implemented

- 🧊 **3D Visualization**:
  - Interactive window for 3D preview of scaffold structures
  - Rotate, zoom, and inspect the generated paths before printing
  - Able and disable grid and axes
  - Export scaffold pre-visualization as PNG.

- 📁 **Output Options**:
  - Generate G-code preview
  - Copy to clipboard
  - Export to `.gcode` file

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup
```bash
# In conda, install git (if using anaconda, recommended):
conda install -c anaconda git
# Or, with pip, install gitpython:
pip install gitpython
# Clone the repository
git clone https://github.com/MaiGitCodes/BioXGCodeGenerator.git
# Enter in the folder of the cloned repository
cd bio_x_gcode_generator
# Install the files in the repository
pip install -e .

# Install dependencies (in case Numpy or Customtkinter are not installed)
pip install -r requirements.txt

# To execute the application, for example in Spyder:
import BioXGCodeGenerator as bgc
bgc.main()
