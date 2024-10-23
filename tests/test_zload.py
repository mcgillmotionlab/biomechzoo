import unittest
import os

from support_functions.zload import zload


CURRENT_DIR = os.getcwd()
DATA_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..', 'sample_study', 'Data'))


class TestZload(unittest.TestCase):

    def setUp(self):
        """Setup resources for testing."""
        # Path to a valid and invalid .zoo (MAT) file for testing purposes.
        self.valid_zoo_file = os.path.join(DATA_DIR, '1-c3d2zoo', 'HC002D', 'Turn', 'HC002D25.zoo')
        self.inexistant_zoo_file = 'idontexist.zoo'
        # self.invalid_zoo_file = os.path.join(DATA_DIR, 'raw c3d files', 'HC002D', 'Straight', 'HC002D06.c3d')

    def test_zload_valid_file(self):
        """Test zload with a valid .zoo file."""
        zoo_data = zload(self.valid_zoo_file)
        self.assertIsNotNone(zoo_data, "zload should return data for valid .zoo file")
        self.assertIn('zoosystem', zoo_data, "zoo_data should contain 'channel1'")

    def test_zload_file_not_found(self):
        """Test zload with a non-existent file."""
        zoo_data = zload(self.inexistant_zoo_file)
        self.assertIsNone(zoo_data, "zload should return None for a non-existent file")

    # def test_zload_invalid_format(self):
    #     """Test zload with an invalid format or corrupt file."""
    #     # Create an invalid .zoo file (for example, a text file instead of MAT format)
    #     with open(self.invalid_zoo_file, 'w') as f:
    #         f.write("This is not a valid .mat file.")
    #
    #     zoo_data = zload(self.invalid_zoo_file)
    #     self.assertIsNone(zoo_data, "zload should return None for an invalid file format")


if __name__ == '__main__':
    unittest.main()
