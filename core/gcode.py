# -*- coding: utf-8 -*-
"""
Created on Tue Mar  4 22:17:15 2025

@author: Maite
"""
import numpy as np

class GCODE:
    
    "class GCODE stores methods/functions to generate small sections of gcode"
    
    @staticmethod
    def initialize(printhead_type_value = None, pattern = None):
        
        gcode = ""

        # Initialization commands
        gcode += "; Code beginning\n\n"
        
        if pattern is not None:
            if pattern.lower() == 'striped': gcode += "; Striped scaffold pattern.\n"
            elif pattern.lower() == 'grid': gcode += "; Grid scaffold pattern.\n"
            
        if printhead_type_value is not None:
            gcode += f"; {printhead_type_value} printhead selected \n\n"
    
        gcode += "G21 ; set units to millimeters\n"
        gcode += "G90 ; use absolute coordinates\n"
        gcode += "M83 ; use relative distances for extrusion\n\n"
        
        return gcode
    
    @staticmethod
    def set_printhead(gcode, printhead = 0, z = None):
        gcode += f"T{printhead}" 
        if z is not None: gcode += f" Z{z:.2f}"
        gcode +=f" ; set printhead number {printhead}\n\n"
        return gcode
    
    @staticmethod
    def set_printhead_speed(gcode, printhead_speed):
        gcode += f"G1 F{float(printhead_speed)} ;"
        gcode += f" Set print speed to {printhead_speed} mm/s \n\n"
    
        return gcode
        
    @staticmethod
    def set_bed_temperature(gcode, temperature = None):
        
        if temperature is None: return gcode
        else: 
            gcode += f"M801 S{float(temperature)} ; Set bed temperature\n" 
            gcode += f"M400 ; wait for bed temperature setting to finish\n\n"
            return gcode
        
    @staticmethod
    def set_printhead_temperature(gcode, temperature, printhead = 0):
        
        gcode += f"M771 T{printhead} P{temperature} ; Set printhead at {temperature} ºC\n"
        gcode += "M400 ; wait for printhead temperature setting to finish\n\n"
        
        return gcode
    
    @staticmethod
    def set_default_pressure(gcode, pressure, printhead = 0):
        
        gcode += (f"M773 T{printhead} P{float(pressure)}" +
                  f" ; Set default pressure for printhead {printhead}\n\n")
        
        return gcode
    
    @staticmethod
    def move_to_position(gcode, x = None, y = None, z = None, 
                         speed = None, row = None, col = None,
                         precise = 0, wait = True, extrusion = None):
        
        speed = float(speed)
        
        gcode += f"G{precise}"
        
        if x is not None: gcode += f" X{x:.3f}"
        if y is not None: gcode += f" Y{y:.3f}"
        
        if z is not None: gcode += f" Z{z:.2f}"
        if extrusion is not None: gcode += f" E{extrusion}"
        if speed is not None: gcode +=  f" F{speed}"
        
        if extrusion is None: gcode += " ; Move to"
        else: gcode += " ; Extruding to"
        
        if x is not None: gcode += f" X{x:.3f}"
        if y is not None: gcode += f" Y{y:.3f}"
        
        if z is not None: gcode += f" Z{z:.2f}"
        if speed is not None: gcode +=  f" with speed {speed} mm/min"
        else: gcode += " with default speed"
         
        if row is not None and col is not None:
            gcode += f" well ({row+1}, {col+1})"
        
        if wait: gcode += "\nM400 ; wait for queued moves to finish" 
        
        return gcode + "\n\n"
    
    
    @staticmethod
    def move_bed(gcode, z, speed = None):
        
        speed = float(speed)
        
        gcode += f"G0 Z{z}"
        
        if speed is not None: gcode +=  f" F{speed}"
        
        gcode += " ; move printbed"
        
        if z == 0: gcode += " up to extrussion position"
        else: gcode += " down to movement position"
        
        if speed is not None: gcode +=  f" with speed {speed} mm/s"
        else: gcode += " with default speed"
        
        gcode += "\nM400 ; wait for queued moves to finish"
        
        return gcode + "\n\n"
    
    @staticmethod
    def dwell(gcode, dwell):
        gcode += f"G4 S{dwell} ; Pause for {dwell} seconds\n"
        return gcode
    
    @staticmethod
    def emd_extrusion(gcode, printhead, pressure, dwell):
        
        seconds = int(np.trunc(dwell))
        miliseconds = int((dwell - seconds) * 1000)
        
        gcode += f"M750 T{printhead} P{pressure}; Start EMD extrusion"
        gcode += f" with pressure {pressure} kPa\n"
        
        if miliseconds != 0 and seconds != 0:
            gcode += f"G4 S{seconds} P{miliseconds}" 
            gcode += f"; Wait for {seconds} seconds and {miliseconds} miliseconds\n"
        elif miliseconds == 0:
            gcode += f"G4 S{seconds}" 
            gcode += f"; Wait for {seconds} seconds\n"
        elif seconds == 0:
            gcode += f"G4 P{miliseconds}" 
            gcode += f"; Wait for {miliseconds} miliseconds\n"
            
        gcode += f"M751 T{printhead} ; Stop EMD extrusion\n\n"
        
        return gcode
    
    
    @staticmethod
    def pneumatic_extrusion(gcode, printhead, pressure, dwell):
        
        seconds = int(np.trunc(dwell))
        miliseconds = int((dwell - seconds) * 1000)
        
        gcode += f"M750 T{printhead} P{pressure}; Start pneumatic extrusion"
        gcode += f" with pressure {pressure} kPa\n"
        
        if miliseconds != 0 and seconds != 0:
            gcode += f"G4 S{seconds} P{miliseconds}" 
            gcode += f"; Wait for {seconds} seconds and {miliseconds} miliseconds\n"
        elif miliseconds == 0:
            gcode += f"G4 S{seconds}" 
            gcode += f"; Wait for {seconds} seconds\n"
        elif seconds == 0:
            gcode += f"G4 P{miliseconds}" 
            gcode += f"; Wait for {miliseconds} miliseconds\n"
            
        gcode += f"M751 T{printhead} ; Stop pneumatic extrusion\n\n"
        
        return gcode
    
    @staticmethod
    def emd_extrusion_cycle(gcode, printhead, pressure, time):
        
        gcode += (f"M750 T{printhead} P{pressure} D{time};" 
                  f" EMD extrusion for {time} seconds\n\n")
        
        return gcode
    
    @staticmethod
    def thermo_extrusion(gcode, printhead, pressure, dwell):
        
        gcode += f"M750 T{printhead} P{pressure}; Start EMD extrusion\n"
        gcode += f"G4 S{dwell} ; Pause for {dwell} seconds\n"
        gcode += f"M751 T{printhead} ; Stop EMD extrusion\n\n"
        
        return gcode
    
    @staticmethod
    def thermo_extrusion_cycle(gcode, printhead, pressure, time):
        
        gcode += (f"M750 T{printhead} P{pressure} D{time};" 
                  f" EMD extrusion for {time} seconds\n\n")
        
        return gcode
    
    @staticmethod
    def generate_scafold_perimeter(gcode, dimensions, origin, extrusion, 
                                   layers = 1, speed = 1200):
        
        """
        Appends G-code to draw a rectangular perimeter starting from 'origin'.
        
        Parameters:
        - gcode: str, initial G-code string to append to.
        - dimensions: tuple (width, height), the rectangle's size in mm.
        - origin: tuple (x, y), starting point of the perimeter.
        - extrusion: float, amount of extrusion per side (assumed fixed).
        - speed: int, movement speed in mm/min (default: 1200).
        
        Returns:
        - Updated gcode string with perimeter moves.
        """
        
        gcode += f"; printing external perimeter at speed {speed} mm/min\n"
        
        # Set the feedrate (movement speed for extrusion moves)
        gcode += f"G1 F{speed}; set extrusion speed movement to {speed} mm/min\n"
            
        
        for i in range(4):
            
            # Current position
            x0, y0 = origin
            
            # Compute quadrant
            angle = np.arctan2(y0, x0)
            quadrant = int((angle/(np.pi/2)) % 4 + 1)
            
            # Choose direction of movement depending on quadrant
            if quadrant == 1: deltax , deltay = - dimensions[0] , 0
            elif quadrant == 2: deltax , deltay = 0 , - dimensions[1]
            elif quadrant == 3: deltax , deltay = dimensions[0] , 0
            elif quadrant == 4: deltax , deltay = 0, dimensions[0]
            
            # Append G-code move and extrusion
            gcode += (f"G1 X{x0 + deltax} Y{y0 + deltay} E{extrusion}; " +
                      f"move to point ({x0 + deltax} , {y0 + deltay}) mm\n")
            
            # Update origin value for next perimeter side
            origin = x0 + deltax , y0 + deltay
            
        return gcode
                
    @classmethod
    def generate_scaffold_stripes(cls, gcode, dimensions, origin,
                                  delta, lines, height, speed = 1200, 
                                  extrusion = 0.94):
        
        xi , yi = origin
        
        for index in range(lines - 1):
            
            xi -= delta
            
            gcode = cls.move_to_position(gcode, x = xi, y = yi, wait = False,
                                         precise = 1, speed = 3000)
            
            gcode = cls.move_to_position(gcode, z = height, speed = 3000, 
                                         precise = 1, wait = False)
            
            gcode = cls.move_to_position(gcode, x=xi, y=-yi, wait = False,
                                         precise = 1, extrusion = extrusion,
                                         speed = speed)
            
            gcode = cls.move_to_position(gcode, z = height + 1, speed = 3000,
                                         precise = 1, wait = False)
            
        return gcode         
        
        
    @staticmethod
    def generate_honeycomb_scaffold(gcode = None, 
                                    size_x=20, size_y=20, size_z=10, 
                                    wall_thickness=0.43, cell_size=5, 
                                    layer_height=0.3, print_speed=10, 
                                    printhead=0, pressure=50):
        """
        Generate honeycomb scaffold G-code for a 3D cube.
        
        Parameters:
        - size_x, size_y, size_z: Dimensions in mm (default 20×20×10mm)
        - wall_thickness: Extrusion width (default 0.43mm)
        - cell_size: Distance between hexagon centers (default 5mm)
        - layer_height: Z-step per layer (default 0.3mm)
        - print_speed: Movement speed (default 10mm/s)
        - printhead: Printhead number (default 0)
        - pressure: Extrusion pressure (default 50kPa)
        """
        if gcode is None: gcode = ""
        
        # Calculate honeycomb parameters
        hex_radius = cell_size / (3**0.5)  # Radius of circumscribed circle
        hex_side = cell_size / (3**0.5)    # Side length
        
        # Initialize printer settings
        gcode = GCODE.initialize()
        gcode = GCODE.set_printhead(gcode, printhead)
        gcode = GCODE.set_printhead_speed(gcode, print_speed)
        gcode = GCODE.set_default_pressure(gcode, pressure, printhead)
        
        # Generate layers
        z_pos = layer_height  # Start at first layer height
        while z_pos <= size_z:
            gcode += f"; LAYER at Z{z_pos:.2f}\n"
            
            # Move to start position
            start_x = -size_x/2
            start_y = -size_y/2
            gcode = GCODE.move_to_position(gcode, x=start_x, y=start_y, z=z_pos, 
                                           speed=print_speed)
            
            # Generate honeycomb pattern for this layer
            # Offset every other row for hexagonal packing
            row_offset = 0
            y_pos = start_y
            
            while y_pos < size_y/2:
                x_pos = start_x + (row_offset * hex_radius)
                
                while x_pos < size_x/2:
                    # Generate one hexagon
                    hex_points = []
                    for i in range(6):
                        angle_deg = 60 * i - 30
                        angle_rad = np.pi / 180 * angle_deg
                        x = x_pos + hex_radius * np.cos(angle_rad)
                        y = y_pos + hex_radius * np.sin(angle_rad)
                        hex_points.append((x, y))
                    
                    # Close the hexagon
                    hex_points.append(hex_points[0])
                    
                    # Generate G-code for this hexagon
                    for i, (x, y) in enumerate(hex_points):
                        if i == 0:
                            # Move to first point without extrusion
                            gcode = GCODE.move_to_position(gcode, x=x, y=y, z=z_pos, 
                                                         speed=print_speed)
                            # Start extrusion
                            gcode = GCODE.pneumatic_extrusion(gcode, printhead, 
                                                            pressure, dwell=0.1)
                        else:
                            # Extrude to next point
                            gcode = GCODE.move_to_position(gcode, x=x, y=y, z=z_pos, 
                                                         speed=print_speed)
                    
                    # Stop extrusion
                    gcode += f"M751 T{printhead} ; Stop extrusion\n"
                    
                    x_pos += 2 * hex_radius
                
                # Alternate row offset and increment y
                row_offset = 1 - row_offset
                y_pos += 1.5 * hex_side
            
            # Move to next layer
            z_pos += layer_height
        
        # Finalize
        gcode += "; Scaffold complete\n"
        return gcode
    

def clean_printhead(gcode, printhead_number, speed, bed_movement_position,
                    pressure = 50, time = 1):
    
    gcode += f"; cleaning printhead number {printhead_number}\n"
    gcode = GCODE.move_to_position(gcode, -20, -50, speed=speed)
    gcode = GCODE.move_bed(gcode, z = 0, speed=speed) # bed go up - prepare to extrude
    gcode = GCODE.emd_extrusion(gcode,
                                 printhead_number,
                                 pressure,
                                 time
                                 ) # Extrusion 
    gcode = GCODE.move_bed(gcode, z = bed_movement_position, speed = speed)
    gcode += f"; finished cleaning printhead number {printhead_number}\n\n"
    
    return gcode
    