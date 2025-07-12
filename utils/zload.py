from scipy.io import loadmat
import os


def zload(filepath):
    if not filepath.endswith('.zoo'):
        raise ValueError(f"{filepath} is not a .zoo file")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    mat_data = loadmat(filepath, struct_as_record=False, squeeze_me=True)

    # Remove default MATLAB metadata fields
    mat_data = {k: v for k, v in mat_data.items() if not k.startswith('__')}

    # Convert MATLAB structs to Python dicts (recursively)
    def mat_struct_to_dict(obj):
        if isinstance(obj, dict):
            return {k: mat_struct_to_dict(v) for k, v in obj.items()}
        elif hasattr(obj, '_fieldnames'):
            return {field: mat_struct_to_dict(getattr(obj, field)) for field in obj._fieldnames}
        elif isinstance(obj, list):
            return [mat_struct_to_dict(item) for item in obj]
        else:
            return obj

    return {k: mat_struct_to_dict(v) for k, v in mat_data.items()}


if __name__ == '__main__':
    """ testing: load a single zoo file from the other subfolder in data"""
    # -------TESTING--------
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    fl = os.path.join(project_root, 'data', 'other', 'HC030A05.zoo')
    data = zload(fl)
    # todo: solve the data.data problem in the same was as Matlab
    data = data['data']
    channels = [k for k in data.keys()]
    print('{} channels found'.format(len(channels)))
    for ch in channels:
        print({ch})

# import os
# import scipy.io
#
# from src.mat_struct_to_dict import mat_struct_to_dict
#
#
# def zload(file_path, verbose=False):
#     """
#     Loads a .zoo file (MAT format) and returns its contents as a Python dictionary.
#
#     Parameters:
#     file_path (str): Path to the .zoo file (MAT format).
#
#     Returns:
#     dict: A dictionary containing the contents of the .zoo file, or None if loading fails.
#     """
#     # todo: mat2struct is slow, needs to be sped up
#
#     # Check if the file exists
#     if not os.path.exists(file_path):
#         print('File {} not found'.format(file_path))
#         return None
#
#     try:
#         # Load the .zoo (MAT) file
#         data = scipy.io.loadmat(file_path, squeeze_me=True, struct_as_record=False)
#         data = data['data']
#         data = mat_struct_to_dict(data)
#
#         if verbose:
#             print('File {} loaded successfully'.format(file_path))
#
#         # Return the loaded data
#         return data
#
#     except Exception as e:
#         print('Error loading file {}: {}'.format(file_path, e))
#         return None
#
#
# if __name__ == '__main__':
#     import os
#     CURRENT_DIR = os.getcwd()
#     DATA_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..', 'data', 'sample_study'))
#     fl = os.path.join(DATA_DIR, '1-c3d2zoo', 'HC002D', 'Turn', 'HC002D25.zoo')
#     zload(fl)