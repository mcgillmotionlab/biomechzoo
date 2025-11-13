import os
from biomechzoo.biomechzoo import BiomechZoo

# get raw data folder
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fld_data = os.path.join(project_root, 'data', 'sample_study', 'opencap files')


#%% set up a new 'bmech' object for processing
bmech = BiomechZoo(fld_data, inplace=False, verbose='all')

#%% Step 1: Conversion to the biomechZoo format -------------------------------------------
# bmech.c3d2zoo(out_folder='visualization c3d')
bmech.table2zoo(extension='csv', out_folder='visualization opencap')
bmech.inplace = True

#%% Step 2: Normalize-------
# bmech.normalize()

# Step 3: bmech explode channel
bmech.explodechannel()

# ---- test visualisation in script----
from biomechzoo.visualization.ensembler import Ensembler

# Initialize the ensembler class and create the subplot bones
ensembler = Ensembler(fld=bmech.in_folder, ch=['hip_flexion_r', 'knee_angle_r', 'ankle_angle_r'],
                      conditions=['Pre', 'Post'],
                      name_contains=["jogging"],
                      side="_r")

# Populate the figure with individual gait cycles and save it to file
ensembler.cycles()
ensembler.save(file_name="individual gait cycles")

# Populate the figure with the average and standard deviation per condition. 
ensembler.average()
ensembler.save(file_name="average gait cycles")

# TODO: priority add markers/event
# TODO: priority super-impose the pre-Post/turn-straight whatever conditions there are.
# TODO: is there a way to hide the cycles. without the legend?
# TODO: find method to deal with outliers.
