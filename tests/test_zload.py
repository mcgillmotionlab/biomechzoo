import unittest
import os
from support_functions.support_functions import zload


class TestZooFunctions(unittest.TestCase):

    def setUp(self):
        """Setup resources for testing."""
        # Path to a valid .zoo (MAT) file for testing purposes.
        # You can create a sample file or mock one if needed.
        self.valid_zoo_file = 'test_data/valid_file.zoo'
        self.invalid_zoo_file = 'test_data/invalid_file.zoo'

        # Ensure the test directory exists and create a mock .zoo file
        os.makedirs('test_data', exist_ok=True)
        # Create a dummy .zoo (MAT) file with simple data (for testing)
        import scipy.io
        scipy.io.savemat(self.valid_zoo_file, {'channel1': [1, 2, 3], 'channel2': [4, 5, 6]})

    def tearDown(self):
        """Clean up after tests."""
        # Remove the test .zoo files after testing
        if os.path.exists(self.valid_zoo_file):
            os.remove(self.valid_zoo_file)
        if os.path.exists(self.invalid_zoo_file):
            os.remove(self.invalid_zoo_file)

    def test_zload_valid_file(self):
        """Test zload with a valid .zoo file."""
        zoo_data = zload(self.valid_zoo_file)
        self.assertIsNotNone(zoo_data, "zload should return data for valid .zoo file")
        self.assertIn('channel1', zoo_data, "zoo_data should contain 'channel1'")
        self.assertIn('channel2', zoo_data, "zoo_data should contain 'channel2'")

    def test_zload_file_not_found(self):
        """Test zload with a non-existent file."""
        zoo_data = zload(self.invalid_zoo_file)
        self.assertIsNone(zoo_data, "zload should return None for a non-existent file")

    def test_zload_invalid_format(self):
        """Test zload with an invalid format or corrupt file."""
        # Create an invalid .zoo file (for example, a text file instead of MAT format)
        with open(self.invalid_zoo_file, 'w') as f:
            f.write("This is not a valid .mat file.")

        zoo_data = zload(self.invalid_zoo_file)
        self.assertIsNone(zoo_data, "zload should return None for an invalid file format")


if __name__ == '__main__':
    unittest.main()
