#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete event handlers for BIOX G-Code Generator

@author: Maria Teresa Alameda Felgueiras
"""
import numpy as np
from tkinter import messagebox, filedialog
import customtkinter as ctk
from ..gui.validation import validate_inputs, validate_input_fields
from .gcode_generation_tools import (generate_droplet_gcode,
                                     generate_scaffold_gcode,
                                     calculate_geometric_parameters,
                                     calculate_lines, calculate_honeycomb_lines)

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
        command=lambda: preview_scaffold(components)
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
    
    components['scaffold_export_button'].configure(
    command=lambda: export_preview_image(components)
    )
    
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
        generate_scaffold_gcode(components)
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
            
def export_preview_image(components):
    """Save the current scaffold preview as a PNG file"""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png")],
        title="Save Scaffold Preview"
    )
    if file_path:
        try:
            components['scaffold_fig'].savefig(file_path, dpi=300)
            messagebox.showinfo("Success", "Preview saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preview: {e}")


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
    scafold_view = (selected_tab == 'Scaffold settings')
    print(scafold_view)
    # Optional: print(components['scafold'])  # for debugging
    return scafold_view

def preview_scaffold(components):
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
    if pattern.lower() == 'striped': plot_stripe_infill(ax, components)
    elif pattern.lower() == 'grid': plot_grid_infill(ax, components)
    elif pattern.lower() == 'honeycomb':
        print('hi')
        plot_honeycomb_infill(ax, components)
    
    if components['show_axes_var'].get():
        ax.set_xlabel("X (mm)")
        ax.set_ylabel("Y (mm)")
        ax.set_zlabel("Z (mm)")
        ax.grid(True)
        ax.set_axis_on()
    else:
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_zlabel("")
        ax.grid(False)
        ax.set_axis_off()
    components['scaffold_canvas'].draw()

def plot_origin(ax):
    
    ax.scatter(0.,0.,0., color = 'black', marker='x', s=20)

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
    
    extrusion = float(components['scaffold_extrusion_entry'].get())
    layer_height = float(components['scaffold_layer_height_entry'].get())
    size_z = float(components['layer_number_entry'].get()) * layer_height
    
    xi , yi = origin
    
    color_norm = Normalize(0, (lines - 1))
    cmap_func = cm.get_cmap(cmap)
    
    for index in range(lines - 1):
        
        xi -= delta
        segments = []
        colors = []

        for z in np.arange(0, size_z, layer_height):
            segment_index = 0
            # Interpolate small steps along this segment
            for t in np.linspace(0, 1, steps_per_segment + 1)[:-1]:
                p1 = np.array([xi, yi, z])
                p2 = np.array([xi, -yi, z])
                start = p1 * (1 - t) + p2 * t
                end = p1 * (1 - (t + 1 / steps_per_segment)) + p2 * (t + 1 / steps_per_segment)
                segments.append([start, end])
                colors.append(cmap_func(color_norm(segment_index)))
                segment_index += 1
            
        collection = Line3DCollection(segments, colors=cmap_func(color_norm(index)), linewidth=extrusion)
        ax.add_collection3d(collection)
        
def plot_grid_infill(ax, components, cmap = 'plasma', steps_per_segment = 5):
    
    from mpl_toolkits.mplot3d.art3d import Line3DCollection
    from matplotlib import cm
    from matplotlib.colors import Normalize
    
    lines, delta = calculate_lines(components, pattern = 'grid')
    dimensions, origin, extrusion = calculate_geometric_parameters(components)
    
    xi , yi = origin
    
    extrusion = float(components['scaffold_extrusion_entry'].get())
    layer_height = float(components['scaffold_layer_height_entry'].get())
    size_z = float(components['layer_number_entry'].get()) * layer_height
    
    color_norm = Normalize(0, (lines - 1))
    cmap_func = cm.get_cmap(cmap)
    
    for index in range(lines - 1):
        
        xi -= delta
        segments = []
        colors = []

        for z in np.arange(0, size_z, layer_height):
            segment_index = 0
            # Interpolate small steps along this segment
            for t in np.linspace(0, 1, steps_per_segment + 1)[:-1]:
                p1 = np.array([xi, yi, z])
                p2 = np.array([xi, -yi, z])
                start = p1 * (1 - t) + p2 * t
                end = p1 * (1 - (t + 1 / steps_per_segment)) + p2 * (t + 1 / steps_per_segment)
                segments.append([start, end])
                segment_index += 1
                
        collection = Line3DCollection(segments, colors=cmap_func(color_norm(index)), linewidth=extrusion)
        ax.add_collection3d(collection)
        
    xi , yi = origin
        
    for index in range(lines - 1):
        
        yi -= delta
        segments = []
        colors = []
        
        for z in np.arange(0, size_z, layer_height):
            segment_index = 0
            # Interpolate small steps along this segment
            for t in np.linspace(0, 1, steps_per_segment + 1)[:-1]:
                p1 = np.array([xi, yi, z])
                p2 = np.array([-xi, yi, z])
                start = p1 * (1 - t) + p2 * t
                end = p1 * (1 - (t + 1 / steps_per_segment)) + p2 * (t + 1 / steps_per_segment)
                segments.append([start, end])
                colors.append(cmap_func(color_norm(segment_index)))
                segment_index += 1
                
        collection = Line3DCollection(segments, colors=colors, linewidth=extrusion)
        ax.add_collection3d(collection)
    
def plot_honeycomb_infill(ax, components, cmap='plasma'):
    from mpl_toolkits.mplot3d.art3d import Line3DCollection
    from matplotlib import cm
    from matplotlib.colors import Normalize
    
    lines, delta = calculate_lines(components, pattern='honeycomb')
    dimensions, origin, extrusion = calculate_geometric_parameters(components)
    
    xi, yi = origin
    extrusion_width = float(components['scaffold_extrusion_entry'].get())
    layer_height = float(components['scaffold_layer_height_entry'].get())
    layers = int(float(components['layer_number_entry'].get()))
    
    # Honeycomb parameters
    hex_spacing = delta
    hex_radius = hex_spacing / np.sqrt(3)
    hex_side = hex_spacing / np.sqrt(3)
    
    # Calculate bounds with extrusion margin
    x_min = -dimensions[0]/2 + extrusion/2
    x_max = dimensions[0]/2 - extrusion/2
    y_min = -dimensions[1]/2 + extrusion/2
    y_max = dimensions[1]/2 - extrusion/2
    
    color_norm = Normalize(0, layers-1)
    cmap_func = cm.get_cmap(cmap)
    
    for layer in range(layers):
        z = layer * layer_height
        row_offset = layer % 2
        segments = []
        
        # Calculate number of complete hexagons that fit
        rows = int((y_max - y_min) / (1.5 * hex_side)) + 1
        cols = int((x_max - x_min) / (hex_side * np.sqrt(3))) + 1
        
        for row in range(-rows, rows+1):
            for col in range(-cols, cols+1):
                # Calculate center position with offset for even rows
                x_center = col * hex_side * np.sqrt(3)
                if row % 2 == 1:
                    x_center += hex_side * np.sqrt(3)/2
                y_center = row * 1.5 * hex_side
                
                # Skip if center is outside bounds
                if not (x_min <= x_center <= x_max and y_min <= y_center <= y_max):
                    continue
                
                # Generate hexagon vertices
                vertices = []
                for i in range(6):
                    angle = np.radians(60 * i + 30)
                    x = x_center + hex_radius * np.cos(angle)
                    y = y_center + hex_radius * np.sin(angle)
                    vertices.append((x, y, z))
                
                # Only draw 3 sides per hexagon
                sides_to_draw = [(0,1), (1,2), (2,3)] if layer % 2 == 0 else [(3,4), (4,5), (5,0)]
                
                for start, end in sides_to_draw:
                    x1, y1, z1 = vertices[start]
                    x2, y2, z2 = vertices[end]
                    
                    # Clip to boundaries
                    x1_clip = max(x_min, min(x_max, x1))
                    y1_clip = max(y_min, min(y_max, y1))
                    x2_clip = max(x_min, min(x_max, x2))
                    y2_clip = max(y_min, min(y_max, y2))
                    
                    # Skip if line segment is completely outside
                    if (x1_clip == x2_clip and y1_clip == y2_clip):
                        continue
                    
                    segments.append([(x1_clip, y1_clip, z1), (x2_clip, y2_clip, z2)])
        
        # Create collection
        collection = Line3DCollection(segments, 
                                     colors=cmap_func(color_norm(layer)),
                                     linewidth=extrusion_width)
        ax.add_collection3d(collection)