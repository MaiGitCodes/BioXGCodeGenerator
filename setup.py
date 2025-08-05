# bio_x_gcode_generator/__init__.py

"""
BIOX G-Code Generator Setup file

A GUI application for generating G-code for Cellink BIOX bioprinters.
"""

from setuptools import setup, find_packages

setup(
    name="bio_x_gcode_generator",
    version="1.3.8b",
    author="Maria Teresa Alameda Felgueiras",
    description="G-code generator for Cellink BIOX bioprinters",
    long_description=open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MaiGitCodes/BioXGCodeGenerator.git",
    packages=find_packages(),
    install_requires=[
        "customtkinter>=5.2.0",
        "numpy>=1.21.0",
        "packaging>=21.0"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "bio-x-gcode=bio_x_gcode_generator.main:main",
        ],
    },
)


