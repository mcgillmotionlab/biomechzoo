import os
from biomechzoo import BiomechZoo

# get raw data folder
project_root = os.path.dirname(os.path.abspath(__file__))
fld_raw_data = os.path.join(project_root, 'data', 'sample_study', 'raw c3d files')

# step 0: initialize object that is an instance of biomechZoo class
bmech = BiomechZoo(fld_raw_data, verbose='all', inplace=False)

# step 1: convert c3d to zoo
bmech.c3d2zoo(out_folder='1-c3d2zoo')

# step 2: cleaning
ch = ['RHipAngles', 'RKneeAngles', 'RAnkleAngles', 'SACR']
bmech.removechannel(ch, mode='keep', out_folder='2-removechannel')

# step 3: explode channels
bmech.explodechannel(out_folder='3-explodechannels')

# step 4: add Right foot strike event
bmech.addevent(out_folder='4-addevent')

# step 5: partition from right foot strike 1 to right foot strike 2
bmech.partition(out_folder='5-partition')

# step 4: normalize data
bmech.normalize(nlen=101, out_folder='4-normalize')