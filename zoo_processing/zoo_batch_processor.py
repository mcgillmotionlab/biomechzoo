import os
import shutil

from support_functions.zoo_handler import zload, zsave
from support_functions.engine import engine


class BatchProcessor:
    def __init__(self):
        """
        Initialize the batch processor
        """

    def removechannel(self, fld, channels_to_remove):
        """
        Remove specified channels from all .zoo files in the folder.

        Parameters:
        channels_to_remove (list or str): A list of channel names or a single channel name to be removed.

        Returns:
        None
        """
        if not isinstance(channels_to_remove, list):
            channels_to_remove = [channels_to_remove]

        # Process each .zoo file in the folder
        fl = engine(path=fld, extension=".zoo")
        for i, _ in enumerate(fl):
            data = zload(fl[i])
            print('removing channel for file {}'.format(fl[i]))

            # remove channels
            for channel_to_remove in channels_to_remove:
                value = data.pop(channel_to_remove, None)
                if value is None:
                    print('channel {} not found'.format(channels_to_remove))

            # save new data
            zsave(data, fl[i])


# Example usage:


# get original folder and copy to working folder
current_dir = os.getcwd()
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
fld = os.path.join(parent_dir, 'sample study/Data/1-c3d2zoo/')
fld_new = fld.replace('1-c3d2zoo', '2-remove_channels')
shutil.copytree(fld, fld_new, dirs_exist_ok=True)

# Initialize the batch processor
bmech = BatchProcessor()

# Remove specific channels from all zoo files in the folder
channels_to_remove = ['CLAV', 'C7']
bmech.removechannel(fld_new, channels_to_remove)
