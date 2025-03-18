# BIOX GCode Generator

## Overview

The BIOX GCode Generator is a Python-based application designed to generate G-code for the BIO X bioprinter. It provides a user-friendly interface for configuring various printhead types, multi-well templates, and other printing parameters. The generated G-code can be copied to the clipboard or exported as a `.gcode` file for use with the BIO X bioprinter.

## Features

- **Printhead Type Selection**: Supports EMD, Pneumatic, Thermo-controlled, and Syringe Pump printheads.
- **Multi-well Templates**: Predefined templates for 96-well, 48-well, μ-Slide 8 Well, µ-Slide Spheroid Perfusion, μ-Slide 15 Well 3D, and μ-Slide 18 Well plates.
- **Parameter Configuration**: Set printhead speed, layer height, bed temperature, pressure, extrusion time, and more.
- **Pressure and Temperature Sweep**: Option to perform pressure or temperature sweeps across wells.
- **G-code Generation**: Generates G-code based on the selected parameters and template.
- **Copy to Clipboard**: Copy the generated G-code to the clipboard.
- **Export G-code**: Save the generated G-code as a `.gcode` file.
- **Dark Mode**: Toggle between light and dark mode for the user interface.

## Requirements

- Python 3.x
- `customtkinter` library
- `numpy` library

## Installation

1. Clone the repository or download the source code.
2. Install the required libraries using pip:

   pip install customtkinter numpy

3. Run the `BIOX_GCode_generator_last_functional_working_extrusion_v1.1.9.py` script:

   python BIOX_GCode_generator_last_functional_working_extrusion_v1.1.9.py

## Usage

1. **Select Printhead Type**: Choose the type of printhead you are using from the dropdown menu.
2. **Set Printhead Number**: Specify the printhead number (0-2).
3. **Choose Multi-well Template**: Select the appropriate multi-well template from the dropdown menu.
4. **Configure Parameters**: Enter the desired values for printhead speed, layer height, bed temperature, pressure, extrusion time, and other relevant parameters.
5. **Generate G-code**: Click the "Generate G-code" button to generate the G-code based on the selected parameters.
6. **Copy or Export G-code**: Use the "Copy to Clipboard" button to copy the G-code or the "Export G-code" button to save it as a `.gcode` file.

## File Structure

- `BIOX_GCode_generator_last_functional_working_extrusion_v1.1.9.py`: Main script containing the GUI and G-code generation logic.
- `gcode.py`: Contains the `GCODE` class with methods for generating G-code commands. This file handles the core G-code generation logic, including initialization, printhead settings, bed movement, and extrusion commands.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
