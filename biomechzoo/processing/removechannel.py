import scipy.io


def remove_channel(zoo_path, channel_name, output_path=None):
    """
    Remove a channel (variable) from a .zoo (MATLAB .mat) file.

    Arguments:
        zoo_path (str): Path to input .zoo file.
        channel_name (str): Name of the channel/variable to remove.
        output_path (str, optional): Path to save modified .zoo file.
            If None, overwrite original file.

    Returns:
        None
    """

    # todo create a zload function to replace this call?
    data = scipy.io.loadmat(zoo_path, squeeze_me=True, struct_as_record=False)

    # MATLAB .mat files have metadata keys starting with '__', ignore them
    keys_to_remove = [k for k in data.keys() if k.startswith('__')]
    for k in keys_to_remove:
        data.pop(k, None)

    if channel_name not in data:
        print(f"Channel '{channel_name}' not found in {zoo_path}")
        return

    data.pop(channel_name)  # Remove the channel

    save_path = output_path if output_path else zoo_path
    scipy.io.savemat(save_path, data)
    print('Saved modified zoo file to {}'.format(save_path))


if __name__ == '__main__':
    import os
     """ testing: test removing channels from an existing zoo file 
     """
     # -------TESTING--------
     # get path to file and load it
     current_dir = os.path.dirname(os.path.abspath(__file__))
     project_root = os.path.dirname(current_dir)
     fl = os.path.join(project_root, 'data', 'other', 'HC002D006.zoo')
     data = zload(fl)

# select channels to remove as list and remove
     chn_rm = ['RKneeAngles', 'LASI']
     remove_channel(data, channel_name=chn_rm)

    
