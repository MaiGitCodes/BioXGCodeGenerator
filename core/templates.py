#!/usr/bin/env python3
"""
Template management for BIOX G-Code Generator

@author: Maria Teresa Alameda Felgueiras
"""
from ..utils.constants import TEMPLATE_PROPERTIES

def set_template(template_name, gcode):
    """
    Get properties for the selected template and update G-code
    
    Returns:
        tuple: (rows, cols, well_spacing_x, well_spacing_y, plate_length, plate_width)
        str: Updated G-code
    """
    gcode += f"\n; {template_name} template selected\n\n"
    
    if template_name not in TEMPLATE_PROPERTIES:
        raise ValueError(f"Unknown template: {template_name}")
    
    properties = TEMPLATE_PROPERTIES[template_name]
    return properties, gcode

def get_available_templates():
    """Return list of available template names"""
    return list(TEMPLATE_PROPERTIES.keys())
