import scipy.io
import os
import numpy as np


class ZooFileHandler:
    def __init__(self, file_path=None):
        """
        Initialize the ZooFileHandler class.

        Parameters:
        file_path (str): Optional file path to load a .zoo file initially.
        """
        self.file_path = file_path
        self.data = None
        if file_path:
            self.load_zoo_file(file_path)

    def load_zoo_file(self, file_path):
        """
        Loads a .zoo file (MAT format) and stores its contents in the class.

        Parameters:
        file_path (str): Path to the .zoo file.

        Returns:
        dict: The loaded zoo data, or None if loading fails.
        """
        if not os.path.exists(file_path):
            print('File {} not found'.format(file_path))
            return None

        try:
            # Load the .zoo (MAT) file
            data = scipy.io.loadmat(file_path, squeeze_me=True, struct_as_record=False)

            # Initialize a dictionary to hold the converted data
            zoo_data = {}

            # Assuming 'zoo_struct' is the main struct you want to convert
            if 'data' in data:
                zoo_data['data'] = self.mat_struct_to_dict(data['data'])

            self.file_path = file_path
            print('File {} loaded successfully'.format(file_path))
            return self.data
        except Exception as e:
            print('Error loading file {}: {}'.format(file_path, e))
            return None

    def mat_struct_to_dict(self, mat_struct):
        """
        Convert a mat_struct to a nested dictionary.

        Parameters:
        mat_struct: The mat_struct object to convert.

        Returns:
        dict: A nested dictionary representation of the mat_struct.
        """
        result = {}
        for field in mat_struct:
            print(field)

        value = mat_struct[field][0, 0]  # Access the field, typically as [0, 0]
        # Recursively convert the value if it's a mat_struct
        result[field] = self.mat_struct_to_dict(value)

        return result

    def save_zoo_file(self, file_path=None):
        """
        Saves the current zoo data to a .zoo file (MAT format).

        Parameters:
        file_path (str): Path where the .zoo file will be saved. If not provided,
                         it will use the original file path.

        Returns:
        bool: True if the file was saved successfully, False otherwise.
        """
        if file_path is None:
            file_path = self.file_path

        if not file_path.endswith('.zoo'):
            file_path += '.zoo'

        if self.data is None:
            print('No data to save.')
            return False

        try:
            # Save the data to a .mat file with a .zoo extension
            scipy.io.savemat(file_path, self.data)
            print('File {} saved successfully'.format(file_path))
            return True
        except Exception as e:
            print('Error saving file {}: {}'.format(file_path, e))
            return False

    def get_channel(self, channel_name):
        """
        Returns the data for a specific channel.

        Parameters:
        channel_name (str): The name of the channel to retrieve.

        Returns:
        array-like: Data for the specified channel, or None if not found.
        """
        if self.data and channel_name in self.data:
            return self.data[channel_name]
        print('Channel {} not found in the zoo file.'.format(channel_name))
        return None

    def remove_channel_data(self, channels_to_remove):
        """
        Remove specified channels from the zoo data.

        Parameters:
        channels_to_remove (list or str): A list of channel names or a single channel name to be removed.

        Returns:
        bool: True if channels were removed, False if channels were not found.
        """
        if not isinstance(channels_to_remove, list):
            channels_to_remove = [channels_to_remove]

        if self.data is None:
            print('No zoo data loaded to remove channels from.')
            return False

        channels_removed = False
        for channel in channels_to_remove:

            if channel in self.data['data']:
                del self.data['data'][channel]
                print('Channel {} removed.'.format(channel))
                channels_removed = True
            else:
                print('Channel {} not found in the zoo file.'.format(channel))

        return channels_removed
