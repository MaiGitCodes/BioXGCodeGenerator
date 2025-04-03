#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main application entry point for BIOX G-Code 

@author: Maria Teresa Alameda Felgueiras
"""
import customtkinter as ctk
from gui.layout import create_main_window
from gui.event_handlers import setup_event_handlers
from utils.constants import APP_TITLE, DEFAULT_MODE, DEFAULT_COLOR

def main():
    
    ctk.set_appearance_mode(DEFAULT_MODE)
    ctk.set_default_color_theme(DEFAULT_COLOR)
    
    root = ctk.CTk()
    root.title(APP_TITLE)
    
    # Create and configure main window
    app_components = create_main_window(root)
    
    # Set up event handlers
    setup_event_handlers(root, app_components)
    
    root.mainloop()

if __name__ == "__main__":
    main()
