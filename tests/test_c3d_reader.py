import unittest
from reading.c3d_reader import C3DReader


class TestC3DReader(unittest.TestCase):

    def setUp(self):
        """Set up test environment and load a sample .c3d file from the sample study."""
        self.file_path = 'sample study/Data/raw c3d files/HC002D/Straight/HC002D06.c3d'
        self.reader = C3DReader(self.file_path)

    def test_marker_data(self):
        """Test that marker data is extracted correctly."""
        marker_data = self.reader.get_marker_data()
        self.assertIsInstance(marker_data, dict)
        # You can add more specific assertions here based on expected output

    def test_analog_data(self):
        """Test that analog data is extracted correctly."""
        analog_data = self.reader.get_analog_data()
        self.assertIsInstance(analog_data, dict)
        # Add assertions based on expected output

    def test_metadata(self):
        """Test that metadata is extracted correctly."""
        metadata = self.reader.get_metadata()
        self.assertIsInstance(metadata, dict)
        # Add assertions based on expected output


if __name__ == '__main__':
    unittest.main()
