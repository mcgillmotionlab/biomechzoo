import os
import pandas as pd
from biomechzoo.utils.engine import engine
from biomechzoo.utils.zload import zload
from biomechzoo.utils.findfield import findfield  # assuming this exists

def eventval(fld, dim1=None, dim2=None, ch=None, localevts=None, globalevts=None, anthroevts=None):
    """
    Extract event values from .zoo files and compile into a pandas DataFrame.

    Parameters
    ----------
    fld : str
        Path to the root data folder containing .zoo files.
    dim1 : list of str, optional
        List of conditions (subfolder names under fld).
    dim2 : list of str, optional
        List of participant identifiers.
    ch : list of str
        List of channels to extract events from.
    localevts : list of str, optional
        List of local events.
    globalevts : list of str, optional
        List of global events.
    anthroevts : list of str, optional
        List of events stored in the metadata.Usually anthropometric data

    Returns
    -------
    pd.DataFrame
        Columns: ['condition', 'subject', 'file', 'event_name', 'event_value']
    """

    zoo_files = engine(fld, extension='.zoo')
    results = []
    files_excluded = []
    for fl in zoo_files:
        data = zload(fl)
        fname = os.path.basename(fl)
        condition = next((c for c in (dim1 or []) if c in fl), '')
        subject = next((s for s in (dim2 or []) if s in fl), '')

        # Skip file if condition or subject is empty

        if not condition or not subject:
            files_excluded.append(fl)
            continue
        else:
            print('processing {}'.format(fl))

        # --- Local events ---
        if localevts and ch:
            print('extracting local events...')
            for channel in ch:
                if channel not in data:
                    print('channel {} not found'.format(channel))
                    continue
                for evt in localevts:
                    try:
                        exd = int(data[channel]['event'][evt][0])  # xdata
                        eyd = data[channel]['event'][evt][1]  # ydata
                        results.append({
                            'condition': condition,
                            'subject': subject,
                            'file': fname,
                            'event_name': f"{channel}_{evt}",
                            'event_index': exd,
                            'event_value': eyd
                        })
                    except (KeyError, IndexError, TypeError) as e:
                        print(f"Local event '{evt}' not found in channel '{channel}' for file '{fname}'")

        # --- Global events ---
        if globalevts and ch:
            print('extracting global events...')
            for evt in globalevts:
                # use findfield to locate where the global event is stored
                evt_val, evt_ch = findfield(data, evt)
                if not evt_ch:
                    print(f"Global event '{evt}' not found in any channel for file '{fname}'")
                    continue

                exd = int(evt_val[0])
                for channel in ch:
                    if channel not in data:
                        print(f"Skipping {evt}: channel {channel} not in data")
                        continue
                    try:
                        eyd = data[channel]['line'][exd]
                        results.append({
                            'condition': condition,
                            'subject': subject,
                            'file': fname,
                            'event_name': f"{channel}_{evt}",
                            'event_index': exd,
                            'event_value': eyd
                        })
                    except (IndexError, KeyError, TypeError) as e:
                        print(f"Global event '{evt}' index out of range in channel '{channel}' for file '{fname}': {e}")

        if anthroevts and ch:
            raise NotImplementedError
            print('extracting anthropometric events...')
            for evt in globalevts:
                # use findfield to locate where the global event is stored
                evt_val, _ = findfield(data, evt)

                if evt_val:
                    results.append({
                        'condition': condition,
                        'subject': subject,
                        'file': fname,
                        'event_name': evt,
                        'event_index': evt_val[0],
                        'event_value': evt_val[1]
                    })

    return pd.DataFrame(results)
