#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constants and configuration for BIOX G-Code Generator

@author: Maria Teresa Alameda Felgueiras
"""

APP_TITLE = "Cellink BIOX GCode Generator"

DEFAULT_MODE = "light"
DEFAULT_COLOR = "blue"

PRINTHEAD_TYPES = [
    "EMD",
    "Pneumatic",
    "Thermo-controlled",
    "Syringe Pump"
]
PRINTHEAD_DEFAULT = "EMD"

TEMPLATE_PROPERTIES = {
    "One drop": {
        'rows': 1,
        'cols': 1,
        'well_spacing_x': 0,
        'well_spacing_y': 0,
        'plate_length': 0,
        'plate_width': 0,
        'description': "Single drop deposition"
    },
    "96-well plate": {
        'rows': 8,
        'cols': 12,
        'well_spacing_x': 9,       # mm (center-to-center spacing)
        'well_spacing_y': 9,       # mm (center-to-center spacing)
        'plate_length': 127.76,    # mm (full plate length)
        'plate_width': 85.48,      # mm (full plate width)
        'description': "Standard 96-well plate (8x12 configuration)"
    },
    "48-well plate": {
        'rows': 6,
        'cols': 8,
        'well_spacing_x': 18.16,   # mm (center-to-center spacing)
        'well_spacing_y': 18.16,   # mm (center-to-center spacing)
        'plate_length': 127.76,    # mm (full plate length)
        'plate_width': 85.48,      # mm (full plate width)
        'description': "Standard 48-well plate (6x8 configuration)"
    },
    "u-Slide 8 Well": {
        'rows': 2,
        'cols': 4,
        'well_spacing_x': 19,      # mm (center-to-center spacing)
        'well_spacing_y': 19,      # mm (center-to-center spacing)
        'plate_length': 75.5,      # mm (full slide length)
        'plate_width': 25.5,       # mm (full slide width)
        'description': "ibidi u-Slide 8 Well plate (2x4 configuration)"
    },
    "u-Slide Spheroid Perfusion": {
        'rows': 3,
        'cols': 7,                 # 3 rows with 7 wells each
        'well_spacing_x': 4.5,     # mm (spacing between wells in a row)
        'well_spacing_y': 9.0,     # mm (spacing between rows)
        'plate_length': 75.5,      # mm (full slide length)
        'plate_width': 25.5,       # mm (full slide width)
        'description': "ibidi u-Slide Spheroid Perfusion plate (3x7 configuration)"
    },
    "u-Slide 15 Well 3D": {
        'rows': 3,
        'cols': 5,                 # 3 rows with 5 wells each
        'well_spacing_x': 9,       # mm (spacing between wells in a row)
        'well_spacing_y': 7,       # mm (spacing between rows)
        'plate_length': 75.5,      # mm (full slide length)
        'plate_width': 25.5,       # mm (full slide width)
        'description': "ibidi u-Slide 15 Well 3D plate (3x5 configuration)"
    },
    "u-Slide 18 Well": {
        'rows': 3,
        'cols': 6,                 # 3 rows with 6 wells each
        'well_spacing_x': 8.10,    # mm (spacing between wells in a row)
        'well_spacing_y': 7.45,    # mm (spacing between rows)
        'plate_length': 75.5,      # mm (full slide length)
        'plate_width': 25.5,       # mm (full slide width)
        'description': "ibidi u-Slide 18 Well plate (3x6 configuration)"
    }
}


# Temperature limits
BED_TEMP_LIMITS = (4, 65)
PH_TEMP_LIMITS = {
    "EMD": (30, 65),
    "Pneumatic": (30, 65),
    "Syringe Pump": (30, 65),
    "Thermo-controlled": (4, 65)
}

# Add this line to create TEMPLATE_NAMES
TEMPLATE_NAMES = sorted(TEMPLATE_PROPERTIES.keys())