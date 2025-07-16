#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete event handlers for BIOX G-Code Generator

@author: Maria Teresa Alameda Felgueiras
"""
import numpy as np
import math
from tkinter import messagebox, filedialog
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from ..core.gcode import GCODE as GC
from ..core.gcode import clean_printhead
from ..core.templates import set_template
from ..gui.validation import validate_inputs, validate_input_fields
from .gcode_generation_tools import (generate_droplet_gcode,
                                     generate_scafold_gcode,
                                     calculate_geometric_parameters,
                                     calculate_lines)

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
    
    # Scaffold preview button
    components['scaffold_preview_button'].configure(
        command=lambda: preview_scaffold_perimeter(components)
    )
    
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
    
    if not on_tab_change(components):
        print('droplet')
        generate_droplet_gcode(components)
    else:
        generate_scafold_gcode(components)
        # components['gcode_text'].delete("1.0", ctk.END)
        print('Scafold')    

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

# Define callback for tab switching
def on_tab_change(components):
    selected_tab = components['tabview'].get()
    scafold_view = (selected_tab == 'Scafold settings')
    print(scafold_view)
    # Optional: print(components['scafold'])  # for debugging
    return scafold_view

def preview_scaffold_perimeter(components):
    try:
        pattern = components['scaffold_pattern_var'].get()
        size_x = float(components['scaffold_size_x_entry'].get())
        size_y = float(components['scaffold_size_y_entry'].get())
        infill = float(components['scaffold_infill_entry'].get())
        wall_thickness = float(components['scaffold_noozle_entry'].get())
        layer_height = float(components['scaffold_layer_height_entry'].get())
        size_z = float(components['layer_number_entry'].get()) * layer_height
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric values")
        return
    
    # Clear previous plot
    ax = components['scaffold_ax']
    ax.clear()
    plot_origin(ax)
    plot_perimeter(ax, size_x, size_y, size_z, layer_height)
    plot_stripe_infill(ax, components)
    components['scaffold_canvas'].draw()

    
    
    
def preview_scaffold_3d(components):
    """Generate and display a 3D preview of the scaffold pattern"""
    # Get parameters from UI
    try:
        pattern = components['scaffold_pattern_var'].get()
        size_x = float(components['scaffold_size_x_entry'].get())
        size_y = float(components['scaffold_size_y_entry'].get())
        cell_size = float(components['scaffold_cell_size_entry'].get())
        wall_thickness = float(components['scaffold_wall_thickness_entry'].get())
        layer_height = float(components['scaffold_layer_height_entry'].get())
        size_z = float(components['layer_number_entry'].get()) * layer_height
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric values")
        return
    
    # Clear previous plot
    ax = components['scaffold_ax']
    ax.clear()
    
    # Set plot limits
    ax.set_xlim([-size_x/2, size_x/2])
    ax.set_ylim([-size_y/2, size_y/2])
    ax.set_zlim([0, size_z])
    ax.set_box_aspect([size_x, size_y, size_z])
    
    # Generate and plot the scaffold
    if pattern == "Honeycomb":
        plot_honeycomb_3d(ax, size_x, size_y, size_z, cell_size, wall_thickness, layer_height)
    elif pattern == "Grid":
        plot_grid_3d(ax, size_x, size_y, size_z, cell_size, wall_thickness, layer_height)
    elif pattern == "Triangular":
        plot_triangular_3d(ax, size_x, size_y, size_z, cell_size, wall_thickness, layer_height)
    
    # Set title and refresh
    ax.set_title(f"{pattern} Scaffold\nDimensions: {size_x}x{size_y}x{size_z}mm", y=1.0, pad=-20)
    components['scaffold_canvas'].draw()
    
def plot_origin(ax):
    
    ax.scatter(0.,0.,0., color = 'black', marker='x', s=50)

def plot_perimeter(ax, size_x, size_y, size_z, layer_height, cmap='plasma',
                   steps_per_segment = 5):
    
    from mpl_toolkits.mplot3d.art3d import Line3DCollection
    from matplotlib import cm
    from matplotlib.colors import Normalize

    x0 = size_x / 2
    y0 = size_y / 2

    points = [
        [x0, y0],
        [x0 - size_x, y0],
        [x0 - size_x, y0 - size_y],
        [x0, y0 - size_y],
        [x0, y0]
    ]

    segments = []
    colors = []

    total_segments = (len(points) - 1) * int(size_z / layer_height) * steps_per_segment
    color_norm = Normalize(0, total_segments)
    cmap_func = cm.get_cmap(cmap)

    segment_index = 0
    for z in np.arange(0, size_z, layer_height):
        for i in range(len(points) - 1):
            p1 = np.array([*points[i], z])
            p2 = np.array([*points[i + 1], z])

            # Interpolate small steps along this segment
            for t in np.linspace(0, 1, steps_per_segment + 1)[:-1]:
                start = p1 * (1 - t) + p2 * t
                end = p1 * (1 - (t + 1 / steps_per_segment)) + p2 * (t + 1 / steps_per_segment)
                segments.append([start, end])
                colors.append(cmap_func(color_norm(segment_index)))
                segment_index += 1

    collection = Line3DCollection(segments, colors=colors, linewidth=3)
    ax.add_collection3d(collection)

    # Set plot limits
    all_x = [p[0] for p in points]
    all_y = [p[1] for p in points]
    ax.set_xlim(min(all_x) - 10, max(all_x) + 10)
    ax.set_ylim(min(all_y) - 10, max(all_y) + 10)
    ax.set_zlim(0, size_z + 5)

def plot_stripe_infill(ax, components, cmap = 'plasma', steps_per_segment = 5):
    
    from mpl_toolkits.mplot3d.art3d import Line3DCollection
    from matplotlib import cm
    from matplotlib.colors import Normalize

    lines, delta = calculate_lines(components)
    dimensions, origin, extrusion = calculate_geometric_parameters(components)
    
    xi , yi = origin
        
    for index in range(lines - 1):
        
        xi -= delta
        segments = []
        colors = []

        total_segments = (lines - 1)  * steps_per_segment
        color_norm = Normalize(0, total_segments)
        cmap_func = cm.get_cmap(cmap)

        segment_index = 0
        # Interpolate small steps along this segment
        for t in np.linspace(0, 1, steps_per_segment + 1)[:-1]:
            p1 = np.array([xi, yi, 0.])
            p2 = np.array([xi, -yi, 0.])
            start = p1 * (1 - t) + p2 * t
            end = p1 * (1 - (t + 1 / steps_per_segment)) + p2 * (t + 1 / steps_per_segment)
            segments.append([start, end])
            colors.append(cmap_func(color_norm(segment_index)))
            segment_index += 1
            
        collection = Line3DCollection(segments, colors=colors, linewidth=extrusion)
        ax.add_collection3d(collection)
    
def plot_honeycomb_3d(ax, size_x, size_y, size_z, cell_size, wall_thickness, layer_height):
    """Plot a 3D honeycomb scaffold"""
    hex_radius = cell_size / (3**0.5)
    hex_side = cell_size / (3**0.5)
    
    # Calculate number of cells
    rows = int(size_y / (1.5 * hex_side))
    cols = int(size_x / (2 * hex_radius))
    
    # Generate layers
    for z in np.arange(0, size_z, layer_height):
        # Offset every other row for hexagonal packing
        row_offset = 0 if (z/layer_height) % 2 == 0 else 1
        
        for row in range(-rows, rows):
            for col in range(-cols, cols):
                x = (col * 2 * hex_radius) + (row_offset * hex_radius)
                y = row * 1.5 * hex_side
                
                # Check if within bounds
                if abs(x) > size_x/2 or abs(y) > size_y/2:
                    continue
                
                # Generate hexagon points
                points = []
                for i in range(7):  # 6 sides + close loop
                    angle_deg = 60 * i - 30
                    angle_rad = np.pi / 180 * angle_deg
                    px = x + hex_radius * np.cos(angle_rad)
                    py = y + hex_radius * np.sin(angle_rad)
                    points.append([px, py])
                
                # Plot vertical walls
                for i in range(6):
                    ax.plot(
                        [points[i][0], points[i+1][0]],
                        [points[i][1], points[i+1][1]],
                        [z, z],
                        color='blue',
                        linewidth=wall_thickness*2
                    )
                
                # Plot horizontal connections if not first layer
                if z > 0:
                    for i in range(6):
                        ax.plot(
                            [points[i][0], points[i][0]],
                            [points[i][1], points[i][1]],
                            [z-layer_height, z],
                            color='blue',
                            linewidth=wall_thickness*2
                        )

def plot_grid_3d(ax, size_x, size_y, size_z, cell_size, wall_thickness, layer_height):
    """Plot a 3D grid scaffold"""
    # Calculate number of cells
    rows = int(size_y / cell_size)
    cols = int(size_x / cell_size)
    
    # Generate layers
    for z in np.arange(0, size_z, layer_height):
        for row in range(-rows, rows):
            for col in range(-cols, cols):
                x = col * cell_size
                y = row * cell_size
                
                # Check if within bounds
                if abs(x) > size_x/2 or abs(y) > size_y/2:
                    continue
                
                # Plot vertical lines
                ax.plot(
                    [x, x + cell_size],
                    [y, y],
                    [z, z],
                    color='green',
                    linewidth=wall_thickness*2
                )
                ax.plot(
                    [x, x],
                    [y, y + cell_size],
                    [z, z],
                    color='green',
                    linewidth=wall_thickness*2
                )
                
                # Plot horizontal connections if not first layer
                if z > 0:
                    ax.plot(
                        [x, x],
                        [y, y],
                        [z-layer_height, z],
                        color='green',
                        linewidth=wall_thickness*2
                    )

def plot_triangular_3d(ax, size_x, size_y, size_z, cell_size, wall_thickness, layer_height):
    """Plot a 3D triangular scaffold"""
    # Calculate number of cells
    rows = int(size_y / (cell_size * 0.866))  # 0.866 = sin(60°)
    cols = int(size_x / cell_size)
    
    # Generate layers
    for z in np.arange(0, size_z, layer_height):
        # Alternate orientation every layer
        orientation = 'up' if (z/layer_height) % 2 == 0 else 'down'
        
        for row in range(-rows, rows):
            for col in range(-cols, cols):
                x = col * cell_size
                y = row * cell_size * 0.866  # Vertical spacing
                
                # Offset every other column
                if orientation == 'down':
                    x += cell_size / 2
                
                # Check if within bounds
                if abs(x) > size_x/2 or abs(y) > size_y/2:
                    continue
                
                # Generate triangle points
                if orientation == 'up':
                    points = [
                        [x, y],
                        [x + cell_size/2, y + cell_size * 0.866],
                        [x - cell_size/2, y + cell_size * 0.866]
                    ]
                else:
                    points = [
                        [x, y + cell_size * 0.866],
                        [x + cell_size/2, y],
                        [x - cell_size/2, y]
                    ]
                
                # Plot triangle
                for i in range(3):
                    ax.plot(
                        [points[i][0], points[(i+1)%3][0]],
                        [points[i][1], points[(i+1)%3][1]],
                        [z, z],
                        color='red',
                        linewidth=wall_thickness*2
                    )
                
                # Plot vertical connections if not first layer
                if z > 0:
                    for i in range(3):
                        ax.plot(
                            [points[i][0], points[i][0]],
                            [points[i][1], points[i][1]],
                            [z-layer_height, z],
                            color='red',
                            linewidth=wall_thickness*2
                        )

  
# def preview_scaffold_pattern(components):
#     """Generate and display a preview of the scaffold pattern"""
#     canvas = components['scaffold_canvas']
#     canvas.delete("all")  # Clear previous drawing
    
#     # Get parameters from UI
#     try:
#         cell_size = float(components['scaffold_cell_size_entry'].get())
#         wall_thickness = float(components['scaffold_wall_thickness_entry'].get())
#         pattern = components['scaffold_pattern_var'].get()
#     except ValueError:
#         messagebox.showerror("Error", "Please enter valid numeric values")
#         return
    
#     # Canvas dimensions
#     width = canvas.winfo_width()
#     height = canvas.winfo_height()
#     scale = min(width, height) / (cell_size * 3)  # Scale to fit
    
#     # Draw based on pattern type
#     if pattern == "Honeycomb":
#         draw_honeycomb_pattern(canvas, cell_size, scale, width, height)
#     elif pattern == "Grid":
#         draw_grid_pattern(canvas, cell_size, scale, width, height)
#     elif pattern == "Triangular":
#         draw_triangular_pattern(canvas, cell_size, scale, width, height)
        
#     # Add scale indicator (1mm reference)
#     draw_scale_indicator(canvas, scale, width, height)


# def draw_scale_indicator(canvas, scale, width, height):
#     """Draw a scale indicator (1mm reference) in the bottom right corner"""
#     scale_length = 1 * scale  # 1mm in canvas units
#     padding = 10  # pixels from edge
    
#     # Position at bottom right
#     x_start = width - padding - scale_length
#     y_pos = height - padding
    
#     # Draw the scale line
#     canvas.create_line(
#         x_start, y_pos,
#         x_start + scale_length, y_pos,
#         fill='red', width=2
#     )
    
#     # Draw end markers
#     marker_size = 5
#     canvas.create_line(
#         x_start, y_pos - marker_size,
#         x_start, y_pos + marker_size,
#         fill='red', width=2
#     )
#     canvas.create_line(
#         x_start + scale_length, y_pos - marker_size,
#         x_start + scale_length, y_pos + marker_size,
#         fill='red', width=2
#     )
    
#     # Add label
#     canvas.create_text(
#         x_start + scale_length/2, y_pos - 10,
#         text="1 mm",
#         fill='red',
#         font=('Helvetica', 8, 'bold')
#     )
        
# def draw_honeycomb_pattern(canvas, cell_size, scale, width, height):
#     """Draw a honeycomb pattern preview with scale"""
#     hex_radius = cell_size / (3**0.5)
#     center_x, center_y = width/2, height/2
    
#     # Draw a single hexagon centered in the canvas
#     points = []
#     for i in range(6):
#         angle_deg = 60 * i - 30
#         angle_rad = np.pi / 180 * angle_deg
#         x = center_x + hex_radius * scale * np.cos(angle_rad)
#         y = center_y + hex_radius * scale * np.sin(angle_rad)
#         points.extend([x, y])
    
#     canvas.create_polygon(points, outline='black', fill='', width=2)
    
#     # Draw neighboring hexagons to show the pattern
#     for dx, dy in [(1, 0), (-1, 0), (0.5, 0.866), (-0.5, 0.866), 
#                    (0.5, -0.866), (-0.5, -0.866)]:
#         neighbor_points = []
#         for i in range(6):
#             angle_deg = 60 * i - 30
#             angle_rad = np.pi / 180 * angle_deg
#             x = center_x + (hex_radius * dx * 1.5 * scale + 
#                            hex_radius * scale * np.cos(angle_rad))
#             y = center_y + (hex_radius * dy * 1.5 * scale + 
#                            hex_radius * scale * np.sin(angle_rad))
#             neighbor_points.extend([x, y])
        
#         canvas.create_polygon(neighbor_points, outline='gray', fill='', width=1)
    
#     # Add dimension indicators for cell size
#     draw_cell_dimension(canvas, center_x, center_y, hex_radius, scale, "honeycomb")

# def draw_grid_pattern(canvas, cell_size, scale, width, height):
#     """Draw a grid pattern preview with scale"""
#     center_x, center_y = width/2, height/2
#     half_size = cell_size * scale / 2
    
#     # Draw center square
#     canvas.create_rectangle(
#         center_x - half_size, center_y - half_size,
#         center_x + half_size, center_y + half_size,
#         outline='black', width=2
#     )
    
#     # Draw neighboring squares
#     for dx, dy in [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,1), (1,-1), (-1,-1)]:
#         canvas.create_rectangle(
#             center_x + dx*cell_size*scale - half_size,
#             center_y + dy*cell_size*scale - half_size,
#             center_x + dx*cell_size*scale + half_size,
#             center_y + dy*cell_size*scale + half_size,
#             outline='gray', width=1
#         )
    
#     # Add dimension indicators for cell size
#     draw_cell_dimension(canvas, center_x, center_y, cell_size/2, scale, "grid")

# def draw_triangular_pattern(canvas, cell_size, scale, width, height):
#     """Draw a triangular pattern preview with scale"""
#     center_x, center_y = width/2, height/2
    
#     # Draw center triangle
#     points = []
#     for i in range(3):
#         angle_deg = 120 * i - 90
#         angle_rad = np.pi / 180 * angle_deg
#         x = center_x + cell_size * scale * np.cos(angle_rad)
#         y = center_y + cell_size * scale * np.sin(angle_rad)
#         points.extend([x, y])
    
#     canvas.create_polygon(points, outline='black', fill='', width=2)
    
#     # Draw neighboring triangles
#     for dx, dy in [(1, 0), (-1, 0), (0.5, 0.866), (-0.5, 0.866), 
#                    (0.5, -0.866), (-0.5, -0.866)]:
#         neighbor_points = []
#         for i in range(3):
#             angle_deg = 120 * i - 90
#             angle_rad = np.pi / 180 * angle_deg
#             x = center_x + (cell_size * dx * scale + 
#                            cell_size * scale * np.cos(angle_rad))
#             y = center_y + (cell_size * dy * scale + 
#                            cell_size * scale * np.sin(angle_rad))
#             neighbor_points.extend([x, y])
        
#         canvas.create_polygon(neighbor_points, outline='gray', fill='', width=1)
    
#     # Add dimension indicators for cell size
#     draw_cell_dimension(canvas, center_x, center_y, cell_size, scale, "triangular")

# def draw_cell_dimension(canvas, center_x, center_y, size, scale, pattern_type):
#     """Draw dimension indicators for the cell size"""
#     color = 'blue'
#     offset = 15
    
#     if pattern_type == "honeycomb":
#         # Draw diameter of hexagon
#         x1 = center_x - size * scale
#         x2 = center_x + size * scale
#         y = center_y + size * scale + offset
        
#         canvas.create_line(x1, y, x2, y, fill=color, width=1, arrow=ctk.BOTH)
#         canvas.create_text(
#             center_x, y + 10,
#             text=f"{size*2:.1f} mm",
#             fill=color,
#             font=('Helvetica', 8)
#         )
        
#     elif pattern_type == "grid":
#         # Draw width of square
#         x1 = center_x - size * scale
#         x2 = center_x + size * scale
#         y = center_y + size * scale + offset
        
#         canvas.create_line(x1, y, x2, y, fill=color, width=1, arrow=ctk.BOTH)
#         canvas.create_text(
#             center_x, y + 10,
#             text=f"{size*2:.1f} mm",
#             fill=color,
#             font=('Helvetica', 8)
#         )
        
#     elif pattern_type == "triangular":
#         # Draw side length
#         x1 = center_x
#         y1 = center_y - size * scale
#         x2 = center_x + size * scale * math.cos(math.radians(30))
#         y2 = center_y + size * scale * math.sin(math.radians(30))
        
#         mid_x = (x1 + x2) / 2
#         mid_y = (y1 + y2) / 2
        
#         # Calculate perpendicular offset
#         angle = math.atan2(y2-y1, x2-x1) + math.pi/2
#         offset_x = 10 * math.cos(angle)
#         offset_y = 10 * math.sin(angle)
        
#         canvas.create_line(
#             x1 + offset_x, y1 + offset_y,
#             x2 + offset_x, y2 + offset_y,
#             fill=color, width=1, arrow=ctk.BOTH
#         )
#         canvas.create_text(
#             mid_x + offset_x * 1.5, mid_y + offset_y * 1.5,
#             text=f"{size:.1f} mm",
#             fill=color,
#             font=('Helvetica', 8)
#         )