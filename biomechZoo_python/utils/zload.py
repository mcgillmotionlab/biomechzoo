import os
import scipy.io

from src.mat_struct_to_dict import mat_struct_to_dict


def zload(file_path, verbose=False):
    """
    Loads a .zoo file (MAT format) and returns its contents as a Python dictionary.

    Parameters:
    file_path (str): Path to the .zoo file (MAT format).

    Returns:
    dict: A dictionary containing the contents of the .zoo file, or None if loading fails.
    """
    # todo: mat2struct is slow, needs to be sped up

    # Check if the file exists
    if not os.path.exists(file_path):
        print('File {} not found'.format(file_path))
        return None

    try:
        # Load the .zoo (MAT) file
        data = scipy.io.loadmat(file_path, squeeze_me=True, struct_as_record=False)
        data = data['data']
        data = mat_struct_to_dict(data)

        if verbose:
            print('File {} loaded successfully'.format(file_path))

        # Return the loaded data
        return data

    except Exception as e:
        print('Error loading file {}: {}'.format(file_path, e))
        return None


if __name__ == '__main__':
    import os
    CURRENT_DIR = os.getcwd()
    DATA_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..', 'data', 'sample_study'))
    fl = os.path.join(DATA_DIR, '1-c3d2zoo', 'HC002D', 'Turn', 'HC002D25.zoo')
    zload(fl)