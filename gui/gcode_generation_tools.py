#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GCODE generation functions

@author: Maria Teresa Alameda Felgueiras
"""

import numpy as np
import customtkinter as ctk
from ..core.gcode import GCODE as GC
from ..core.gcode import clean_printhead
from ..core.templates import set_template
from .validation import validate_inputs


def generate_scaffold_gcode(components):
    
    printhead_type = components['printhead_type'].get()
    printhead_number = int(components['printhead_number'].get())
    
    pattern = components['scaffold_pattern_var'].get()
    extrusion = float(components['scaffold_extrusion_entry'].get())
    height = float(components['scaffold_layer_height_entry'].get())
    speed = float(components['scaffold_speed_entry'].get())
    layers = int(components['layer_number_entry'].get())
        
    dimensions, origin, extrusion = calculate_geometric_parameters(components)
    lines, delta = calculate_lines(components)
    
    gcode = GC.initialize(printhead_type_value = printhead_type, pattern = pattern)
    
    gcode = GC.set_printhead(gcode, printhead_number, z = height)
        
    for layer in range(layers):
        
        layer_height = (layer + 1) * height
        gcode = GC.introduce_comment(gcode, f"Printing layer at height {layer_height} mm")
        
        gcode = GC.move_to_position(gcode, z = layer_height + 1, speed = 3000, precise = 1)
        gcode = GC.move_to_position(gcode, x = origin[0], y = origin[1], speed = 3000, precise = 1)
        gcode = GC.move_to_position(gcode, z = layer_height, speed = 3000, precise = 1)
                
        gcode = GC.generate_scafold_perimeter(gcode, dimensions, origin, extrusion, layer_height,
                                              speed = speed)
        
        gcode = GC.move_to_position(gcode, z = layer_height + 1, speed = 3000, precise = 1)
        
        if pattern.lower() == 'striped':
            gcode = GC.generate_striped_scaffold(gcode, dimensions, origin,
                                             delta, lines, layer_height, speed = speed)
        elif pattern.lower() == 'grid':
             gcode = GC.generate_grid_scaffold(gcode, dimensions, origin,
                                              delta, lines, layer_height, speed = speed)
        else:
            pass
        
    
    gcode = GC.terminate(gcode, components)
    
    # Display generated G-code
    components['gcode_text'].delete("1.0", ctk.END)
    components['gcode_text'].insert(ctk.END, gcode)

def generate_droplet_gcode(components):
    
    """Generate G-code based on current settings"""
        
    # Printhead-specific settings
    printhead_type_value = components['printhead_type'].get()
    printhead_number = int(components['printhead_number'].get())
    bed_movement_position = float(components['bed_zpos_entry'].get())
    clean_printhead_bool = components['clean_printhead_var'].get()
    
    # Handle sweep parameters
    pressure_sweep = components['pressure_sweep_var'].get()
    temperature_sweep = components['temperature_sweep_var'].get()
    extrusion_time_sweep = components['extrusion_time_sweep_var'].get()
       
    gcode = GC.initialize(printhead_type_value=printhead_type_value)
    
    # Get selected template
    template_properties, gcode = set_template(components['template_var'].get(), gcode)
    rows = template_properties['rows']
    cols = template_properties['cols']
    well_spacing_x = template_properties['well_spacing_x']
    well_spacing_y = template_properties['well_spacing_y']
    
    # Calculate starting position to center the plate
    start_x = 0.
    start_y = 0.
           
    gcode = GC.set_printhead(gcode, printhead=printhead_number)
    
    # Check if any sweep is active
    any_sweep_active = (pressure_sweep or temperature_sweep or extrusion_time_sweep)
    
    # Only set temperatures if no sweep is active
    if not any_sweep_active:
        if components['control_bedtemperature_var'].get():
            gcode = GC.set_bed_temperature(gcode, 
            float(
                components['bed_temp_entry'].get()
                )
            )
            
        if components['control_phtemperature_var'].get():
            gcode = GC.set_printhead_temperature(
                gcode, 
                float(components['phtemp_entry'].get()),
                printhead_number
            )
    
    if not pressure_sweep: 
        gcode = GC.set_default_pressure(
            gcode,
            float(components['pressure_entry'].get())
            )
    
    # Generate sweep arrays based on direction
    if pressure_sweep:
        initial_pressure = float(components['pressure_initial_entry'].get())
        final_pressure = float(components['pressure_final_entry'].get())
        direction = components['pressure_sweep_dir'].get()
        
        if direction == "row":
            pressures = np.linspace(initial_pressure, final_pressure, rows)
            pressures = np.repeat(pressures, cols)
        elif direction == "column":
            pressures = np.linspace(initial_pressure, final_pressure, cols)
            pressures = np.tile(pressures, rows)
        else:  # "well"
            pressures = np.linspace(initial_pressure, final_pressure, rows*cols)
            
        temperatures = [float(components['phtemp_entry'].get())] * (rows*cols) if components['control_phtemperature_var'].get() else [None] * (rows*cols)
        extrusion_times = [float(components['extrusion_time_entry'].get())] * (rows*cols)
        
    elif temperature_sweep:
        initial_temp = float(components['temperature_initial_entry'].get())
        final_temp = float(components['temperature_final_entry'].get())
        direction = components['temp_sweep_dir'].get()
        
        if direction == "row":
            temperatures = np.linspace(initial_temp, final_temp, rows)
            temperatures = np.repeat(temperatures, cols)
        elif direction == "column":
            temperatures = np.linspace(initial_temp, final_temp, cols)
            temperatures = np.tile(temperatures, rows)
        else:  # "well"
            temperatures = np.linspace(initial_temp, final_temp, rows*cols)
            
        pressures = [float(components['pressure_entry'].get())] * (rows*cols)
        extrusion_times = [float(components['extrusion_time_entry'].get())] * (rows*cols)
        
    elif extrusion_time_sweep:
        initial_time = float(components['extrusion_time_initial_entry'].get())
        final_time = float(components['extrusion_time_final_entry'].get())
        direction = components['time_sweep_dir'].get()
        
        if direction == "row":
            extrusion_times = np.linspace(initial_time, final_time, rows)
            extrusion_times = np.repeat(extrusion_times, cols)
        elif direction == "column":
            extrusion_times = np.linspace(initial_time, final_time, cols)
            extrusion_times = np.tile(extrusion_times, rows)
        else:  # "well"
            extrusion_times = np.linspace(initial_time, final_time, rows*cols)
            
        pressures = [float(components['pressure_entry'].get())] * (rows*cols)
        temperatures = [float(components['phtemp_entry'].get())] * (rows*cols) if components['control_phtemperature_var'].get() else [None] * (rows*cols)
        
    else:
        pressures = [float(components['pressure_entry'].get())] * (rows*cols)
        temperatures = [float(components['phtemp_entry'].get())] * (rows*cols) if components['control_phtemperature_var'].get() else [None] * (rows*cols)
        extrusion_times = [float(components['extrusion_time_entry'].get())] * (rows*cols)

    # Generate G-code for printing over the wells
    gcode = GC.set_printhead_speed(gcode, components['printhead_speed_entry'].get())
    
    if clean_printhead_bool:
        gcode = clean_printhead(
            gcode, 
            printhead_number,
            components['printhead_speed_entry'].get(),
            bed_movement_position
        )
           
    counter = 0
    for row in range(rows):
        for col in range(cols):
            x = start_x + col * well_spacing_x
            y = start_y + row * well_spacing_y
            z = float(components['layer_height_entry'].get())

            gcode = GC.move_to_position(
                gcode, 
                x, 
                y,
                speed=components['printhead_speed_entry'].get(), 
                row=row, 
                col=col
            )
            
            # Update temperature if doing temperature sweep and temperature is specified
            if temperature_sweep and temperatures[counter] is not None:
                gcode = GC.set_printhead_temperature(
                    gcode, 
                    temperatures[counter], 
                    printhead_number
                )
                gcode += "M400 ; wait for temperature change\n"
            
            # Extrude material in the well
            if printhead_type_value == "EMD":
                gcode = GC.move_bed(
                    gcode, 
                    z=0, 
                    speed=components['printhead_speed_entry'].get()
                )
                gcode = GC.emd_extrusion(
                    gcode,
                    printhead_number,
                    float(pressures[counter]),
                    float(extrusion_times[counter])
                )
                gcode = GC.move_bed(
                    gcode, 
                    z=bed_movement_position, 
                    speed=components['printhead_speed_entry'].get()
                )
                
            elif printhead_type_value == "Pneumatic":
                gcode = GC.move_bed(
                    gcode, 
                    z, 
                    speed=components['printhead_speed_entry'].get()
                )
                gcode = GC.pneumatic_extrusion(
                    gcode,
                    printhead_number,
                    float(pressures[counter]),
                    float(extrusion_times[counter])
                )
                gcode = GC.move_bed(
                    gcode, 
                    z=bed_movement_position, 
                    speed=components['printhead_speed_entry'].get()
                )
            
            elif printhead_type_value == "Thermo-controlled":
                gcode = GC.move_bed(
                    gcode, 
                    z, 
                    speed=components['printhead_speed_entry'].get()
                )
                gcode = GC.thermo_extrusion(
                    gcode,
                    printhead_number,
                    float(pressures[counter]),
                    float(extrusion_times[counter])
                )
                gcode = GC.move_bed(
                    gcode, 
                    z=bed_movement_position, 
                    speed=components['printhead_speed_entry'].get()
                )
                
            elif printhead_type_value == "Syringe Pump":
                gcode += f"G1 E{10 * float(extrusion_times[counter])} F100 ; Extrude material\n"
            
            counter += 1

    # Introduce termination commands
    gcode = GC.terminate(gcode, components, any_sweep_active=any_sweep_active)

    # Display generated G-code
    components['gcode_text'].delete("1.0", ctk.END)
    components['gcode_text'].insert(ctk.END, gcode)
    
    
def calculate_geometric_parameters(components):
    
    deltax = float(components['scaffold_size_entry'].get())
    deltay = float(components['scaffold_size_entry'].get())
    extrusion = float(components['scaffold_noozle_entry'].get())

    
    x0 = deltax/2 - extrusion/2
    y0 = deltay/2 - extrusion/2
    dimensions = (deltax - extrusion, deltay - extrusion)
    origin = (x0, y0)
    
    return dimensions, origin, extrusion

def calculate_lines(components, pattern='striped'):
    infill = float(components['scaffold_infill_entry'].get())
    deltax = float(components['scaffold_size_entry'].get())
    deltay = float(components['scaffold_size_entry'].get())
    extrusion = float(components['scaffold_noozle_entry'].get())
    
    dimensions = (deltax - extrusion, deltay - extrusion)
    effective_size = deltax - extrusion 
    
    if pattern.lower() == 'striped':
        line_area = extrusion * dimensions[1]
        number_of_lines = round((dimensions[0] * dimensions[1] * infill/100) / line_area)
        delta = dimensions[0] / number_of_lines
        return number_of_lines, delta
    
    elif pattern.lower() == 'grid':
        line_area = extrusion * (dimensions[0] + dimensions[1])  # One horizontal and one vertical line
        number_of_lines = round((dimensions[0] * dimensions[1] * infill/100) / line_area)
        delta = dimensions[0] / number_of_lines
        return number_of_lines, delta
    
    elif pattern.lower() == 'honeycomb':
        # Honeycomb-specific calculations
        # Relationship between infill and wall length: infill = (wall_length * extrusion)/area
        # For honeycomb, wall_length per unit area = (4 + 2√3)/(3√3 * s) where s is spacing
        
        # Calculate required spacing to achieve desired infill
        spacing = (4 + 2*np.sqrt(3)) / (3*np.sqrt(3)) * extrusion / (infill/100)
        
        # Calculate number of complete hexagons that fit
        hex_width = spacing * np.sqrt(3)  # width between opposite sides
        hex_height = spacing * 2          # height between opposite vertices
        
        # Number of horizontal lines
        n_horizontal = int((effective_size - extrusion) / (hex_height * 0.75)) + 1
        
        # Number of vertical lines (diagonals)
        n_vertical = int((effective_size - extrusion) / (hex_width * 0.5)) + 1
        
        return (n_horizontal + n_vertical), spacing
    

def calculate_cells(infill, extrusion, infill_area):
    
    infill /= 100
    
    unit_cell_side =  2 * extrusion + np.sqrt((2 * extrusion) ** 2 - 4 * infill * extrusion ** 2 )
    
    unit_cell_side /= (2 * infill)
    
    n = infill_area / unit_cell_side ** 2
    
    return n
    
def calculate_honeycomb_lines(components):
    
    """Calculate number of lines and spacing for honeycomb pattern"""
    
    infill = float(components['scaffold_infill_entry'].get()) / 100
    size = float(components['scaffold_size_entry'].get())
    extrusion = float(components['scaffold_noozle_entry'].get())
    
    # Honeycomb specific calculations
    # The relationship between infill and line spacing is different for honeycomb
    # This is an approximation - you may need to adjust based on your exact requirements
    effective_spacing = (extrusion * (1 - infill)) / infill
    
    # Number of lines is approximately the size divided by the effective spacing
    number_of_lines = round(size / effective_spacing)
    
    # Ensure we have at least 1 line
    number_of_lines = max(1, number_of_lines)
    
    # Calculate actual spacing
    delta = size / number_of_lines
    
    return number_of_lines, delta
    
    
    
    
    
    
    
    
    