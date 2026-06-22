import numpy as np
import os
from ezc3d import c3d

from biomechzoo.utils.find_repo_root import find_repo_root
from biomechzoo.utils.zload import zload
from biomechzoo.conversion.c3d2zoo_data import c3d2zoo_data

def load_sample_zoo_file():
    """
    Load and return a sample zoo data structure from the repository.

    The sample file is used for examples, testing, and validation of
    BiomechZoo functions.

    Returns
    -------
    dict
        Zoo-format data structure generated from the sample C3D file.

    Raises
    ------
    FileNotFoundError
        If the sample C3D file cannot be found.
    """

    # Locate the repository root and construct the path to the sample C3D file.
    repo_dir = find_repo_root()
    fl = os.path.join(repo_dir,'data','sample_study','raw c3d files','HC040A','Straight','HC040A14.c3d')

    if not os.path.isfile(fl):
        raise FileNotFoundError("Sample C3D file not found: {}".format(fl))

    c3d_obj = c3d(fl)
    data = c3d2zoo_data(c3d_obj)

    return data