# bio_x_gcode_generator/__init__.py

"""
BIOX G-Code Generator Package

A GUI application for generating G-code for Cellink BIOX bioprinters.
"""

__version__ = "1.3.0"
__author__ = "Maria Teresa Alameda Felgueiras"

# Import main components to make them available at package level
from .main import main
from .gui.layout import create_main_window
from .core.gcode import GCODE

