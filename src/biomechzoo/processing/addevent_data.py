import numpy as np
import copy
import warnings
from typing import Dict, List, Union, Optional, Any
from scipy.signal import find_peaks
from biomechzoo.utils.peak_sign import peak_sign
from biomechzoo.biomech_ops.movement_onset import movement_onset, movement_offset
from biomechzoo.imu.step_detection import imu_mcgrath

def addevent_data(
        data: Dict[str, Any], channels: Union[str, List[str]], ename: str,
        etype: str, fsamp: Optional[float] = None,
        constant: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Add events to specified channels in a biomechanical data structure.

    This function creates events based on various event types (e.g., max, min, peaks,
    movement onset/offset, force plate thresholds) and adds them to the specified
    channels in the data dictionary.

    Parameters
    ----------
    data : dict of str to Any
        Biomechanical data dictionary containing channels and zoosystem metadata.
    channels : str or list of str
        Channel name(s) to add events to. Pass ``'all'`` to apply to all channels.
    ename : str
        Name of the event to add. Use empty string to clear all events.
    etype : str
        Event type, one of: 'max', 'min', 'absmax', 'first', 'last', 'rom',
        'first peak', 'movement_onset', 'movement_offset', 'mcgrath_fs',
        'mcgrath_fo', 'fs_fp', 'fo_fp'.
    fsamp : float, optional
        Sampling frequency in Hz. If None, extracted from zoosystem metadata.
    constant : float, optional
        Threshold or parameter value for certain event types (e.g., peak
        height threshold, force plate threshold).

    Returns
    -------
    data_new : dict of str to Any
        Deep copy of input data with events added to specified channels.

    Raises
    ------
    KeyError
        If specified channel does not exist in data.
    ValueError
        If event type is unknown or if required peaks are not found.
    Warning
        If video and analog sampling rates differ for force plate events.

    Notes
    -----
    Event format in data structure: [index, value, 0] where index is the frame
    number, value is the signal value at that frame, and 0 is a placeholder.

    For event types that find multiple events (mcgrath_fs, mcgrath_fo), events
    are numbered sequentially (e.g., 'ename_1', 'ename_2', etc.).

    Channels must already be 1-D (e.g. an exploded ``'<ch>_x'`` component)
    for 'max', 'min', 'absmax', 'first', 'last', and 'rom'; passing a
    multi-dimensional channel (e.g. an unexploded n x 3 marker) causes
    ``np.argmax``/``np.argmin`` to return a flat index into the whole
    array rather than a per-row index, which will raise an
    ``IndexError`` or silently select the wrong frame. Use
    :func:`explodechannel_data` first if needed.
    """

    data_new = copy.deepcopy(data)

    if isinstance(channels, str):
        channels = [channels]

    if len(channels) == 1 and channels[0].lower() == 'all':
        channels = [key for key in data if key != 'zoosystem']

    for channel in channels:
        if ename == '':
            data[channel]['event'] = {}
            continue

        if channel not in data:
            raise KeyError('Channel {} does not exist'.format(channel))

        # todo extract sampling frequency (needed for some events)
        # if channel in data['zoosystem']['Video']['Channels']:
        #     fsamp = data['zoosystem']['Video']['Freq']
        # elif channel in data['zoosystem']['Analog']['Channels']:
        #     fsamp = data['zoosystem']['Analog']['Freq']
        # else:
        #     raise ValueError('Cannot extract sampling frequency associated with data')

        if fsamp is None:
            fsamp = data['zoosystem']['Video']['Freq']

        yd = data_new[channel]['line']  # 1D array
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
        elif etype == 'first peak':
            # special event for gait and running
            exd = find_first_peak(yd, constant)
            eyd = float(yd[exd])
        elif etype == 'movement_onset':
            exd = movement_onset(yd, fsamp, constant)
            eyd = yd[exd]
        elif etype == 'movement_offset':
            exd = movement_offset(yd, fsamp, constant)
            eyd = yd[exd]
        elif etype == 'mcgrath_fs':
            if constant is None:
                constant = 95
            IC, _ = imu_mcgrath(yd, fsamp, min_stance_t=constant)
            exd = [int(ic) for ic in IC]
            ey = []
            for i, ex in enumerate(exd):
                ey.append(yd[ex])
            eyd = [float(y) for y in ey]
        elif etype == 'mcgrath_fo':
            if constant is None:
                constant = 95
            _, TC = imu_mcgrath(yd, fsamp, min_stance_t=constant)
            exd = [int(tc) for tc in TC]
            ey = []
            for i, ex in enumerate(exd):
                ey.append(yd[ex])
            eyd = [float(y) for y in ey]
        elif etype in ['fs_fp', 'fo_fp']:
            # --- Handle constant ---
            if constant is None:
                print('Warning: Force plate threshold not set, defaulting to 0.')
                constant = 0.0

            # --- Check sampling rates ---
            AVR = data['zoosystem']['AVR']
            if AVR != 1:
                warnings.warn('Video and Analog channels must be at the same sampling rate or events will be incorrect.')

            # --- Handle units ---
            units = data['zoosystem']['Units']['Forces']
            if units == 'N/kg':
                m = data['zoosystem']['Anthro']['Bodymass']
            else:
                m = 1.0

            # --- Extract force signal ---
            if '_' not in channel:
                yd = data_new[channel]['line'][:, 2]  # looking for GRF Z
            else:
                yd = data_new[channel]['line']

            # --- Determine peak sign ---
            peak = peak_sign(yd)  # user-defined function

            # --- Find threshold crossing ---
            threshold_signal = peak * yd * m
            if 'fs' in etype:
                exd_array = np.where(threshold_signal > constant)[0]
                exd = exd_array[0] - 1  # MATLAB indexing correction
                eyd = yd[exd]
            else:  # 'FO' type
                exd_array = np.where(threshold_signal > constant)[0]
                exd = exd_array[-1] + 1
                eyd = yd[exd]
        else:
            raise ValueError(f'Unknown event type: {etype}')

        # Add event to the channel's event dict
        if isinstance(exd, list):
            for i, ex in enumerate(exd):
                name = ename + '_' + str(i + 1)
                data_new[channel]['event'][name] = [int(ex), eyd[i], 0]
        else:
            data_new[channel]['event'][ename] = [exd, eyd, 0]

    return data_new

def find_first_peak(yd: np.ndarray, constant: Optional[float]) -> int:
    """
    Extract the index of the first peak from a multi-peak signal.

    Parameters
    ----------
    yd : ndarray
        1-D signal data array to search for peaks.
    constant : float or None
        Minimum height threshold for peak detection.

    Returns
    -------
    exd : int
        Index of the first peak in the signal.

    Raises
    ------
    ValueError
        If fewer than 2 peaks are found.
    """
    # Find peaks above threshold
    peaks, _ = find_peaks(yd, height=constant)

    if len(peaks) == 0:
        raise ValueError('No peaks found')
    elif len(peaks) == 1:
        raise ValueError('Only 1 peak found')
    else:
        # Take the first valid peak
        exd = peaks[0]

    return exd