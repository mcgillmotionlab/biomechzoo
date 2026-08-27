import os
from typing import Any, Dict

import numpy as np
from scipy.io import loadmat


def zload(filepath: str) -> Dict:
    """
    Load a .zoo file into a zoo data dictionary.

    Parameters
    ----------
    filepath : str
        Path to the .zoo file to load.

    Returns
    -------
    data : dict
        Zoo data dictionary, with MATLAB structs converted to nested
        Python dicts and Video/Analog channel lists converted to
        Python lists of stripped strings.

    Raises
    ------
    ValueError
        If ``filepath`` does not end in ``'.zoo'``.
    FileNotFoundError
        If ``filepath`` does not exist.
    """
    if not filepath.endswith('.zoo'):
        raise ValueError(f"{filepath} is not a .zoo file")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    mat_data = loadmat(filepath, struct_as_record=False, squeeze_me=True)

    # Remove default MATLAB metadata fields
    mat_data = {k: v for k, v in mat_data.items() if not k.startswith('__')}

    # Convert MATLAB structs to Python dicts (recursively)
    def mat_struct_to_dict(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: mat_struct_to_dict(v) for k, v in obj.items()}
        elif hasattr(obj, '_fieldnames'):
            return {field: mat_struct_to_dict(getattr(obj, field)) for field in obj._fieldnames}
        elif isinstance(obj, list):
            return [mat_struct_to_dict(item) for item in obj]
        else:
            return obj
    data = {k: mat_struct_to_dict(v) for k, v in mat_data.items()}

    if 'data' in data:
        data = data['data']

    # Convert Video and Analog channel arrays to Python lists
    for sys in ['Video', 'Analog']:
        if 'zoosystem' in data and sys in data['zoosystem']:
            channels = data['zoosystem'][sys].get('Channels', [])
            # Convert to list and strip spaces
            if isinstance(channels, np.ndarray):
                channels = channels.tolist()
            channels = [str(ch).strip() for ch in channels]
            data['zoosystem'][sys]['Channels'] = channels

    return data


if __name__ == '__main__':
    """ testing: load a single zoo file from the sample_study/normalized folder"""
    # -------TESTING--------
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    fl = os.path.join(project_root, 'data', 'sample_study', 'normalized', 'HC030A', 'Straight', 'HC030A05.zoo')
    data = zload(fl)

    channels = [k for k in data.keys()]
    print('{} channels found'.format(len(channels)))
    for ch in channels:
        print({ch})
