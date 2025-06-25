import os
from biomechzoo import BiomechZoo


# get raw data folder
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
fld_raw_data = os.path.join(project_root, 'data', 'sample_study', 'raw c3d files')


# step 0: initialize object that is an instance of biomechZoo class
bmech = BiomechZoo(fld_raw_data, verbose=True)


# step 0: convert c3d to zoo



bmech.normalize()