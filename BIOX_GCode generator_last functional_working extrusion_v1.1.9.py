# -*- coding: utf-8 -*-
"""
Created on Sat Mar  1 16:59:47 2025

@author: Maria Teresa Alameda
"""

import numpy as np
import customtkinter as ctk
from tkinter import messagebox, filedialog

from gcode import GCODE as GC
from gcode import clean_printhead

# Set customtkinter appearance
ctk.set_appearance_mode("Light")  # Default to light mode
ctk.set_default_color_theme("blue")  # Use the default blue theme

# Function to copy the gcode to clippoard
def copy_to_clipboard():
    gcode = gcode_text.get("1.0", ctk.END)
    if gcode.strip():
        root.clipboard_clear()  # Clear the clipboard
        root.clipboard_append(gcode)  # Copy the G-code to the clipboard
        messagebox.showinfo("Success", "G-code copied to clipboard.")
    else:
        messagebox.showerror("Error", "No G-code to copy.")


# Function to generate G-code for a multi-well template
def generate_gcode():
    if not validate_inputs():
        return
    
    # Printhead-specific settings
    printhead_type_value = printhead_type.get()
    printhead_number = int(printhead_number_var.get())
    bed_movement_position = float(bed_zpos_entry.get())
    clean_printhead_bool = clean_printhead_var.get()
       
    gcode = GC.initialize(printhead_type_value = printhead_type_value)
    
    # Get selected template
    template_properties, gcode = set_template(template_var.get(), gcode)
    rows, cols, well_spacing_x, well_spacing_y, _, _ = template_properties
           
    gcode = GC.set_printhead(gcode, printhead = printhead_number)
    
    gcode = GC.set_bed_temperature(gcode, float(bed_temp_entry.get()))
    
    gcode = GC.set_default_pressure(gcode, float(pressure_entry.get()))
       
    # gcode += "M400 ; Wait for bed temperature to stabilize\n\n"

    if printhead_type_value == "EMD":
        pass
        # gcode += f"M2065 T{printhead_number} S{float(emd_open_time_entry.get())} ; Set EMD open time\n"
        # gcode += f"M2067 T{printhead_number} S{float(emd_cycle_time_entry.get())} ; Set EMD cycle time\n"
    elif printhead_type_value == "pneumatic":
        pass
    elif printhead_type_value == "thermo-controlled":
        gcode = GC.set_printhead_temperature(gcode,
                                             float(thermo_temp_entry.get()),
                                             printhead=printhead_number
                                             )
    elif printhead_type_value == "syringe pump":
        gcode += f"M2032 T{printhead_number} S{float(syringe_extrusion_rate_entry.get())} ; Set syringe pump extrusion rate\n"

    pressure_sweep = pressure_sweep_var.get()
    if pressure_sweep:
        initial_pressure = float(pressure_initial_entry.get())
        final_pressure = float(pressure_final_entry.get())
        pressures = np.linspace(initial_pressure, final_pressure, rows*cols)
    else:
        pressures = [pressure_entry.get()]
    
    # Calculate the starting position to center the plate on the print bed
    start_x = 0.0
    start_y = 0.0

    # Generate G-code for printing over the wells
    gcode = GC.set_printhead_speed(gcode, printhead_speed_entry.get())
    
    if clean_printhead_bool:
        # Clean printhead
        gcode = clean_printhead(
                            gcode, printhead_number,
                            printhead_speed_entry.get(),
                            bed_movement_position
                            )
           
    counter = 0
    for row in range(rows):
        for col in range(cols):
            
            
            x = start_x + col * well_spacing_x
            y = start_y + row * well_spacing_y
            z = float(layer_height_entry.get())

            gcode = GC.move_to_position(gcode, x, y,
                                        speed = printhead_speed_entry.get(), 
                                        row = row, col = col)
            
            # Extrude material in the well
            if printhead_type_value == "EMD":
                gcode = GC.move_bed(gcode, z = 0, 
                                    speed=printhead_speed_entry.get()) # bed go up - prepare to extrude
                gcode = GC.emd_extrusion(gcode,
                                             printhead_number,
                                             float(pressures[counter]),
                                             float(extrusion_time_entry.get())
                                             ) # Extrusion 
                gcode = GC.move_bed(gcode, z = bed_movement_position,
                                    speed=printhead_speed_entry.get()) 
                # bed go down to movement position after extrusion
                
            elif printhead_type_value == "pneumatic":
                gcode = GC.move_bed(gcode, z,
                                    speed = printhead_speed_entry.get()) # bed go up - prepare to extrude
                gcode = GC.pneumatic_extrusion(gcode,
                                             printhead_number,
                                             float(pressures[counter]),
                                             float(extrusion_time_entry.get())
                                             ) # Extrusion 
                gcode = GC.move_bed(gcode, z = bed_movement_position,
                                    speed=printhead_speed_entry.get()) 
                # bed go down to movement position after extrusion
            
            elif printhead_type_value == "thermo-controlled":
                gcode = GC.move_bed(gcode, z,
                                    speed = printhead_speed_entry.get()) # bed go up - prepare to extrude
                gcode = GC.thermo_extrusion(gcode,
                                             printhead_number,
                                             float(pressures[counter]),
                                             float(extrusion_time_entry.get())
                                             ) # Extrusion 
                gcode = GC.move_bed(gcode, z = bed_movement_position,
                                    speed=printhead_speed_entry.get()) 
                # bed go down to movement position after extrusion
                
            elif printhead_type_value == "syringe pump":
                gcode += f"M2032 T{printhead_number} S{float(syringe_extrusion_rate_entry.get())} ; Set extrusion rate\n"
                gcode += "G1 E10 F100 ; Extrude material\n"  # Extrude 10mm of material
                
                
            if pressure_sweep: counter+=1

        # End-of-print commands
    gcode += "M800 ; Turn off bed heating\n"
    gcode += "M84 ; Disable motors\n"

    # Display generated G-code
    gcode_text.delete("1.0", ctk.END)
    gcode_text.insert(ctk.END, gcode)

