import os
from biomechzoo import BiomechZoo


# get raw data folder
project_root = os.path.dirname(os.path.abspath(__file__))
fld_raw_data = os.path.join(project_root, 'data', 'sample_study', 'raw c3d files')

# step 0: initialize object that is an instance of biomechZoo class
bmech = BiomechZoo(fld_raw_data, verbose=True)

# step 1: convert c3d to zoo
bmech.c3d2zoo()

# step 2: cleaning
ch = ['RHipAngles', 'RKneeAngles', 'RAnkleAngles']
bmech.removechannel(ch, mode='keep')

