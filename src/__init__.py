"""
BiomechZoo: A Python toolbox for processing and analyzing human movement data.

This package provides functions for converting, processing, analyzing,
and visualizing biomechanical data (e.g., motion capture, EMG, kinetics).

Example:
    from biomechzoo import BiomechZoo
    from biomechzoo.conversion import c3d2zoo

    zoo = BiomechZoo()
    zoo.conversion.c3d2zoo('path/to/data')
"""

# Import main class or entry point
from .biomechzo import BiomechZoo

# Import commonly used submodules
from . import conversion
from . import processing
from . import plotting
from . import utils

# Define what gets exposed with "from biomechzoo import *"
__all__ = [
    "BiomechZoo",
    "conversion",
    "processing",
    "plotting",
    "utils",
]

__version__ = "0.4.4"
