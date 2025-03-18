# -*- coding: utf-8 -*-
"""
Created on Tue Mar  4 22:17:15 2025

@author: Maria Teresa Alameda
"""


class GCODE:
    
    """
    Class GCODE stores methods/functions to generate small sections of G-code.
    These methods are used to create G-code commands for controlling the BIO X bioprinter.
    """

    @staticmethod
    def initialize(printhead_type_value=None):
        """
        Initializes the G-code with basic setup commands.
        
        Args:
            printhead_type_value (str, optional): Type of printhead being used. Defaults to None.
        
        Returns:
            str: Initial G-code string with setup commands.
        """
        gcode = ""

        # Initialization commands
        gcode += "; Code beginning\n\n"
        if printhead_type_value is not None:
            gcode += f"; {printhead_type_value} printhead selected \n\n"
            
        gcode += "G21 ; set units to millimeters\n"
        gcode += "G90 ; use absolute coordinates\n"
        gcode += "M83 ; use relative distances for extrusion\n"
        
        return gcode
    
    @staticmethod
    def set_printhead(gcode, printhead=0):
        """
        Sets the active printhead in the G-code.
        
        Args:
            gcode (str): Existing G-code string.
            printhead (int, optional): Printhead number (0-2). Defaults to 0.
        
        Returns:
            str: Updated G-code string with printhead selection command.
        """
        gcode += f"T{printhead} ; set printhead number {printhead}\n\n"
        return gcode
    
    @staticmethod
    def set_printhead_speed(gcode, printhead_speed):
        """
        Sets the printhead speed in the G-code.
        
        Args:
            gcode (str): Existing G-code string.
            printhead_speed (float): Speed of the printhead in mm/s.
        
        Returns:
            str: Updated G-code string with printhead speed command.
        """
        gcode += f"G1 F{float(printhead_speed)} ;"
        gcode += f" Set print speed to {printhead_speed} mm/s \n\n"
        return gcode
        
    @staticmethod
    def set_bed_temperature(gcode, temperature=None):
        """
        Sets the bed temperature in the G-code.
        
        Args:
            gcode (str): Existing G-code string.
            temperature (float, optional): Bed temperature in °C. Defaults to None.
        
        Returns:
            str: Updated G-code string with bed temperature command.
        """
        if temperature is None: 
            return gcode
        else: 
            gcode += f"M801 S{float(temperature)} ; Set bed temperature\n\n"    
            return gcode
        
    @staticmethod
    def set_printhead_temperature(gcode, temperature, printhead=0):
        """
        Sets the printhead temperature in the G-code.
        
        Args:
            gcode (str): Existing G-code string.
            temperature (float): Printhead temperature in °C.
            printhead (int, optional): Printhead number (0-2). Defaults to 0.
        
        Returns:
            str: Updated G-code string with printhead temperature command.
        """
        gcode += f"M771 T{printhead} P{temperature}; Set printhead at {temperature} ºC\n"
        gcode += "\nM400 ; wait for queued moves to finish"
        return gcode
    
    @staticmethod
    def set_default_pressure(gcode, pressure, printhead=0):
        """
        Sets the default pressure for the printhead in the G-code.
        
        Args:
            gcode (str): Existing G-code string.
            pressure (float): Pressure in kPa.
            printhead (int, optional): Printhead number (0-2). Defaults to 0.
        
        Returns:
            str: Updated G-code string with default pressure command.
        """
        gcode += (f"M773 T{printhead} P{float(pressure)}" +
                  f" ; Set default pressure for printhead {printhead}\n")
        return gcode
    
    @staticmethod
    def move_to_position(gcode, x=0, y=0, z=None, speed=None, row=None, col=None):
        """
        Moves the printhead to a specific position in the G-code.
        
        Args:
            gcode (str): Existing G-code string.
            x (float, optional): X-coordinate. Defaults to 0.
            y (float, optional): Y-coordinate. Defaults to 0.
            z (float, optional): Z-coordinate. Defaults to None.
            speed (float, optional): Movement speed in mm/s. Defaults to None.
            row (int, optional): Row number for multi-well plates. Defaults to None.
            col (int, optional): Column number for multi-well plates. Defaults to None.
        
        Returns:
            str: Updated G-code string with movement command.
        """
        speed = float(speed)
        gcode += f"G0 X{x} Y{y}"
        
        if z is not None: 
            gcode += f" Z{z}"
        if speed is not None: 
            gcode += f" F{speed}"
        
        gcode += f" ; Move to X{x} Y{y}"
        
        if z is not None: 
            gcode += f" Z{z}"
        if speed is not None: 
            gcode += f" with speed {speed} mm/s"
        else: 
            gcode += " with default speed"
         
        if row is not None and col is not None:
            gcode += f" well ({row+1}, {col+1})"
        
        gcode += "\nM400 ; wait for queued moves to finish" 
        return gcode + "\n\n"
    
    @staticmethod
    def move_bed(gcode, z, speed=None):
        """
        Moves the print bed to a specific Z position in the G-code.
        
        Args:
            gcode (str): Existing G-code string.
            z (float): Z-coordinate for bed movement.
            speed (float, optional): Movement speed in mm/s. Defaults to None.
        
        Returns:
            str: Updated G-code string with bed movement command.
        """
        speed = float(speed)
        gcode += f"G0 Z{z}"
        
        if speed is not None: 
            gcode += f" F{speed}"
        
        gcode += " ; move printbed"
        
        if z == 0: 
            gcode += " up to extrusion position"
        else: 
            gcode += " down to movement position"
        
        if speed is not None: 
            gcode += f" with speed {speed} mm/s"
        else: 
            gcode += " with default speed"
        
        gcode += "\nM400 ; wait for queued moves to finish"
        return gcode + "\n\n"
    
    @staticmethod
    def dwell(gcode, dwell):
        """
        Adds a dwell (pause) command to the G-code.
        
        Args:
            gcode (str): Existing G-code string.
            dwell (float): Dwell time in seconds.
        
        Returns:
            str: Updated G-code string with dwell command.
        """
        gcode += f"G4 S{dwell} ; Pause for {dwell} seconds\n"
        return gcode
    
    @staticmethod
    def emd_extrusion(gcode, printhead, pressure, dwell):
        """
        Adds an EMD (Electro-Mechanical Dispenser) extrusion command to the G-code.
        
        Args:
            gcode (str): Existing G-code string.
            printhead (int): Printhead number (0-2).
            pressure (float): Pressure in kPa.
            dwell (float): Dwell time in seconds.
        
        Returns:
            str: Updated G-code string with EMD extrusion command.
        """
        gcode += f"M750 T{printhead} P{pressure}; Start EMD extrusion\n"
        gcode += f"G4 S{dwell} ; Pause for {dwell} seconds\n"
        gcode += f"M751 T{printhead} ; Stop EMD extrusion\n\n"
        return gcode
    
    @staticmethod
    def pneumatic_extrusion(gcode, printhead, pressure, dwell):
        """
        Adds a pneumatic extrusion command to the G-code.
        
        Args:
            gcode (str): Existing G-code string.
            printhead (int): Printhead number (0-2).
            pressure (float): Pressure in kPa.
            dwell (float): Dwell time in seconds.
        
        Returns:
            str: Updated G-code string with pneumatic extrusion command.
        """
        gcode += f"M750 T{printhead} P{pressure}; Start pneumatic extrusion"
        gcode += f" with pressure {pressure} kPa\n"
        gcode += f"G4 S{dwell} ; Pause for {dwell} seconds\n"
        gcode += f"M751 T{printhead} ; Stop pneumatic extrusion\n\n"
        return gcode
    
    @staticmethod
    def emd_extrusion_cycle(gcode, printhead, pressure, time):
        """
        Adds an EMD extrusion cycle command to the G-code.
        
        Args:
            gcode (str): Existing G-code string.
            printhead (int): Printhead number (0-2).
            pressure (float): Pressure in kPa.
            time (float): Extrusion time in seconds.
        
        Returns:
            str: Updated G-code string with EMD extrusion cycle command.
        """
        gcode += (f"M750 T{printhead} P{pressure} D{time};" 
                  f" EMD extrusion for {time} seconds\n\n")
        return gcode
    
    @staticmethod
    def thermo_extrusion(gcode, printhead, pressure, dwell):
        """
        Adds a thermo-controlled extrusion command to the G-code.
        
        Args:
            gcode (str): Existing G-code string.
            printhead (int): Printhead number (0-2).
            pressure (float): Pressure in kPa.
            dwell (float): Dwell time in seconds.
        
        Returns:
            str: Updated G-code string with thermo-controlled extrusion command.
        """
        gcode += f"M750 T{printhead} P{pressure}; Start EMD extrusion\n"
        gcode += f"G4 S{dwell} ; Pause for {dwell} seconds\n"
        gcode += f"M751 T{printhead} ; Stop EMD extrusion\n\n"
        return gcode
    
    @staticmethod
    def thermo_extrusion_cycle(gcode, printhead, pressure, time):
        """
        Adds a thermo-controlled extrusion cycle command to the G-code.
        
        Args:
            gcode (str): Existing G-code string.
            printhead (int): Printhead number (0-2).
            pressure (float): Pressure in kPa.
            time (float): Extrusion time in seconds.
        
        Returns:
            str: Updated G-code string with thermo-controlled extrusion cycle command.
        """
        gcode += (f"M750 T{printhead} P{pressure} D{time};" 
                  f" EMD extrusion for {time} seconds\n\n")
        return gcode
    

def clean_printhead(gcode, printhead_number, speed, bed_movement_position, pressure=50, time=1):
    """
    Adds a printhead cleaning routine to the G-code.
    
    Args:
        gcode (str): Existing G-code string.
        printhead_number (int): Printhead number (0-2).
        speed (float): Movement speed in mm/s.
        bed_movement_position (float): Z position for bed movement.
        pressure (float, optional): Pressure in kPa. Defaults to 50.
        time (float, optional): Extrusion time in seconds. Defaults to 1.
    
    Returns:
        str: Updated G-code string with printhead cleaning routine.
    """
    gcode += f" ; cleaning printhead number {printhead_number}\n"
    gcode = GCODE.move_to_position(gcode, -20, -50, speed=speed)
    gcode = GCODE.move_bed(gcode, z=0, speed=speed)  # bed go up - prepare to extrude
    gcode = GCODE.emd_extrusion(gcode, printhead_number, pressure, time)  # Extrusion
    gcode = GCODE.move_bed(gcode, z=bed_movement_position, speed=speed)
    gcode += f" ; finished cleaning printhead number {printhead_number}\n\n"
    return gcode