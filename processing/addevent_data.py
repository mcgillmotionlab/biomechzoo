import numpy as np


def addevent_data(data, ch, ename, etype):
    if isinstance(ch, str):
        ch = [ch]

    if len(ch) == 1 and ch[0].lower() == 'all':
        ch = [key for key in data if key != 'zoosystem']

    for channel in ch:
        if ename == '':
            data[channel]['event'] = {}
            continue

        if channel not in data:
            print(f'Channel {channel} does not exist')
            continue

        yd = data[channel]['line']  # 1D array
        etype = etype.lower()
        if etype == 'absmax':
            exd = int(np.argmax(np.abs(yd)))
            eyd = float(yd[exd])
        elif etype == 'first':
            exd = 0
            eyd = float(yd[exd])
        elif etype == 'last':
            exd = len(yd) - 1
            eyd = float(yd[exd])
        elif etype == 'max':
            exd = int(np.argmax(yd))
            eyd = float(yd[exd])
        elif etype == 'min':
            exd = int(np.argmin(yd))
            eyd = float(yd[exd])
        elif etype == 'rom':
            eyd = float(np.max(yd) - np.min(yd))
            exd = 0  # dummy index (like MATLAB version)
        else:
            raise ValueError(f'Unknown event type: {etype}')

        # Add event to the channel's event dict
        data[channel]['event'][ename] = [exd, eyd, 0]

    return data
