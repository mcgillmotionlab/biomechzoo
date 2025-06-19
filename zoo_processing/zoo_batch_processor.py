import os
import shutil

from support_functions.engine import engine
from support_functions.zsave import zsave
from support_functions.zload import zload
from removechannel_data import removechannel_data


class BatchProcessor:
    def __init__(self):
        """
        Initialize the batch processor
        """

    @staticmethod
    def removechannel(fld, channels_to_remove):
        """
        Remove specified channels from all .zoo files in the folder.

        Parameters:
            fld (str): Full path to the folder to operate on
            channels_to_remove (list or str): A list of channel names or a single channel name to be removed.

        Returns:
            None
        """
        # todo: update inputs to match Matlab version

        if not isinstance(channels_to_remove, list):
            channels_to_remove = [channels_to_remove]

        # Process each .zoo file in the folder
        fl = engine(path=fld, extension=".zoo")
        for i, _ in enumerate(fl):
            data = zload(fl[i])
            print('removing channels for file {}'.format(fl[i]))

            # remove channels using _data function
            data = removechannel_data(data, channels_to_remove)

            # save new data
            zsave(fl[i], data)


# Example usage:


# get original folder and copy to working folder
current_dir = os.getcwd()
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
fld = os.path.join(parent_dir, 'sample_study/Data/1-c3d2zoo/')
fld_new = fld.replace('1-c3d2zoo', '2-remove_channels')
shutil.copytree(fld, fld_new, dirs_exist_ok=True)

# Initialize the batch processor
bmech = BatchProcessor()

# Remove specific channels from all zoo files in the folder
channels_to_remove = ['CLAV', 'C7']
bmech.removechannel(fld_new, channels_to_remove)

# open a process zoo file to check
fl_1 = os.path.join(fld_new, 'HC002D', 'Turn', 'HC002D25.zoo')
zdata = zload(fl_1)