# VALIDATION FUNCTIONS:
    
# Function to validate input fields and highlight invalid values in red
def validate_input_fields():
    # Validate printhead number
    printhead_number = printhead_number_var.get()
    if printhead_number.isdigit():
        printhead_number = int(printhead_number)
        if printhead_number < 0 or printhead_number > 2:
            printhead_number_menu.configure(text_color="red")
        else:
            printhead_number_menu.configure(text_color=ctk.ThemeManager.theme["CTkOptionMenu"]["text_color"])
    else:
        printhead_number_menu.configure(text_color="red")

    # Validate print speed
    printhead_speed = printhead_speed_entry.get()
    if printhead_speed.replace(".", "", 1).isdigit():
        printhead_speed = float(printhead_speed)
        if printhead_speed <= 0 or printhead_speed > 1500:
            printhead_speed_entry.configure(text_color="red")
        else:
            printhead_speed_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
    elif printhead_speed == "":
        printhead_speed_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
    else:
        printhead_speed_entry.configure(text_color="red")

    # Validate layer height
    layer_height = layer_height_entry.get()
    if layer_height.replace(".", "", 1).isdigit():
        layer_height = float(layer_height)
        if layer_height < 0.1 or layer_height > 1.0:
            layer_height_entry.configure(text_color="red")
        else:
            layer_height_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
    elif layer_height == "":
        layer_height_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
    else:
        layer_height_entry.configure(text_color="red")

    # Validate bed temperature
    bed_temp = bed_temp_entry.get()
    if bed_temp.replace(".", "", 1).isdigit():
        bed_temp = float(bed_temp)
        if bed_temp < 4 or bed_temp > 65:
            bed_temp_entry.configure(text_color="red")
        else:
            bed_temp_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
    elif bed_temp == "":
        bed_temp_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
    else:
        bed_temp_entry.configure(text_color="red")
        
    # Validate pressure
    pressure = pressure_entry.get()
    if pressure.replace(".", "", 1).isdigit():
        pressure = float(pressure)
        if pressure < 0 or pressure > 200:
            pressure_entry.configure(text_color="red")
        else:
            pressure_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
    elif pressure == "":
        pressure_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
    else:
        pressure_entry.configure(text_color="red")
        
    # Validate extrusion time
    extrusion_time = extrusion_time_entry.get()
    if extrusion_time.replace(".", "", 1).isdigit():
        extrusion_time = float(extrusion_time)
        if extrusion_time <= 0:
            extrusion_time_entry.configure(text_color="red")
        else:
            extrusion_time_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
    elif extrusion_time == "":
        extrusion_time_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
    else:
        extrusion_time_entry.configure(text_color="red")
        
        
    # Validate extrusion time
    bed_position = bed_zpos_entry.get()
    if bed_position.replace(".", "", 1).isdigit():
        bed_position = float(bed_position)
        if bed_position <= 0:
            bed_zpos_entry.configure(text_color="red")
        else:
            bed_zpos_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
    elif bed_position == "":
        bed_zpos_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
    else:
        bed_zpos_entry.configure(text_color="red")

    # Validate printhead-specific settings
    printhead_type_value = printhead_type.get()

    if printhead_type_value == "EMD":
        open_time = emd_open_time_entry.get()
        cycle_time = emd_cycle_time_entry.get()
        if open_time.replace(".", "", 1).isdigit():
            open_time = float(open_time)
            if open_time < 0 or open_time > 20:
                emd_open_time_entry.configure(text_color="red")
            else:
                emd_open_time_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
        elif open_time == "":
            emd_open_time_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
        else:
            emd_open_time_entry.configure(text_color="red")

        if cycle_time.replace(".", "", 1).isdigit():
            cycle_time = float(cycle_time)
            if cycle_time < 0 or cycle_time > 10000:
                emd_cycle_time_entry.configure(text_color="red")
            else:
                emd_cycle_time_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
        elif cycle_time == "":
            emd_cycle_time_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
        else:
            emd_cycle_time_entry.configure(text_color="red")

    # elif printhead_type_value == "pneumatic":
    #     pressure = pneumatic_pressure_entry.get()
    #     if pressure.replace(".", "", 1).isdigit():
    #         pressure = float(pressure)
    #         if pressure < 0 or pressure > 200:
    #             pneumatic_pressure_entry.configure(text_color="red")
    #         else:
    #             pneumatic_pressure_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
    #     elif pressure == "":
    #         pneumatic_pressure_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
    #     else:
    #         pneumatic_pressure_entry.configure(text_color="red")

    elif printhead_type_value == "thermo-controlled":
        temperature = thermo_temp_entry.get()
        if temperature.replace(".", "", 1).isdigit():
            temperature = float(temperature)
            if temperature < 4 or temperature > 65:
                thermo_temp_entry.configure(text_color="red")
            else:
                thermo_temp_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
        elif temperature == "":
            thermo_temp_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
        else:
            thermo_temp_entry.configure(text_color="red")

    elif printhead_type_value == "syringe pump":
        extrusion_rate = syringe_extrusion_rate_entry.get()
        if extrusion_rate.replace(".", "", 1).isdigit():
            extrusion_rate = float(extrusion_rate)
            if extrusion_rate < 0 or extrusion_rate > 1000:
                syringe_extrusion_rate_entry.configure(text_color="red")
            else:
                syringe_extrusion_rate_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
        elif extrusion_rate == "":
            syringe_extrusion_rate_entry.configure(text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"])
        else:
            syringe_extrusion_rate_entry.configure(text_color="red")

# Function to validate mandatory input values
def validate_inputs():
    try:
        # Validate printhead number
        printhead_number = int(printhead_number_var.get())
        if printhead_number < 0 or printhead_number > 2:  # BIO X supports 1-3 printheads
            raise ValueError("Printhead number must be between 0 and 2.")

        # Validate print speed
        printhead_speed = float(printhead_speed_entry.get())
        if printhead_speed <= 0 or printhead_speed > 1500:  
            # Recommended range: 0–50 mm/s
            raise ValueError("Print speed must be between 0 and 50 mm/s.")

        # Validate layer height
        layer_height = float(layer_height_entry.get())
        if layer_height < 0.1 or layer_height > 1.0:  # Typical range: 0.1–1.0 mm
            raise ValueError("Layer height must be between 0.1 and 1.0 mm.")

        # Validate bed temperature
        bed_temp = float(bed_temp_entry.get())
        if bed_temp < 4 or bed_temp > 65:  # Range: 4–65°C
            raise ValueError("Bed temperature must be between 4 and 65 °C.")
            
        # Validate pressure
        pressure = float(pressure_entry.get())
        if pressure <= 0 or pressure > 200:  # Range: 0 – 200 kPa
            raise ValueError("Pressure must be between 0 and 200 kPa.")
            
        # Validate extrusion time
        extrusion_time = float(extrusion_time_entry.get())
        if extrusion_time <= 0:  # Range: <0 s
            raise ValueError("Exrusion time must be between <0")
            
            
        # Validate bed movement position
        bed_position = float(bed_zpos_entry.get())
        if bed_position <= 0:  # Range: <0 s
            raise ValueError("Bed position at prtinhead movement must be greater than 0")
        

        # Validate printhead-specific mandatory settings
        printhead_type_value = printhead_type.get()

        if printhead_type_value == "EMD":
            open_time = emd_open_time_entry.get()
            cycle_time = emd_cycle_time_entry.get()
            if not open_time or not cycle_time:
                raise ValueError("EMD open time and cycle time are mandatory.")
            if float(open_time) < 0 or float(open_time) > 20:  # Open time: 0–20 ms
                raise ValueError("EMD open time must be between 0 and 10 seconds.")
            if float(cycle_time) < 0 or float(cycle_time) > 10000:  # Cycle time: 0–10,000 µs
                raise ValueError("EMD cycle time must be between 0 and 10,000 µs.")

        # elif printhead_type_value == "pneumatic":
        #     pressure = pneumatic_pressure_entry.get()
        #     if not pressure:
        #         raise ValueError("Pneumatic pressure is mandatory.")
        #     if float(pressure) < 0 or float(pressure) > 200:  # Range: 0–200 kPa
        #         raise ValueError("Pneumatic pressure must be between 0 and 200 kPa.")

        elif printhead_type_value == "thermo-controlled":
            temperature = thermo_temp_entry.get()
            if not temperature:
                raise ValueError("Thermo-controlled temperature is mandatory.")
            if float(temperature) < 4 or float(temperature) > 65:  # Range: 4–65°C
                raise ValueError("Thermo-controlled temperature must be between 4 and 65 °C.")

        elif printhead_type_value == "syringe pump":
            extrusion_rate = syringe_extrusion_rate_entry.get()
            if not extrusion_rate:
                raise ValueError("Extrusion rate is mandatory.")
            if float(extrusion_rate) < 0 or float(extrusion_rate) > 1000:  # Range: 0–1000 nL/s
                raise ValueError("Extrusion rate must be between 0 and 1000 nL/s.")

        return True
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))
        return False

