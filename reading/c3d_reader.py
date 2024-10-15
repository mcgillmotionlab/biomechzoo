import ezc3d


class C3DReader:
    def __init__(self, file_path):
        """
        Initialize the C3DReader by loading the .c3d file.
        """
        try:
            self.c3d_data = ezc3d.c3d(file_path)
            print('File {} loaded successfully'.format(file_path))
        except FileNotFoundError:
            raise Exception('File not found: {}'.format(file_path))
        except Exception as e:
            raise Exception('Error loading file: {}'.format(e))

    def get_marker_data(self):
        """
        Extract marker data from the .c3d file and return it as a dictionary with separate keys for each marker.
        Each key will correspond to an n x 3 matrix.
        The dictionary structure will be:
        {
            'markername': [[x1, y1, z1], [x2, y2, z2], ...],
            ...
        }
        """
        try:
            # Marker data is stored in the 'points' section
            points = self.c3d_data['data']['points']

            # Extract marker labels
            marker_labels = self.c3d_data['parameters']['POINT']['LABELS']['value']

            # Initialize the dictionary to store the data
            marker_dict = {}

            # For each marker, create a key with an n x 3 matrix
            for i, label in enumerate(marker_labels):
                # Create an n x 3 matrix for the marker
                marker_dict[label] = [
                    [points[0, i, j], points[1, i, j], points[2, i, j]]
                    for j in range(points.shape[2])
                ]

            return marker_dict
        except Exception as e:
            raise Exception('Error extracting marker data: {}'.format(e))

    def get_analog_data(self):
        """
        Extract analog data (e.g., force plate data) from the .c3d file and return it as a dictionary.
        The dictionary structure will be:
        {
            'analog_signal_name': [values],
            ...
        }
        """
        try:
            # Analog data is stored in the 'analogs' section
            analogs = self.c3d_data['data']['analogs']

            # Extract analog labels
            analog_labels = self.c3d_data['parameters']['ANALOG']['LABELS']['value']

            # Initialize the dictionary to store the analog data
            analog_dict = {label: analogs[i, :].tolist() for i, label in enumerate(analog_labels)}
            return analog_dict
        except Exception as e:
            raise Exception('Error extracting analog data: {}'.format(e))

    def get_metadata(self):
        """
        Extract metadata (e.g., frame rate, duration, etc.) from the .c3d file.
        """
        try:
            metadata = {
                'frame_rate': self.c3d_data['parameters']['POINT']['RATE']['value'][0],
                'start_frame': self.c3d_data['header']['points']['first_frame'],
                'end_frame': self.c3d_data['header']['points']['last_frame'],
            }
            return metadata
        except Exception as e:
            raise Exception('Error extracting metadata: {}'.format(e))
