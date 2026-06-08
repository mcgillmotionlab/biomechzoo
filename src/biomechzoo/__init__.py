"""
BiomechZoo: A Python toolbox for processing and analyzing human movement data.

This package provides functions for converting, processing, analyzing,
and visualizing biomechanical data (e.g., motion capture, EMG, kinetics).

Example:
    from biomechzoo import BiomechZoo
    from biomechzoo.conversion import c3d2zoo

    zoo = BiomechZoo('path/to/data')
"""

# Import main class or entry point
from .biomechzoo import BiomechZoo

# Import commonly used submodules
from . import conversion
from . import processing
from . import visualization
from . import utils

# Define what gets exposed with "from biomechzoo import *"
__all__ = [
    "BiomechZoo",
    "conversion",
    "processing",
    "visualization",
    "utils",
]

__version__ = "0.8.4"
