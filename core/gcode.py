# -*- coding: utf-8 -*-
"""
Created on Tue Mar  4 22:17:15 2025

@author: Maite
"""
import numpy as np

class GCODE:
    
    "class GCODE stores methods/functions to generate small sections of gcode"
    
    @staticmethod
    def initialize(printhead_type_value = None):
        
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
    def set_printhead(gcode, printhead = 0):
        gcode += f"T{printhead} ; set printhead number {printhead}\n\n"
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
    def move_to_position(gcode, x = 0, y = 0, z = None, 
                         speed = None, row = None, col = None):
        
        speed = float(speed)
        
        gcode += f"G0 X{x} Y{y}"
        
        if z is not None: gcode += f" Z{z}"
        if speed is not None: gcode +=  f" F{speed}"
        
        gcode += f" ; Move to X{x} Y{y}"
        
        if z is not None: gcode += f" Z{z}"
        if speed is not None: gcode +=  f" with speed {speed} mm/s"
        else: gcode += " with default speed"
         
        if row is not None and col is not None:
            gcode += f" well ({row+1}, {col+1})"
        
        gcode += "\nM400 ; wait for queued moves to finish" 
        
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
    