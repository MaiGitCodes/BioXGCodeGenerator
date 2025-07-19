#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete GUI layout definition for BIOX G-Code Generator

@author: Maria Teresa Alameda Felgueiras
"""

import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from utils.constants import (PRINTHEAD_DEFAULT, PRINTHEAD_TYPES, 
                             TEMPLATE_PROPERTIES)

def create_main_window(root):
    """Create main window"""
    
    components = {'root' : root}
    
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(expand = True, fill = 'both', padx = 5, pady = 5)
    
    # Create tab container
    tabview = ctk.CTkTabview(main_frame)
    tabview.pack(expand = True, fill = 'both', padx = 5, pady = 5)
    components['tabview'] = tabview
    
    # Add tabs
    tab_main = tabview.add('Main settings')
    tab_scafold = tabview.add('Scaffold settings')
    
    # Configure main tab grid
    tab_main.grid_columnconfigure(0, weight=1)
    
    # Create tab droplet 
    create_main_tab(tab_main, components)
    
    # Create scafold tab
    create_scaffold_tab(tab_scafold, components)
    
    # Create shared components
    create_shared_elements(main_frame, components)
    return components

def create_shared_elements(parent, components):
    
   # G-code Display Label
    ctk.CTkLabel(parent, text="Generated G-code:").pack(
        padx=5, pady=(10, 0), anchor="w"
    )
    
    # Row 6: G-code Text Display
    components.update(create_gcode_display(parent, row=6))
    
    # Row 7: Action Buttons
    components.update(create_action_buttons(parent, row=7))
    
    return components

def create_main_tab(parent, components):
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
        
    return components

def create_scaffold_tab(parent, components):
    """Create and configure all GUI components in scaffold tab"""
    # Main container frame
    main_frame = ctk.CTkFrame(parent)
    main_frame.pack(fill='both', expand=True, padx=5, pady=5)
    
    # Parameters frame (left side)
    params_frame = ctk.CTkFrame(main_frame)
    params_frame.pack(side='left', fill='y', padx=5, pady=5)
    
    # Visualization frame (right side)
    viz_frame = ctk.CTkFrame(main_frame)
    viz_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)
    
    # Scaffold Parameters
    ctk.CTkLabel(params_frame, text="Scaffold Parameters", font=('Helvetica', 14, 'bold')).pack(pady=10)
    
    # Pattern Type
    ctk.CTkLabel(params_frame, text="Pattern:").pack(pady=(10,0))
    pattern_var = ctk.StringVar(value="Grid")
    pattern_menu = ctk.CTkOptionMenu(
        params_frame,
        variable=pattern_var,
        values=["Grid", "Striped", "Honeycomb"],
        width=150
    )
    pattern_menu.pack(pady=5)
    
    # Dimensions
    ctk.CTkLabel(params_frame, text="Dimensions (mm):").pack(pady=(10,0))
    
    dim_frame = ctk.CTkFrame(params_frame)
    dim_frame.pack(pady=5)
    
    # X dimension
    ctk.CTkLabel(dim_frame, text="X:").grid(row=0, column=0, padx=5)
    size_x_entry = ctk.CTkEntry(dim_frame, width=60)
    size_x_entry.insert(0, "50")
    size_x_entry.grid(row=0, column=1, padx=5)
    
    # Y dimension
    ctk.CTkLabel(dim_frame, text="Y:").grid(row=0, column=2, padx=5)
    size_y_entry = ctk.CTkEntry(dim_frame, width=60)
    size_y_entry.insert(0, "50")
    size_y_entry.grid(row=0, column=3, padx=5)
        
    # Cell Parameters
    ctk.CTkLabel(params_frame, text="General Parameters:").pack(pady=(10,0))
    
    cell_frame = ctk.CTkFrame(params_frame)
    cell_frame.pack(pady=5)
    
    # Cell Size
    ctk.CTkLabel(cell_frame, text="Infill (%):").grid(row=0, column=0, padx=5)
    infill_entry = ctk.CTkEntry(cell_frame, width=60)
    infill_entry.insert(0, "50")
    infill_entry.grid(row=0, column=1, padx=5)
    
    # Noozle size --> Wall Thickness
    ctk.CTkLabel(cell_frame, text="Noozle (mm):").grid(row=1, column=0, padx=5)
    noozle_entry = ctk.CTkEntry(cell_frame, width=60)
    noozle_entry.insert(0, "0.41")
    noozle_entry.grid(row=1, column=1, padx=5)
    
    # Extrusion parameter (ammount of extruded material deposited in a movement)
    ctk.CTkLabel(cell_frame, text="Extrusion (mL):").grid(row=2, column=0, padx=5)
    extrusion_entry = ctk.CTkEntry(cell_frame, width=60)
    extrusion_entry.insert(0, "1")
    extrusion_entry.grid(row=2, column=1, padx=5)
    
    # Layer Height
    ctk.CTkLabel(cell_frame, text="Layer Height (mm):").grid(row=3, column=0, padx=5)
    layer_height_entry = ctk.CTkEntry(cell_frame, width=60)
    layer_height_entry.insert(0, "1")
    layer_height_entry.grid(row=3, column=1, padx=5)
    
    # Number of layers
    ctk.CTkLabel(cell_frame, text="Number of Layers:").grid(row=4, column=0, padx=5)
    layer_number_entry = ctk.CTkEntry(cell_frame, width=60)
    layer_number_entry.insert(0, "2")
    layer_number_entry.grid(row=4, column=1, padx=5)
    
    # Number of layers
    ctk.CTkLabel(cell_frame, text="Speed (mm/min):").grid(row=5, column=0, padx=5)
    speed_entry = ctk.CTkEntry(cell_frame, width=60)
    speed_entry.insert(0, "1200")
    speed_entry.grid(row=5, column=1, padx=5)
    
    # Preview Button
    preview_button = ctk.CTkButton(
        params_frame,
        text="Preview Scaffold"
    )
    preview_button.pack(pady=20)
    
    export_preview_button = ctk.CTkButton(
        params_frame,
        text="Export as PNG"
    )
    export_preview_button.pack(pady=5)
    
    show_axes_var = ctk.BooleanVar(value=True)
    show_axes_checkbox = ctk.CTkCheckBox(
        params_frame,
        text="Show Axes and Grid",
        variable=show_axes_var
    )
    show_axes_checkbox.pack(pady=5)
        
    # Create 3D visualization area
    fig = Figure(figsize=(6, 6), dpi=150)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_axis_off()
    fig.tight_layout()
    
    canvas = FigureCanvasTkAgg(fig, master=viz_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill='both', expand=True)
    toolbar = NavigationToolbar2Tk(canvas, viz_frame)
    toolbar.update()
    toolbar.pack(fill='x', padx=5, pady=(0, 5))

    
    components.update({
        'scaffold_pattern_var': pattern_var,
        'scaffold_size_x_entry': size_x_entry,
        'scaffold_size_y_entry': size_y_entry,
        'scaffold_infill_entry': infill_entry,
        'scaffold_noozle_entry': noozle_entry,
        'scaffold_extrusion_entry': extrusion_entry,
        'scaffold_layer_height_entry': layer_height_entry,
        'layer_number_entry': layer_number_entry,
        'scaffold_speed_entry': speed_entry,
        'scaffold_preview_button': preview_button,
        'scaffold_export_button': export_preview_button,
        'show_axes_var': show_axes_var,
        'scaffold_fig': fig,
        'scaffold_ax': ax,
        'scaffold_canvas': canvas
    })
    
    return components
   
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
    clean_printhead_checkbox.grid(row=1, column=0, columnspan=3, padx=5, pady=5)
    
    # Terminate current operation
    terminate_operation_var = ctk.BooleanVar(value=True)
    terminate_operation_checkbox = ctk.CTkCheckBox(
        frame,
        text="Terminate operation",
        variable=terminate_operation_var)
    terminate_operation_checkbox.grid(row=1, column=1, columnspan=3, padx=5, pady=5)
    
    return {
        'bed_zpos_entry': bed_zpos_entry,
        'printhead_speed_entry': printhead_speed_entry,
        'clean_printhead_var': clean_printhead_var,
        'clean_printhead_checkbox': clean_printhead_checkbox,
        'terminate_operation_checkbox': terminate_operation_checkbox
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
    frame.pack(fill='both', expand=False, padx=5, pady=5)
    
    gcode_text = ctk.CTkTextbox(frame, width=80, height=300, wrap=ctk.NONE)
    gcode_text.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
    
    return {
        'gcode_text': gcode_text,
        'gcode_frame': frame
    }


def create_action_buttons(parent, row):
    """Create action buttons at the bottom"""
    frame = ctk.CTkFrame(parent)
    frame.pack(fill='both', expand=False, padx=5, pady=5)
    
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