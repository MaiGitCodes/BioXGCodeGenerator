#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete input validation for BIOX G-Code Generator

@author: Maria Teresa Alameda Felgueiras
"""
import customtkinter as ctk
from tkinter import messagebox  # Add this import
from ..utils.constants import (BED_TEMP_LIMITS, PH_TEMP_LIMITS)

def validate_inputs(components):
    """
    Validate all mandatory inputs before generating G-code
    
    Returns:
        bool: True if all inputs are valid, False otherwise
    """
    try:
        # Check if any sweep is active
        any_sweep_active = (components['pressure_sweep_var'].get() or 
                          components['temperature_sweep_var'].get() or
                          components['extrusion_time_sweep_var'].get())

        # Validate printhead number
        printhead_number = components['printhead_number'].get()
        if not printhead_number.isdigit() or not (0 <= int(printhead_number) <= 2):
            raise ValueError("Printhead number must be between 0 and 2.")

        # Validate print speed
        printhead_speed = components['printhead_speed_entry'].get()
        if not is_float(printhead_speed) or not (0 < float(printhead_speed) <= 1500):
            raise ValueError("Print speed must be between 0 and 1500 mm/s.")

        # Validate layer height
        layer_height = components['layer_height_entry'].get()
        if not is_float(layer_height) or not (0.1 <= float(layer_height) <= 1.0):
            raise ValueError("Layer height must be between 0.1 and 1.0 mm.")

        # Validate bed movement position
        bed_position = components['bed_zpos_entry'].get()
        if not is_float(bed_position) or float(bed_position) <= 0:
            raise ValueError("Bed position must be greater than 0.")

        # Validate pressure
        pressure = components['pressure_entry'].get()
        if not is_float(pressure) or not (0 <= float(pressure) <= 200):
            raise ValueError("Pressure must be between 0 and 200 kPa.")

        # Validate extrusion time
        extrusion_time = components['extrusion_time_entry'].get()
        if not is_float(extrusion_time) or float(extrusion_time) <= 0:
            raise ValueError("Extrusion time must be greater than 0 seconds.")

        # Only validate temperature controls if no sweep is active
        if not any_sweep_active:
            # Validate bed temperature if enabled
            if components['control_bedtemperature_var'].get():
                bed_temp = components['bed_temp_entry'].get()
                if not is_float(bed_temp) or not (BED_TEMP_LIMITS[0] <= float(bed_temp) <= BED_TEMP_LIMITS[1]):
                    raise ValueError(f"Bed temperature must be between {BED_TEMP_LIMITS[0]} and {BED_TEMP_LIMITS[1]} °C.")

            # Validate printhead temperature if enabled
            if components['control_phtemperature_var'].get():
                ph_temp = components['phtemp_entry'].get()
                ph_limits = PH_TEMP_LIMITS.get(components['printhead_type'].get(), (30, 65))
                if not is_float(ph_temp) or not (ph_limits[0] <= float(ph_temp) <= ph_limits[1]):
                    raise ValueError(f"Printhead temperature must be between {ph_limits[0]} and {ph_limits[1]} °C.")

        # Validate sweep parameters if enabled
        if components['pressure_sweep_var'].get():
            validate_sweep_parameters(
                components['pressure_initial_entry'].get(),
                components['pressure_final_entry'].get(),
                "Pressure"
            )
            
        if components['temperature_sweep_var'].get():
            validate_sweep_parameters(
                components['temperature_initial_entry'].get(),
                components['temperature_final_entry'].get(),
                "Temperature"
            )
            
        if components['extrusion_time_sweep_var'].get():
            validate_sweep_parameters(
                components['extrusion_time_initial_entry'].get(),
                components['extrusion_time_final_entry'].get(),
                "Extrusion time"
            )

        return True
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))
        return False

def validate_input_fields(components):
    """
    Validate individual input fields and highlight invalid values in red
    """
    # Printhead number validation
    printhead_number = components['printhead_number'].get()
    if printhead_number.isdigit():
        printhead_number = int(printhead_number)
        if not (0 <= printhead_number <= 2):
            set_invalid(components['printhead_number_menu'])
        else:
            set_valid(components['printhead_number_menu'])
    else:
        set_invalid(components['printhead_number_menu'])

    # Print speed validation
    printhead_speed = components['printhead_speed_entry'].get()
    if is_float(printhead_speed):
        printhead_speed = float(printhead_speed)
        if not (0 < printhead_speed <= 1500):
            set_invalid(components['printhead_speed_entry'])
        else:
            set_valid(components['printhead_speed_entry'])
    elif printhead_speed == "":
        set_valid(components['printhead_speed_entry'])
    else:
        set_invalid(components['printhead_speed_entry'])

    # Layer height validation
    layer_height = components['layer_height_entry'].get()
    if is_float(layer_height):
        layer_height = float(layer_height)
        if not (0.1 <= layer_height <= 1.0):
            set_invalid(components['layer_height_entry'])
        else:
            set_valid(components['layer_height_entry'])
    elif layer_height == "":
        set_valid(components['layer_height_entry'])
    else:
        set_invalid(components['layer_height_entry'])

    # Pressure validation
    pressure = components['pressure_entry'].get()
    if is_float(pressure):
        pressure = float(pressure)
        if not (0 <= pressure <= 200):
            set_invalid(components['pressure_entry'])
        else:
            set_valid(components['pressure_entry'])
    elif pressure == "":
        set_valid(components['pressure_entry'])
    else:
        set_invalid(components['pressure_entry'])

    # Extrusion time validation
    extrusion_time = components['extrusion_time_entry'].get()
    if is_float(extrusion_time):
        if float(extrusion_time) <= 0:
            set_invalid(components['extrusion_time_entry'])
        else:
            set_valid(components['extrusion_time_entry'])
    elif extrusion_time == "":
        set_valid(components['extrusion_time_entry'])
    else:
        set_invalid(components['extrusion_time_entry'])

    # Bed position validation
    bed_position = components['bed_zpos_entry'].get()
    if is_float(bed_position):
        if float(bed_position) <= 0:
            set_invalid(components['bed_zpos_entry'])
        else:
            set_valid(components['bed_zpos_entry'])
    elif bed_position == "":
        set_valid(components['bed_zpos_entry'])
    else:
        set_invalid(components['bed_zpos_entry'])

    # Printhead-specific validation
    printhead_type_value = components['printhead_type'].get()
    
    # Bed temperature validation
    bed_temp = components['bed_temp_entry'].get()
    if is_float(bed_temp):
        bed_temp = float(bed_temp)
        if not (BED_TEMP_LIMITS[0] <= bed_temp <= BED_TEMP_LIMITS[1]):
            set_invalid(components['bed_temp_entry'])
        else:
            set_valid(components['bed_temp_entry'])
    elif bed_temp == "":
        set_valid(components['bed_temp_entry'])
    else:
        set_invalid(components['bed_temp_entry'])

    # Printhead temperature validation
    ph_temp = components['phtemp_entry'].get()
    if is_float(ph_temp):
        ph_temp = float(ph_temp)
        ph_limits = PH_TEMP_LIMITS.get(printhead_type_value, (30, 65))
        if not (ph_limits[0] <= ph_temp <= ph_limits[1]):
            set_invalid(components['phtemp_entry'])
        else:
            set_valid(components['phtemp_entry'])
    elif ph_temp == "":
        set_valid(components['phtemp_entry'])
    else:
        set_invalid(components['phtemp_entry'])

    # Sweep parameters validation
    if components['pressure_sweep_var'].get():
        validate_sweep_fields(
            components['pressure_initial_entry'],
            components['pressure_final_entry'],
            components['pressure_initial_entry'],
            components['pressure_final_entry']
        )
        
    if components['temperature_sweep_var'].get():
        validate_sweep_fields(
            components['temperature_initial_entry'],
            components['temperature_final_entry'],
            components['temperature_initial_entry'],
            components['temperature_final_entry']
        )
        
    if components['extrusion_time_sweep_var'].get():
        validate_sweep_fields(
            components['extrusion_time_initial_entry'],
            components['extrusion_time_final_entry'],
            components['extrusion_time_initial_entry'],
            components['extrusion_time_final_entry']
        )

def validate_sweep_parameters(initial, final, param_name):
    """
    Validate sweep parameters (initial and final values)
    
    Args:
        initial (str): Initial value
        final (str): Final value
        param_name (str): Name of the parameter being validated
    """
    if not initial or not final:
        raise ValueError(f"Both initial and final {param_name.lower()} must be specified for sweep.")
    
    if not is_float(initial) or not is_float(final):
        raise ValueError(f"{param_name} values must be numbers.")
    
    initial_val = float(initial)
    final_val = float(final)
    
    if initial_val < 0:
        raise ValueError(f"Initial {param_name.lower()} cannot be negative.")
    
    if final_val <= 0:
        raise ValueError(f"Final {param_name.lower()} must be greater than 0.")
    
    if initial_val >= final_val:
        raise ValueError(f"Initial {param_name.lower()} must be less than final value.")

def validate_sweep_fields(initial_entry, final_entry, initial_component, final_component):
    """
    Validate sweep fields and highlight appropriately
    """
    initial = initial_entry.get()
    final = final_entry.get()
    
    if initial and final:
        if is_float(initial) and is_float(final):
            initial_val = float(initial)
            final_val = float(final)
            
            if initial_val < 0 or final_val <= 0 or initial_val >= final_val:
                set_invalid(initial_component)
                set_invalid(final_component)
            else:
                set_valid(initial_component)
                set_valid(final_component)
        else:
            set_invalid(initial_component)
            set_invalid(final_component)
    else:
        set_valid(initial_component)
        set_valid(final_component)

def is_float(value):
    """Check if a string can be converted to float"""
    try:
        float(value)
        return True
    except ValueError:
        return False

def set_valid(component):
    """Set component to valid state (default appearance)"""
    if isinstance(component, ctk.CTkEntry):
        component.configure(
            fg_color=ctk.ThemeManager.theme["CTkEntry"]["fg_color"],
            text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"]
        )
    elif isinstance(component, ctk.CTkOptionMenu):
        component.configure(
            text_color=ctk.ThemeManager.theme["CTkOptionMenu"]["text_color"]
        )

def set_invalid(component):
    """Set component to invalid state (red highlight)"""
    if isinstance(component, ctk.CTkEntry):
        component.configure(fg_color="#ffdddd", text_color="red")
    elif isinstance(component, ctk.CTkOptionMenu):
        component.configure(text_color="red")
