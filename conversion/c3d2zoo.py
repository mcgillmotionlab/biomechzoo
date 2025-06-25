import os
from ezc3d import c3d
from scipy.io import savemat

from biomechzoo.engine import engine
from biomechzoo.utils.zsave import zsave


def c3d2zoo(fld):
    """
    Convert all .c3d files in a folder to .zoo format (.mat with .zoo extension).

    Args:
        fld (str): Path to folder containing .c3d files
    """
    # todo: add line and event subdicts to match biomechzoo convention

    # check if we are processing a single file or folder
    if '.' in fld:
        fl = [fld]
    else:
        if not os.path.isdir(fld):
            raise NotADirectoryError('{} is not a valid directory'.format(fld))
        fl = engine(fld, extension='.c3d')

    if not fl:
        print('No C3D files found in {}'.format(fld))
        return

    for f in fl:
        c3d_path = os.path.join(fld, f)
        print('Processing {}'.format(c3d_path))

        c3d_obj = c3d(c3d_path)
        data = {}

        # todo: expand this to forces, analog, etc.
        if 'points' in c3d_obj['data']:
            points = c3d_obj['data']['points']
            labels = c3d_obj['parameters']['POINT']['LABELS']['value']
            for i, label in enumerate(labels):
                data[label] = points[:3, i, :].T  # shape: (frames, 3)

        # Save as .zoo (MATLAB-style)
        out_path = os.path.join(fld, f.replace(".c3d", ".zoo"))

        zsave(out_path, data)
        print('Saved zoo file to: {}'.format(out_path))


if __name__ == '__main__':
    """ testing: convert a c3d file to zoo and delete after"""
    from biomechzoo.utils.zload import zload
    # -------TESTING--------
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    fl = os.path.join(project_root, 'data', 'other', 'HC038A27.c3d')
    c3d2zoo(fl)

    # load the created file
    fl_zoo = fl.replace('.c3d', '.zoo')
    data = zload(fl_zoo)
    # get rid of the created file
    os.remove(fl_zoo)
