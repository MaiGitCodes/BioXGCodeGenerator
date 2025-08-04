# File organization and folder structure.
# by Maria Teresa Alameda Felgueiras
# v 1.3.0 - bio_x_code_generator

bio_x_gcode_generator/
│── setup.py
│── README.md
│── requirements.txt
│── Folder structure.md
│── __init__.py
│── main.py                # Main application entry point
│── gui/
│   │── __init__.py
│   │── layout.py          # GUI layout definition
│   │── event_handlers.py  # Button callbacks and event handling
│   │── validation.py      # Input validation logic
│── core/
│   │── __init__.py
│   │── gcode.py           # G-code generation
│   │── templates.py       # Template management
│── utils/
│   │── __init__.py
│   │── constants.py       # Constants and configuration
