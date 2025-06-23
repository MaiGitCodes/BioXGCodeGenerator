#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete event handlers for BIOX G-Code Generator

@author: Maria Teresa Alameda Felgueiras
"""
import numpy as np
from tkinter import messagebox, filedialog
import customtkinter as ctk
from ..core.gcode import GCODE as GC
from ..core.gcode import clean_printhead
from ..core.templates import set_template
from ..gui.validation import validate_inputs, validate_input_fields

def setup_event_handlers(root, components):
    """Configure all event handlers and callbacks"""
    # Printhead type change handler
    components['printhead_type'].trace("w", lambda *args: update_ui(components))
    
    # Template change handler
    components['template_var'].trace("w", lambda *args: toggle_sweep_options_based_on_template(components))
    
    # Generate button
    components['generate_button'].configure(command=lambda: generate_gcode(components))
    
    # Export button
    components['export_button'].configure(command=lambda: export_gcode(components))
    
    # Copy button
    components['copy_button'].configure(command=lambda: copy_to_clipboard(components))
    
    # Dark mode toggle
    components['dark_mode_button'].configure(command=toggle_dark_mode)
    
    # Temperature control checkboxes
    components['control_phtemperature_var'].trace(
        "w", lambda *args: toggle_printhead_temperature(components))
    components['control_bedtemperature_var'].trace(
        "w", lambda *args: toggle_bed_temperature(components))
    
    # Sweep option checkboxes
    components['pressure_sweep_var'].trace(
        "w", lambda *args: toggle_sweep_options("pressure", components))
    components['temperature_sweep_var'].trace(
        "w", lambda *args: toggle_sweep_options("temperature", components))
    components['extrusion_time_sweep_var'].trace(
        "w", lambda *args: toggle_sweep_options("extrusion_time", components))
    
    # Input validation bindings
    for entry in [components['printhead_speed_entry'], 
                 components['layer_height_entry'],
                 components['bed_temp_entry'],
                 components['pressure_entry'],
                 components['extrusion_time_entry'],
                 components['bed_zpos_entry'],
                 components['phtemp_entry'],
                 components['pressure_initial_entry'],
                 components['pressure_final_entry'],
                 components['temperature_initial_entry'],
                 components['temperature_final_entry'],
                 components['extrusion_time_initial_entry'],
                 components['extrusion_time_final_entry']]:
        entry.bind("<KeyRelease>", lambda event: validate_input_fields(components))

def generate_gcode(components):
    """Generate G-code based on current settings"""
    if not validate_inputs(components):
        return
        
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

    # End-of-print commands
    if components['control_bedtemperature_var'].get() and not any_sweep_active:
        gcode += "M800 ; Turn off bed heating\n"
        
    gcode += "G0 Z50; move bed to parking position\n"
    gcode += "M400; wait for bed to reach parking position\n"
    if components['terminate_operation_checkbox'].get():
        gcode += "M84 ; Disable motors\n"
    else:
        gcode += "; Current operation not terminated to maintain conditions\n"
        gcode += "; Don't forget to terminate operation manually when finished\n"

    # Display generated G-code
    components['gcode_text'].delete("1.0", ctk.END)
    components['gcode_text'].insert(ctk.END, gcode)

def export_gcode(components):
    """Export generated G-code to file"""
    gcode = components['gcode_text'].get("1.0", ctk.END)
    if not gcode.strip():
        messagebox.showerror("Error", "No G-code to export.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".gcode", 
        filetypes=[("G-code files", "*.gcode")]
    )
    if file_path:
        try:
            with open(file_path, "w") as file:
                file.write(gcode)
            messagebox.showinfo("Success", "G-code exported successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export G-code: {e}")

def copy_to_clipboard(components):
    """Copy G-code to clipboard"""
    gcode = components['gcode_text'].get("1.0", ctk.END)
    if gcode.strip():
        components['root'].clipboard_clear()  # Access root from components
        components['root'].clipboard_append(gcode)
        messagebox.showinfo("Success", "G-code copied to clipboard.")
    else:
        messagebox.showerror("Error", "No G-code to copy.")

def toggle_dark_mode():
    """Toggle between light and dark mode"""
    if ctk.get_appearance_mode() == "Light":
        ctk.set_appearance_mode("Dark")
    else:
        ctk.set_appearance_mode("Light")

def update_ui(components):
    """Update UI based on selected printhead type"""
    printhead_type_value = components['printhead_type'].get()
    
    if printhead_type_value in ["EMD", "Pneumatic", "Syringe Pump"]:
        components['phtemp_label'].configure(text="Printhead Temperature (30-65 °C):")
        components['phtemp_entry'].delete(0, ctk.END)
        components['phtemp_entry'].insert(0, "30")
    elif printhead_type_value == "Thermo-controlled":
        components['phtemp_label'].configure(text="Printhead Temperature (4-65 °C):")
        components['phtemp_entry'].delete(0, ctk.END)
        components['phtemp_entry'].insert(0, "4")

def toggle_printhead_temperature(components):
    """Toggle printhead temperature control"""
    if components['control_phtemperature_var'].get():
        components['phtemp_entry'].configure(
            state="normal", 
            fg_color="white", 
            text_color="black"
        )
    else:
        components['phtemp_entry'].configure(
            state="disabled", 
            fg_color="#d3d3d3", 
            text_color="gray"
        )

def toggle_bed_temperature(components):
    """Toggle bed temperature control"""
    if components['control_bedtemperature_var'].get():
        components['bed_temp_entry'].configure(
            state="normal", 
            fg_color="white", 
            text_color="black"
        )
    else:
        components['bed_temp_entry'].configure(
            state="disabled", 
            fg_color="#d3d3d3", 
            text_color="gray"
        )

def toggle_sweep_options(sweep_type, components):
    """Toggle sweep options and disable temperature controls when any sweep is active"""
    # First handle mutual exclusivity of sweep options
    if sweep_type == "pressure" and components['pressure_sweep_var'].get():
        # If enabling pressure sweep, disable others
        components['temperature_sweep_var'].set(False)
        components['extrusion_time_sweep_var'].set(False)
    elif sweep_type == "temperature" and components['temperature_sweep_var'].get():
        # If enabling temperature sweep, disable others
        components['pressure_sweep_var'].set(False)
        components['extrusion_time_sweep_var'].set(False)
    elif sweep_type == "extrusion_time" and components['extrusion_time_sweep_var'].get():
        # If enabling time sweep, disable others
        components['pressure_sweep_var'].set(False)
        components['temperature_sweep_var'].set(False)

    # Now update the UI state for all sweep options
    update_sweep_ui_state(components)
    
def update_sweep_ui_state(components):
    """Update the UI state for all sweep options based on their current values"""
    # Update pressure sweep UI
    update_single_sweep_ui(
        "pressure",
        components['pressure_sweep_var'].get(),
        components['pressure_dir_menu'],
        components['pressure_initial_entry'],
        components['pressure_final_entry'],
        components['pressure_entry'],
        components
    )

    # Update temperature sweep UI
    update_single_sweep_ui(
        "temperature",
        components['temperature_sweep_var'].get(),
        components['temp_dir_menu'],
        components['temperature_initial_entry'],
        components['temperature_final_entry'],
        None,  # No default entry for temperature
        components
    )

    # Update time sweep UI
    update_single_sweep_ui(
        "extrusion_time",
        components['extrusion_time_sweep_var'].get(),
        components['time_dir_menu'],
        components['extrusion_time_initial_entry'],
        components['extrusion_time_final_entry'],
        components['extrusion_time_entry'],
        components
    )

    # Check if any sweep is now active
    any_sweep_active = (components['pressure_sweep_var'].get() or
                       components['temperature_sweep_var'].get() or
                       components['extrusion_time_sweep_var'].get())

    # Update temperature controls based on sweep state
    temperature_sweep_active = components['temperature_sweep_var'].get()
    update_temperature_controls(components, temperature_sweep_active)

def update_single_sweep_ui(sweep_type, is_active, dir_menu, initial_entry, final_entry, default_entry, components):
    """Update the UI state for a single sweep option"""
    if is_active:  # If this sweep is active
        # Enable sweep controls
        dir_menu.configure(state="normal")
        set_entry_state(initial_entry, enabled=True)
        set_entry_state(final_entry, enabled=True)
        if default_entry:
            set_entry_state(default_entry, enabled=False)
        
        # # Disable other sweep checkboxes
        # if sweep_type != "pressure":
        #     components['pressure_sweep_checkbox'].configure(state="disabled")
        # if sweep_type != "temperature":
        #     components['temperature_sweep_checkbox'].configure(state="disabled")
        # if sweep_type != "extrusion_time":
        #     components['extrusion_time_sweep_checkbox'].configure(state="disabled")
    else:  # If this sweep is inactive
        # Disable sweep controls
        dir_menu.configure(state="disabled")
        set_entry_state(initial_entry, enabled=False)
        set_entry_state(final_entry, enabled=False)
        if default_entry:
            set_entry_state(default_entry, enabled=True)
        
        # Enable other sweep checkboxes if no sweep is active
        if not (components['pressure_sweep_var'].get() or 
                components['temperature_sweep_var'].get() or 
                components['extrusion_time_sweep_var'].get()):
            components['pressure_sweep_checkbox'].configure(state="normal")
            components['temperature_sweep_checkbox'].configure(state="normal")
            components['extrusion_time_sweep_checkbox'].configure(state="normal")

def update_temperature_controls(components, temperature_sweep_active):
    """Update temperature controls based on sweep state"""
    if temperature_sweep_active:
        # Disable temperature controls
        # components['control_bedtemperature_var'].set(False)
        components['control_phtemperature_var'].set(False)
        # components['bed_temp_entry'].configure(state="disabled", fg_color="#d3d3d3", text_color="gray")
        components['phtemp_entry'].configure(state="disabled", fg_color="#d3d3d3", text_color="gray")
        # components['control_bedtemperature_checkbox'].configure(state="disabled")
        components['control_phtemperature_checkbox'].configure(state="disabled")
    else:
        # Enable temperature checkboxes
        # components['control_bedtemperature_checkbox'].configure(state="normal")
        components['control_phtemperature_checkbox'].configure(state="normal")
        # Update the actual entry states based on their checkbox values
        # toggle_bed_temperature(components)
        toggle_printhead_temperature(components)
def set_entry_state(entry, enabled=True):
    """
    Helper function to set the state and appearance of an entry widget
    
    Args:
        entry (CTkEntry): The entry widget to modify
        enabled (bool): Whether to enable or disable the entry
    """
    if enabled:
        entry.configure(
            state="normal",
            fg_color="white",
            text_color="black"
        )
    else:
        entry.configure(
            state="disabled",
            fg_color="#d3d3d3",  # Light gray
            text_color="gray"
        )

def toggle_sweep_options_based_on_template(components):
    """Enable/disable sweep options based on template selection"""
    if components['template_var'].get() == "One drop":
        # Disable all sweep options
        components['pressure_sweep_var'].set(False)
        components['temperature_sweep_var'].set(False)
        components['extrusion_time_sweep_var'].set(False)
        
        # Disable all sweep controls
        components['pressure_sweep_checkbox'].configure(state="disabled")
        components['temperature_sweep_checkbox'].configure(state="disabled")
        components['extrusion_time_sweep_checkbox'].configure(state="disabled")
        
        # Call toggle_sweep_options to disable all sweep parameters
        toggle_sweep_options("pressure", components)
        toggle_sweep_options("temperature", components)
        toggle_sweep_options("extrusion_time", components)
    else:
        # Enable sweep checkboxes
        components['pressure_sweep_checkbox'].configure(state="normal")
        components['temperature_sweep_checkbox'].configure(state="normal")
        components['extrusion_time_sweep_checkbox'].configure(state="normal")
