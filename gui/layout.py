#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete GUI layout definition for BIOX G-Code Generator

@author: Maria Teresa Alameda Felgueiras
"""

import customtkinter as ctk
from utils.constants import (PRINTHEAD_DEFAULT, PRINTHEAD_TYPES, 
                             TEMPLATE_PROPERTIES)

def create_main_window(root):
    """Create main window"""
    
    components = {'root' : root}
    
    # Create tab container
    tabview = ctk.CTkTabview(root)
    tabview.pack(expand = True, fill = 'both', padx = 5, pady = 5)
    
    # Add tabs
    tab_droplet = tabview.add('Droplet settings')
    tab_scafold = tabview.add('Scafold settings')
    
    # Configure main tab grid
    tab_droplet.grid_columnconfigure(0, weight=1)
    
    # Create tab droplet 
    create_droplet_tab(tab_droplet, components)
    
    # Create scafold tab
    create_scafold_tab(tab_scafold, components)
    
    return components
    
def create_droplet_tab(parent, components):
    """Create and configure all GUI components in droplet tab"""
    
    # Row 0: Printhead and Template selection
    components.update(create_printhead_section(parent, row=0))
    components.update(create_template_section(parent, row=0, column=4))
    
    # Row 1: General Settings
    components.update(create_general_settings(parent, row=1))
    
    # Row 2: Layer and Cleaning Settings
    components.update(create_layer_settings(parent, row=2))
    
    # Row 3: Temperature Control Frame
    components.update(create_temperature_section(parent, row=3))
    
    # Row 4: Sweep Options Frame
    components.update(create_sweep_options(parent, row=4))
    
    # Row 5: G-code Display Label
    ctk.CTkLabel(parent, text="Generated G-code:").grid(
        row=5, column=0, columnspan=6, padx=5, pady=5, sticky="w")
    
    # Row 6: G-code Text Display
    components.update(create_gcode_display(parent, row=6))
    
    # Row 7: Action Buttons
    components.update(create_action_buttons(parent, row=7))
    
    return components

def create_scafold_tab(parent, components):
    
    return

def create_printhead_section(parent, row):
    """Create printhead type and number selection"""
    frame = ctk.CTkFrame(parent)
    frame.grid(row=row, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
    
    # Printhead Type
    ctk.CTkLabel(frame, text="Printhead Type:").grid(row=0, column=0, padx=5, pady=5)
    printhead_type = ctk.StringVar(value=PRINTHEAD_DEFAULT)
    printhead_menu = ctk.CTkOptionMenu(
        frame, 
        variable=printhead_type,
        values=PRINTHEAD_TYPES,
        width=175,
        dynamic_resizing=False
    )
    printhead_menu.grid(row=0, column=1, padx=5, pady=5)
    
    # Printhead Number
    ctk.CTkLabel(frame, text="Printhead Number (0-2):").grid(row=0, column=2, padx=5, pady=5)
    printhead_number = ctk.StringVar(value="0")
    printhead_number_menu = ctk.CTkOptionMenu(
        frame,
        variable=printhead_number,
        values=["0", "1", "2"]
    )
    printhead_number_menu.grid(row=0, column=3, padx=5, pady=5)
    
    return {
        'printhead_type': printhead_type,
        'printhead_menu': printhead_menu,
        'printhead_number': printhead_number,
        'printhead_number_menu': printhead_number_menu
    }

def create_template_section(parent, row, column):
    """Create template selection dropdown"""
    frame = ctk.CTkFrame(parent)
    frame.grid(row=row, column=column, columnspan=2, padx=5, pady=5, sticky="ew")
    
    ctk.CTkLabel(frame, text="Multi-well Template:").grid(row=0, column=0, padx=5, pady=5)
    template_var = ctk.StringVar(value="One drop")
    template_menu = ctk.CTkOptionMenu(
        frame,
        variable=template_var,
        values=list(TEMPLATE_PROPERTIES.keys()),
        width=200,
        dynamic_resizing=False
    )
    template_menu.grid(row=0, column=1, padx=5, pady=5)
    
    return {
        'template_var': template_var,
        'template_menu': template_menu
    }

def create_general_settings(parent, row):
    """Create general print settings section"""
    frame = ctk.CTkFrame(parent)
    frame.grid(row=row, column=0, columnspan=6, padx=5, pady=5)
    
    # Pressure Setting
    ctk.CTkLabel(frame, text="Pressure (0-200 kPa):").grid(
                                        row=0, column=0, padx=5, pady=5
                                        )
    pressure_entry = ctk.CTkEntry(frame)
    pressure_entry.insert(0, "20")
    pressure_entry.grid(row=0, column=1, padx=5, pady=5)
    
    # Extrusion Time
    ctk.CTkLabel(frame, text="Extrusion time (s):").grid(row=0, column=2, padx=5, pady=5)
    extrusion_time_entry = ctk.CTkEntry(frame)
    extrusion_time_entry.insert(0, "1")
    extrusion_time_entry.grid(row=0, column=3, padx=5, pady=5)
    
    # Layer Height
    ctk.CTkLabel(frame, text="Layer Height (0.1-1.0 mm):").grid(
                                            row=0, column=4, padx=5, pady=5
                                            )
    layer_height_entry = ctk.CTkEntry(frame)
    layer_height_entry.insert(0, "0.1")
    layer_height_entry.grid(row=0, column=5, padx=5, pady=5)
    
    return {
        'pressure_entry': pressure_entry,
        'extrusion_time_entry': extrusion_time_entry,
        'layer_height_entry': layer_height_entry,
    }

def create_layer_settings(parent, row):
    """Create layer height and cleaning settings"""
    frame = ctk.CTkFrame(parent)
    frame.grid(row=row, column=0, columnspan=6, padx=5, pady=5)
    
    # Bed Z Position
    ctk.CTkLabel(frame, text="Bed move Z position (mm):").grid(
                                            row=0, column=0, padx=5, pady=5
                                            )
    bed_zpos_entry = ctk.CTkEntry(frame)
    bed_zpos_entry.insert(0, "10")
    bed_zpos_entry.grid(row=0, column=1, padx=5, pady=5)
    
    # Printhead Speed
    ctk.CTkLabel(frame, text="Printhead Speed (0-1500 mm/s):").grid(
                                        row=0, column=2, padx=5, pady=5
                                        )
    printhead_speed_entry = ctk.CTkEntry(frame)
    printhead_speed_entry.insert(0, "1200")
    printhead_speed_entry.grid(row=0, column=3, padx=5, pady=5)
       
    # Clean Printhead Checkbox
    clean_printhead_var = ctk.BooleanVar(value=False)
    clean_printhead_checkbox = ctk.CTkCheckBox(
        frame, 
        text="Clean printhead first",
        variable=clean_printhead_var
    )
    clean_printhead_checkbox.grid(row=0, column=4, columnspan=2, padx=5, pady=5)
    
    return {
        'bed_zpos_entry': bed_zpos_entry,
        'printhead_speed_entry': printhead_speed_entry,
        'clean_printhead_var': clean_printhead_var,
        'clean_printhead_checkbox': clean_printhead_checkbox
    }

def create_temperature_section(parent, row):
    """Create temperature control frame"""
    frame = ctk.CTkFrame(parent, border_width=2, border_color="#ADD8E6")
    frame.grid(row=row, column=0, columnspan=6, padx=10, pady=5)
    
    # Printhead Temperature
    phtemp_label = ctk.CTkLabel(frame, text="Printhead Temperature (30-65 °C):")
    phtemp_label.grid(row=0, column=0, padx=5, pady=5)
    phtemp_entry = ctk.CTkEntry(frame)
    phtemp_entry.insert(0, "30")
    phtemp_entry.grid(row=0, column=1, padx=5, pady=5)
    phtemp_entry.configure(state="disabled", fg_color="#d3d3d3", text_color="gray")
    
    # Control Printhead Temperature Checkbox
    control_phtemperature_var = ctk.BooleanVar(value=False)
    control_phtemperature_checkbox = ctk.CTkCheckBox(
        frame,
        text="Control printhead temperature",
        variable=control_phtemperature_var
    )
    control_phtemperature_checkbox.grid(row=0, column=2, padx=5, pady=5)
    
    # Bed Temperature
    bed_temp_label = ctk.CTkLabel(frame, text="Bed Temperature (4-65 °C):")
    bed_temp_label.grid(row=1, column=0, padx=5, pady=5)
    bed_temp_entry = ctk.CTkEntry(frame)
    bed_temp_entry.insert(0, "20")
    bed_temp_entry.grid(row=1, column=1, padx=5, pady=5)
    bed_temp_entry.configure(state="disabled", fg_color="#d3d3d3", text_color="gray")
    
    # Control Bed Temperature Checkbox
    control_bedtemperature_var = ctk.BooleanVar(value=False)
    control_bedtemperature_checkbox = ctk.CTkCheckBox(
        frame,
        text="Control bed temperature",
        variable=control_bedtemperature_var
    )
    control_bedtemperature_checkbox.grid(row=1, column=2, padx=5, pady=5)
    
    return {
        'phtemp_label': phtemp_label,
        'phtemp_entry': phtemp_entry,
        'control_phtemperature_var': control_phtemperature_var,
        'control_phtemperature_checkbox': control_phtemperature_checkbox,
        'bed_temp_label': bed_temp_label,
        'bed_temp_entry': bed_temp_entry,
        'control_bedtemperature_var': control_bedtemperature_var,
        'control_bedtemperature_checkbox': control_bedtemperature_checkbox
    }

def create_sweep_options(parent, row):
    """Create sweep options frame"""
    frame = ctk.CTkFrame(parent, border_width=2, border_color="#ff9999")
    frame.grid(row=row, column=0, columnspan=6, padx=10, pady=5)
    
    components = {}
    
    # Pressure Sweep Section
    components.update(create_pressure_sweep_section(frame, row=0))
    
    # Temperature Sweep Section
    components.update(create_temperature_sweep_section(frame, row=1))
    
    # Time Sweep Section
    components.update(create_time_sweep_section(frame, row=2))
    
    return components

def create_pressure_sweep_section(frame, row):
    """Create pressure sweep controls"""
    pressure_sweep_var = ctk.BooleanVar(value=False)
    pressure_sweep_checkbox = ctk.CTkCheckBox(
        frame,
        text="Pressure Sweep",
        variable=pressure_sweep_var
    )
    pressure_sweep_checkbox.grid(row=row, column=0, padx=5, pady=5)
    
    pressure_sweep_dir = ctk.StringVar(value="well")
    pressure_dir_menu = ctk.CTkOptionMenu(
        frame,
        variable=pressure_sweep_dir,
        values=["well", "row", "column"],
        width=80
    )
    pressure_dir_menu.grid(row=row, column=1, padx=5, pady=5)
    pressure_dir_menu.configure(state="disabled")
    
    # Initial Pressure
    ctk.CTkLabel(frame, text="Initial Pressure:").grid(row=row, column=2, padx=5, pady=5)
    pressure_initial_entry = ctk.CTkEntry(frame, state="disabled")
    pressure_initial_entry.configure(fg_color="#d3d3d3", text_color="gray")
    pressure_initial_entry.grid(row=row, column=3, padx=5, pady=5)
    
    # Final Pressure
    ctk.CTkLabel(frame, text="Final Pressure:").grid(row=row, column=4, padx=5, pady=5)
    pressure_final_entry = ctk.CTkEntry(frame, state="disabled")
    pressure_final_entry.configure(fg_color="#d3d3d3", text_color="gray")
    pressure_final_entry.grid(row=row, column=5, padx=5, pady=5)
    
    return {
        'pressure_sweep_var': pressure_sweep_var,
        'pressure_sweep_checkbox': pressure_sweep_checkbox,
        'pressure_sweep_dir': pressure_sweep_dir,
        'pressure_dir_menu': pressure_dir_menu,
        'pressure_initial_entry': pressure_initial_entry,
        'pressure_final_entry': pressure_final_entry
    }

def create_temperature_sweep_section(frame, row):
    """Create temperature sweep controls"""
    temperature_sweep_var = ctk.BooleanVar(value=False)
    temperature_sweep_checkbox = ctk.CTkCheckBox(
        frame,
        text="Temperature Sweep",
        variable=temperature_sweep_var
    )
    temperature_sweep_checkbox.grid(row=row, column=0, padx=5, pady=5)
    
    temp_sweep_dir = ctk.StringVar(value="well")
    temp_dir_menu = ctk.CTkOptionMenu(
        frame,
        variable=temp_sweep_dir,
        values=["well", "row", "column"],
        width=80
    )
    temp_dir_menu.grid(row=row, column=1, padx=5, pady=5)
    temp_dir_menu.configure(state="disabled")
    
    # Initial Temperature
    ctk.CTkLabel(frame, text="Initial Temp:").grid(row=row, column=2, padx=5, pady=5)
    temperature_initial_entry = ctk.CTkEntry(frame, state="disabled")
    temperature_initial_entry.configure(fg_color="#d3d3d3", text_color="gray")
    temperature_initial_entry.grid(row=row, column=3, padx=5, pady=5)
    
    # Final Temperature
    ctk.CTkLabel(frame, text="Final Temp:").grid(row=row, column=4, padx=5, pady=5)
    temperature_final_entry = ctk.CTkEntry(frame, state="disabled")
    temperature_final_entry.configure(fg_color="#d3d3d3", text_color="gray")
    temperature_final_entry.grid(row=row, column=5, padx=5, pady=5)
    
    return {
        'temperature_sweep_var': temperature_sweep_var,
        'temperature_sweep_checkbox': temperature_sweep_checkbox,
        'temp_sweep_dir': temp_sweep_dir,
        'temp_dir_menu': temp_dir_menu,
        'temperature_initial_entry': temperature_initial_entry,
        'temperature_final_entry': temperature_final_entry
    }

def create_time_sweep_section(frame, row):
    """Create extrusion time sweep controls"""
    extrusion_time_sweep_var = ctk.BooleanVar(value=False)
    extrusion_time_sweep_checkbox = ctk.CTkCheckBox(
        frame,
        text="Extrusion Time Sweep",
        variable=extrusion_time_sweep_var
    )
    extrusion_time_sweep_checkbox.grid(row=row, column=0, padx=5, pady=5)
    
    time_sweep_dir = ctk.StringVar(value="well")
    time_dir_menu = ctk.CTkOptionMenu(
        frame,
        variable=time_sweep_dir,
        values=["well", "row", "column"],
        width=80
    )
    time_dir_menu.grid(row=row, column=1, padx=5, pady=5)
    time_dir_menu.configure(state="disabled")
    
    # Initial Time
    ctk.CTkLabel(frame, text="Initial Time:").grid(row=row, column=2, padx=5, pady=5)
    extrusion_time_initial_entry = ctk.CTkEntry(frame, state="disabled")
    extrusion_time_initial_entry.configure(fg_color="#d3d3d3", text_color="gray")
    extrusion_time_initial_entry.grid(row=row, column=3, padx=5, pady=5)
    
    # Final Time
    ctk.CTkLabel(frame, text="Final Time:").grid(row=row, column=4, padx=5, pady=5)
    extrusion_time_final_entry = ctk.CTkEntry(frame, state="disabled")
    extrusion_time_final_entry.configure(fg_color="#d3d3d3", text_color="gray")
    extrusion_time_final_entry.grid(row=row, column=5, padx=5, pady=5)
    
    return {
        'extrusion_time_sweep_var': extrusion_time_sweep_var,
        'extrusion_time_sweep_checkbox': extrusion_time_sweep_checkbox,
        'time_sweep_dir': time_sweep_dir,
        'time_dir_menu': time_dir_menu,
        'extrusion_time_initial_entry': extrusion_time_initial_entry,
        'extrusion_time_final_entry': extrusion_time_final_entry
    }

def create_gcode_display(parent, row):
    """Create G-code display area with scrollbar"""
    frame = ctk.CTkFrame(parent)
    frame.grid(row=row, column=0, columnspan=6, padx=5, pady=5, sticky="nsew")
    
    gcode_text = ctk.CTkTextbox(frame, width=80, height=300, wrap=ctk.NONE)
    gcode_text.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
    
    return {
        'gcode_text': gcode_text,
        'gcode_frame': frame
    }

def create_action_buttons(parent, row):
    """Create action buttons at the bottom"""
    frame = ctk.CTkFrame(parent)
    frame.grid(row=row, column=0, columnspan=6, padx=5, pady=5, sticky="ew")
    
    # Toggle Dark Mode
    dark_mode_button = ctk.CTkButton(frame, text="Toggle Dark Mode")
    dark_mode_button.pack(side=ctk.LEFT, padx=5, pady=5)
    
    # Generate Button
    generate_button = ctk.CTkButton(frame, text="Generate G-code")
    generate_button.pack(side=ctk.RIGHT, padx=5, pady=5)
    
    # Export Button
    export_button = ctk.CTkButton(frame, text="Export G-code")
    export_button.pack(side=ctk.RIGHT, padx=5, pady=5)
    
    # Copy Button
    copy_button = ctk.CTkButton(frame, text="Copy to Clipboard")
    copy_button.pack(side=ctk.RIGHT, padx=5, pady=5)
    
    return {
        'dark_mode_button': dark_mode_button,
        'generate_button': generate_button,
        'export_button': export_button,
        'copy_button': copy_button
    }
