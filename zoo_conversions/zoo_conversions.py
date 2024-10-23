import ezc3d

from support_functions.zsave import zsave
from support_functions.zload import zload
from support_functions.checkinput import checkinput


def c3d_to_zoo(fld, delFile=False, verbose=False):
    """ convert c3d file located at fl into dictionary with easily accessible marker data

    Arguments:
        fld      ... str, full path to folder containing c3d files
        delFile  ... bool. If true, delete original files
        verbose ... bool, Default = False. If true, information about processing printed to screen
    Returns:
        data    ... dict, c3d file with markers as keys and coordinates as values

    Notes:
        - For details on reading c3d with ezc3d see:
        https://github.com/pyomeca/ezc3d#python-3
    """
    #todo implement file deletion

    [_, fl, saveFile] = checkinput(fld, '.c3d')

    if verbose:
        print('converting c3d to zoo for: {}'.format(fl))

    for i, _ in enumerate(fl):
        # load c3d object
        d = ezc3d.c3d(fl[i])

        # add all markers to a dictionary
        marker_names = d['parameters']['POINT']['LABELS']['value']  # marker names
        point_data = d['data']['points']  # 4xNxT, where 4 represent the components XYZ1
        data = {}
        for j, marker_name in enumerate(marker_names):
            data[marker_name] = point_data[0:3, j, :].T  # we only want XYZ components in N X 3 format

        # add analog data to dictionary
        analog_names = d['parameters']['ANALOG']['LABELS']['value']
        analog_data = d['data']['analogs']
        for j, analog_name in enumerate(analog_names):
            data[analog_name] = analog_data[0:3, j, :].T  # we only want XYZ components in N X 3 format

        # add meta information
        if 'parameters' in d.keys():
            data['parameters'] = {}
            params = list(d['parameters'].keys())
            for param in params:
                data['parameters'][param] = d['parameters'][param]

        # header
        if 'header' in d.keys():
            data['header'] = {}
            headers = list(d['header'].keys())
            for header in headers:
                data['header'][param] = d['header'][header]

        # save data
        if saveFile:
            zsave(fl[i], data)

    return data


if __name__ == "__main__":
    import os
    # For basic testing

    # load a c3d file from the sample_study
    current_dir = os.getcwd()
    parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
    fl_c3d = os.path.join(parent_dir, 'sample_study/Data/raw c3d files/HC002D/Straight/HC002D06.c3d')
    fl_zoo = fl_c3d.replace('c3d', 'zoo')

    # convert to zoo
    data1 = c3d_to_zoo(fl_c3d, verbose=True)

    # load zoo file
    data2 = zload(fl_zoo)

    # compare