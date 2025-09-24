import numpy as np
import os
import scipy.io as sio
from biomechzoo.utils.findfield import findfield


def split_trial_by_gait_cycle(fl, event_name):
    """ splits lengthy trials containing n cycles into n trials based on side"""

    # extract folder and file name
    fld = os.path.dirname(fl)
    fl_name = os.path.splitext(os.path.basename(fl))[0]

    # load file
    data = zload(fl)

    # find all events, events should follow style name1, name2, etc..
    split_events = []
    i = 1
    _, channel_name = findfield(data, event_name)
    event_name_root = event_name[0:-1]
    while True:
        key = f"{event_name_root}{i}"
        if key in data[channel_name]['event']:
            split_events.append(data[channel_name]['event'][key])
            i += 1
        else:
            break

    n_segments = len(split_events) - 1
    if n_segments < 1:
        print("Not enough {} events to split.".format(event_name_root))
        return

    for i in range(n_segments):

        start = split_events[i][0]
        end = split_events[i + 1][0]
        fl_new = os.path.join(fld, fl_name + '_' + str(i+1) + '.zoo')
        data_new = _split_trial(fld, fl_new, start, end)

def _split_trial(fld, fl_new, start, end):
    raise NotImplementedError

if __name__ == '__main__':
    """ testing: load a single zoo file from the other subfolder in data"""
    # -------TESTING--------
    from src.biomechzoo.utils.zload import zload
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    fl = os.path.join(project_root, 'data', 'other', 'HC030A05.zoo')
    split_trial_by_gait_cycle(fl, event_name='Right_FootStrike1')
