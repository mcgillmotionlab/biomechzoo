import os
from ezc3d import c3d
from scipy.io import savemat

from bmech.engine import engine


def c3d2zoo(fld):
    """
    Convert all .c3d files in a folder to .zoo format (.mat with .zoo extension).

    Args:
        fld (str): Path to folder containing .c3d files
    """
    if not os.path.isdir(fld):
        raise NotADirectoryError('{} is not a valid directory'.format(fld))

    fl = engine(fld)
    fl = [f for f in os.listdir(fld) if f.lower().endswith(".c3d")]
    if not fl:
        print('No C3D files found in {}'.format(fld))
        return

    for f in fl:
        c3d_path = os.path.join(fld, f)
        print('Processing {}'.format(c3d_path))

        c3d_obj = c3d(c3d_path)
        data = {}

        # Example: extract marker data (you can expand this to forces, analog, etc.)
        if 'points' in c3d_obj['data']:
            points = c3d_obj['data']['points']
            labels = c3d_obj['parameters']['POINT']['LABELS']['value']
            for i, label in enumerate(labels):
                data[label] = points[:3, i, :].T  # shape: (frames, 3)

        # Save as .zoo (MATLAB-style)
        out_path = os.path.join(fld, f.replace(".c3d", ".zoo"))
        savemat(out_path, data)
        print(f"Saved zoo file: {out_path}")