# Function to toggle sweep options
def toggle_sweep_options(sweep_type):
    if sweep_type == "pressure":
        if pressure_sweep_var.get():
            # Disable temperature sweep and its text boxes
            temperature_sweep_var.set(False)
            temperature_initial_entry.configure(state="disabled", fg_color="#d3d3d3", text_color="gray")
            temperature_final_entry.configure(state="disabled", fg_color="#d3d3d3", text_color="gray")
            
            # Enable pressure sweep text boxes
            pressure_initial_entry.configure(state="normal", fg_color="white", text_color="black")
            pressure_final_entry.configure(state="normal", fg_color="white", text_color="black")
            
            # Disable the default pressure text box
            pressure_entry.configure(state="disabled", fg_color="#d3d3d3", text_color="gray")
        else:
            # Disable pressure sweep text boxes
            pressure_initial_entry.configure(state="disabled", fg_color="#d3d3d3", text_color="gray")
            pressure_final_entry.configure(state="disabled", fg_color="#d3d3d3", text_color="gray")
            
            # Re-enable the default pressure text box
            pressure_entry.configure(state="normal", fg_color="white", text_color="black")
    elif sweep_type == "temperature":
        if temperature_sweep_var.get():
            # Disable pressure sweep and its text boxes
            pressure_sweep_var.set(False)
            pressure_initial_entry.configure(state="disabled", fg_color="#d3d3d3", text_color="gray")
            pressure_final_entry.configure(state="disabled", fg_color="#d3d3d3", text_color="gray")
            
            # Enable temperature sweep text boxes
            temperature_initial_entry.configure(state="normal", fg_color="white", text_color="black")
            temperature_final_entry.configure(state="normal", fg_color="white", text_color="black")
            
            # Re-enable the default pressure text box (if it was disabled)
            pressure_entry.configure(state="normal", fg_color="white", text_color="black")
        else:
            # Disable temperature sweep text boxes
            temperature_initial_entry.configure(state="disabled", fg_color="#d3d3d3", text_color="gray")
            temperature_final_entry.configure(state="disabled", fg_color="#d3d3d3", text_color="gray")
            
