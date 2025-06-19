import os


def fileparts(file):
    """
   Splits the file path into directory, filename, and extension.

   Arguments:
   file_path -- str. The full file path.

   Returns:
   tuple -- (directory, filename, extension)
   """

    directory = os.path.dirname(file)
    basename = os.path.basename(file)
    filename, ext = os.path.splitext(basename)

    return directory, filename, ext
