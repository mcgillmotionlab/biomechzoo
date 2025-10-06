import numpy as np
from pathlib import Path
from biomechzoo.utils.version import get_biomechzoo_version


def set_zoosystem(fl=None):
    """
    Create the 'zoosystem' branch for data being imported to BiomechZoo.

    Args:
        fl: str
            Path to the source file (e.g., C3D or CSV).

    Returns:
        zoosystem: dict
            Dictionary containing default BiomechZoo system parameters.
    """

    # Default top-level fields
    zch = ['Analog', 'Anthro', 'AVR', 'CompInfo', 'SourceFile',
           'Units', 'Version', 'Video']

    # Initialize top-level dict
    zoosystem = {key: {} for key in zch}

    # Section-specific defaults
    section = ['Video', 'Analog']
    for sec in section:
        zoosystem[sec]['Channels'] = []
        zoosystem[sec]['Freq'] = []
        zoosystem[sec]['Indx'] = []
        zoosystem[sec]['ORIGINAL_START_FRAME'] = []
        zoosystem[sec]['ORIGINAL_END_FRAME'] = []
        zoosystem[sec]['CURRENT_START_FRAME'] = []
        zoosystem[sec]['CURRENT_END_FRAME'] = []

    # Processing and AVR defaults
    zoosystem['Processing'] = ''
    zoosystem['AVR'] = 0

    # Force plates defaults
    zoosystem['Analog']['FPlates'] = {
        'CORNERS': [],
        'NUMUSED': 0,
        'LOCALORIGIN': [],
        'LABELS': []
    }

    # Version and source file
    zoosystem['Version'] = get_biomechzoo_version()
    if fl is None:
        zoosystem['SourceFile'] = 'None'  # ensure string
    else:
        zoosystem['SourceFile'] = str(Path(fl))  # ensure string

    # Units defaults
    zoosystem['Units'] = {
        'Markers': 'mm',
        'Angles': 'deg',
        'Forces': 'N',
        'Moments': 'Nmm',
        'Power': 'W/kg',
        'Scalars': 'mm'
    }

    return zoosystem