# Function to export G-code as a .gcode file
def export_gcode():
    gcode = gcode_text.get("1.0", ctk.END)
    if not gcode.strip():
        messagebox.showerror("Error", "No G-code to export.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".gcode", filetypes=[("G-code files", "*.gcode")])
    if file_path:
        try:
            with open(file_path, "w") as file:
                file.write(gcode)
            messagebox.showinfo("Success", "G-code exported successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export G-code: {e}")

# Function to update UI based on selected printhead type
def update_ui():
    printhead_type_value = printhead_type.get()

    # Clear all printhead-specific labels and entries
    for widget in printhead_specific_frame.winfo_children():
        widget.grid_remove()

    # Show relevant settings based on selected printhead type
    if printhead_type_value == "EMD":
        emd_open_time_label.grid(row=0, column=0, padx=5, pady=5)
        emd_open_time_entry.grid(row=0, column=1, padx=5, pady=5)
        emd_cycle_time_label.grid(row=0, column=2, padx=5, pady=5)
        emd_cycle_time_entry.grid(row=0, column=3, padx=5, pady=5)
    elif printhead_type_value == "Pneumatic":
        pass
    elif printhead_type_value == "Thermo-controlled":
        thermo_temp_label.grid(row=0, column=0, padx=5, pady=5)
        thermo_temp_entry.grid(row=0, column=1, padx=5, pady=5)
        temperature_sweep_checkbox.configure(state="normal")
    elif printhead_type_value == "Syringe pump":
        syringe_extrusion_rate_label.grid(row=0, column=0, padx=5, pady=5)
        syringe_extrusion_rate_entry.grid(row=0, column=1, padx=5, pady=5)
        temperature_sweep_checkbox.configure(state="disabled")

    # Show optional parameters for all printheads
    extrusion_volume_label.grid(row=1, column=0, padx=5, pady=5)
    extrusion_volume_entry.grid(row=1, column=1, padx=5, pady=5)
    pause_time_label.grid(row=1, column=2, padx=5, pady=5)
    pause_time_entry.grid(row=1, column=3, padx=5, pady=5)


# Function to toggle dark mode
def toggle_dark_mode():
    if ctk.get_appearance_mode() == "Light":
        ctk.set_appearance_mode("Dark")
    else:
        ctk.set_appearance_mode("Light")


def set_template(template, gcode):
    
    gcode += f"\n; {template} template selected\n\n"
       
    # template = template.split(' ')[0]
    # Define well positions for each template
    if template == "96-well plate":
        rows, cols = 8, 12
        well_spacing_x, well_spacing_y = 9, 9  # mm (center-to-center spacing for 96-well plates)
        plate_length, plate_width = 127.76, 85.48  # mm (footprint of 96-well plate)
    elif template == "48-well plate":
        rows, cols = 6, 8
        well_spacing_x, well_spacing_y = 18.16, 18.16  # mm (center-to-center spacing for 48-well plates)
        plate_length, plate_width = 127.76, 85.48  # mm (footprint of 48-well plate)
    elif template == "μ-Slide 8 Well":
        rows, cols = 2, 4
        well_spacing_x, well_spacing_y = 19, 19  # mm (center-to-center spacing for μ-Slide 8 Well)
        plate_length, plate_width = 75.5, 25.5  # mm (footprint of μ-Slide 8 Well)
    elif template == "µ-Slide Spheroid Perfusion":
        rows, cols = 3, 7  # 3 rows with 7 wells each
        well_spacing_x = 4.5  # mm (center-to-center spacing between wells within a row)
        well_spacing_y = 9.0  # mm (center-to-center spacing between rows)
        plate_length, plate_width = 75.5, 25.5  # mm (footprint of µ-Slide Spheroid Perfusion)
    elif template == "μ-Slide 15 Well 3D":
        rows, cols = 3, 5  # 3 rows with 5 wells each
        well_spacing_x = 9  # mm (center-to-center spacing between wells within a row)
        well_spacing_y = 7  # mm (center-to-center spacing between rows)
        plate_length, plate_width = 75.5, 25.5  # mm (footprint of μ-Slide 15 Well 3D)
    elif template == "μ-Slide 18 Well":
        rows, cols = 3, 6  # 3 rows with 6 wells each
        well_spacing_x = 8.10  # mm (center-to-center spacing between wells within a row)
        well_spacing_y = 7.45  # mm (center-to-center spacing between rows)
        plate_length, plate_width = 75.5, 25.5  # mm (footprint of μ-Slide 18 Well)
    
    template_properties = (rows, cols, well_spacing_x, well_spacing_y, plate_length, plate_width)
    
    return template_properties, gcode

# Create the main window
root = ctk.CTk()
root.title("Cellink BIOX Bioprinter Control")

# Printhead type selection using a drop-down menu
ctk.CTkLabel(root, text="Printhead Type:").grid(row=1, column=0, padx=5, pady=5)
printhead_type = ctk.StringVar(value="EMD")
printhead_type_menu = ctk.CTkOptionMenu(root, variable=printhead_type, 
                                          values=["EMD",
                                                  "Pneumatic",
                                                  "Thermo-controlled",
                                                  "Syringe Pumpe"],
                                          width=140,
                                          dynamic_resizing=False
                                          )
# Update UI when printhead type changes
printhead_type.trace("w", lambda *args: update_ui()) 
printhead_type_menu.grid(row=1, column=1, padx=5, pady=5)

# Printhead number selection using a drop-down menu
ctk.CTkLabel(root, text="Printhead Number (0-2):").grid(row=1, column=2, padx=5, pady=5)
printhead_number_var = ctk.StringVar(value="0")
printhead_number_menu = ctk.CTkOptionMenu(root, variable=printhead_number_var,
                                          values=["0", "1", "2"]
                                          )
printhead_number_menu.grid(row=1, column=3, padx=5, pady=5)

# Multi-well template selection with a drop-down menu
ctk.CTkLabel(root, text="Multi-well Template:").grid(row=1, column=4, padx=5, pady=5)
template_var = ctk.StringVar(value="96-well")
template_menu = ctk.CTkOptionMenu(root, variable=template_var, 
                                          values=["96-well plate",
                                                  "48-well plate",
                                                  "μ-Slide 8 Well",
                                                  "µ-Slide Spheroid Perfusion",
                                                  "μ-Slide 15 Well 3D",
                                                  "μ-Slide 18 Well"],
                                          width=200,
                                          dynamic_resizing=False,
                                          )
template_menu.grid(row=1, column=5, padx=5, pady=5)

# General settings
ctk.CTkLabel(root, text="Printhead Speed (0-1500 mm/s):").grid(row=2, column=4, padx=5, pady=5)
printhead_speed_entry = ctk.CTkEntry(root)
printhead_speed_entry.insert(0, "1200")  # Default print speed
printhead_speed_entry.grid(row=2, column=5, padx=5, pady=5)

ctk.CTkLabel(root, text="Layer Height (0.1-1.0 mm):").grid(row=3, column=0, padx=5, pady=5)
layer_height_entry = ctk.CTkEntry(root)
layer_height_entry.insert(0, "0.1")  # Default layer height
layer_height_entry.grid(row=3, column=1, padx=5, pady=5)

ctk.CTkLabel(root, text="Bed Temperature (4-65 °C):").grid(row=3, column=4, padx=5, pady=5)
bed_temp_entry = ctk.CTkEntry(root)
bed_temp_entry.insert(0, "20")  # Default bed temperature
bed_temp_entry.grid(row=3, column=5, padx=5, pady=5)

ctk.CTkLabel(root, text="Pressure (0-200 kPa):").grid(row=2, column=0, padx=5, pady=5)
pressure_entry = ctk.CTkEntry(root)
pressure_entry.insert(0, "20")  # Default pressure
pressure_entry.grid(row=2, column=1, padx=5, pady=5)

ctk.CTkLabel(root, text="Extrussion time (s):").grid(row=2, column=2, padx=5, pady=5)
extrusion_time_entry = ctk.CTkEntry(root)
extrusion_time_entry.insert(0, "1")  # Default extrusion time
extrusion_time_entry.grid(row=2, column=3, padx=5, pady=5)

# Bedtime move position
bed_zpos_label = ctk.CTkLabel(root, text="Bed move Z position:")
bed_zpos_label.grid(row=3, column=2, padx=5, pady=5)
bed_zpos_entry = ctk.CTkEntry(root)
bed_zpos_entry.insert(0, "10")
bed_zpos_entry.grid(row=3, column=3, padx=5, pady=5)

# Wait for moves (M400)
clean_printhead_var = ctk.BooleanVar(value=False)
clean_printhead_checkbox = ctk.CTkCheckBox(root, text="Clean printhead first",
                                           variable=clean_printhead_var)
clean_printhead_checkbox.grid(row=4, column=2, padx=5, pady=5)


# Printhead-specific settings frame with a softer blue border
printhead_specific_frame = ctk.CTkFrame(root, border_width=2, border_color="#ADD8E6")  # Light blue border
printhead_specific_frame.grid(row=6, column=0, columnspan=6, padx=10, pady=5)

# # G-code display with scrollbar
# printhead_specific_title = ctk.CTkFrame(printhead_specific_frame)
# ctk.CTkLabel(printhead_specific_title, text="Printhead Specific Parameters").grid(row=0, column=0, columnspan=6, padx=5, pady=5)

# EMD settings
emd_open_time_label = ctk.CTkLabel(printhead_specific_frame, text="EMD Open Time (0-20 s):")
emd_open_time_entry = ctk.CTkEntry(printhead_specific_frame)
emd_open_time_entry.insert(0, "1")  # Default EMD open time

emd_cycle_time_label = ctk.CTkLabel(printhead_specific_frame, text="EMD Cycle Time (0-10000 µs):")
emd_cycle_time_entry = ctk.CTkEntry(printhead_specific_frame)
emd_cycle_time_entry.insert(0, "1000")  # Default EMD cycle time

# # Pneumatic settings
# pneumatic_pressure_label = ctk.CTkLabel(printhead_specific_frame, text="Pneumatic Pressure (0-200 kPa):")
# pneumatic_pressure_entry = ctk.CTkEntry(printhead_specific_frame)

# Thermo-controlled settings
thermo_temp_label = ctk.CTkLabel(printhead_specific_frame, text="Temperature (4-65 °C):")
thermo_temp_entry = ctk.CTkEntry(printhead_specific_frame)

# Syringe pump settings
syringe_extrusion_rate_label = ctk.CTkLabel(printhead_specific_frame, text="Extrusion Rate (0-1000 nL/s):")
syringe_extrusion_rate_entry = ctk.CTkEntry(printhead_specific_frame)

# Optional parameters (common for all printheads)
extrusion_volume_label = ctk.CTkLabel(printhead_specific_frame, text="Extrusion Volume (mm) (Optional):")
extrusion_volume_entry = ctk.CTkEntry(printhead_specific_frame)

pause_time_label = ctk.CTkLabel(printhead_specific_frame, text="Pause Time (s) (Optional):")
pause_time_entry = ctk.CTkEntry(printhead_specific_frame)

# G-code display with scrollbar
ctk.CTkLabel(root, text="Generated G-code:").grid(row=8, column=0, columnspan=6, padx=5, pady=5)

# Create a frame to hold the Text widget and Scrollbar
gcode_frame = ctk.CTkFrame(root)
gcode_frame.grid(row=9, column=0, columnspan=6, padx=5, pady=5, sticky="nsew")

# Create a Text widget
gcode_text = ctk.CTkTextbox(gcode_frame, width=80, height=300, wrap=ctk.NONE)
gcode_text.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

# Buttons at the bottom
button_frame = ctk.CTkFrame(root)
button_frame.grid(row=10, column=0, columnspan=6, padx=5, pady=5, sticky="ew")

# Toggle Dark Mode button on the bottom left
dark_mode_button = ctk.CTkButton(button_frame, text="Toggle Dark Mode", command=toggle_dark_mode)
dark_mode_button.pack(side=ctk.LEFT, padx=5, pady=5)

# Generate, Copy, and Export buttons on the bottom right
generate_button = ctk.CTkButton(button_frame, text="Generate G-code", command=generate_gcode)
generate_button.pack(side=ctk.RIGHT, padx=5, pady=5)

export_button = ctk.CTkButton(button_frame, text="Export G-code", command=export_gcode)
export_button.pack(side=ctk.RIGHT, padx=5, pady=5)

copy_button = ctk.CTkButton(button_frame, text="Copy to Clipboard", command=copy_to_clipboard)
copy_button.pack(side=ctk.RIGHT, padx=5, pady=5)

sweep_options_frame = ctk.CTkFrame(root, border_width=2, border_color="#ff9999")
sweep_options_frame.grid(row=7, column=0, columnspan=6, padx=10, pady=5)

# Pressure Sweep Checkbox
pressure_sweep_var = ctk.BooleanVar(value=False)
pressure_sweep_checkbox = ctk.CTkCheckBox(sweep_options_frame, 
                                          text="Pressure Sweep",
                                          variable=pressure_sweep_var,
                                          command=lambda: toggle_sweep_options("pressure"))
pressure_sweep_checkbox.grid(row=1, column=0, padx=5, pady=5)

# Temperature Sweep Checkbox
temperature_sweep_var = ctk.BooleanVar(value=False)
temperature_sweep_checkbox = ctk.CTkCheckBox(sweep_options_frame, 
                                             text="Temperature Sweep",
                                             variable=temperature_sweep_var,
                                             command=lambda: toggle_sweep_options("temperature"))
temperature_sweep_checkbox.grid(row=2, column=0, padx=5, pady=5)

# Initial and Final Value Text Boxes
pressure_initial_label = ctk.CTkLabel(sweep_options_frame, text="Initial Pressure (kPa):")
pressure_initial_label.grid(row=1, column=1, padx=5, pady=5)
pressure_initial_entry = ctk.CTkEntry(sweep_options_frame, state="disabled")
pressure_initial_entry.configure(fg_color="#d3d3d3", text_color="gray")  # Gray background and text
pressure_initial_entry.grid(row=1, column=2, padx=5, pady=5)

pressure_final_label = ctk.CTkLabel(sweep_options_frame, text="Final Pressure (kPa):")
pressure_final_label.grid(row=1, column=3, padx=5, pady=5)
pressure_final_entry = ctk.CTkEntry(sweep_options_frame, state="disabled")
pressure_final_entry.configure(fg_color="#d3d3d3", text_color="gray")  # Gray background and text
pressure_final_entry.grid(row=1, column=4, padx=5, pady=5)

temperature_initial_label = ctk.CTkLabel(sweep_options_frame, text="Initial Temp (°C):")
temperature_initial_label.grid(row=2, column=1, padx=5, pady=5)
temperature_initial_entry = ctk.CTkEntry(sweep_options_frame, state="disabled")
temperature_initial_entry.configure(fg_color="#d3d3d3", text_color="gray")  # Gray background and text
temperature_initial_entry.grid(row=2, column=2, padx=5, pady=5)

temperature_final_label = ctk.CTkLabel(sweep_options_frame, text="Final Temp (°C):")
temperature_final_label.grid(row=2, column=3, padx=5, pady=5)
temperature_final_entry = ctk.CTkEntry(sweep_options_frame, state="disabled")
temperature_final_entry.configure(fg_color="#d3d3d3", text_color="gray")  # Gray background and text
temperature_final_entry.grid(row=2, column=4, padx=5, pady=5)


# Initialize UI
update_ui()

# Bind input validation to entry fields
for entry in [printhead_speed_entry, layer_height_entry, bed_temp_entry, 
              pressure_entry, extrusion_time_entry, bed_zpos_entry,
              emd_open_time_entry, emd_cycle_time_entry,
              thermo_temp_entry,
              syringe_extrusion_rate_entry]:
    
    entry.bind("<KeyRelease>", lambda event: validate_input_fields())

# Run the application
root.mainloop()


