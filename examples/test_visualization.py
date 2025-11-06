import os
from biomechzoo.biomechzoo import BiomechZoo
from biomechzoo import biomechzoo

# get raw data folder
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fld_data = os.path.join(project_root, 'data', 'sample_study', 'raw c3d files')


# set up a new 'bmech' object for processing
bmech = BiomechZoo(fld_data, inplace=False, verbose='all')

# Step 1: Conversion to the biomechZoo format -------------------------------------------
bmech.c3d2zoo(out_folder='visualization')
bmech.inplace = True

# Step 2: Normalize-------
# TODO: question ch_data_line length is 101;
#  This is the format for matlab because it starts at 1.
#  But python starts at 0, so should the length of the normalized data be 100

bmech.normalize()

# Step 3: bmech explode channel
bmech.explodechannel()

# ---- test visualisation in script----
# ensembler.average()

from biomechzoo.visualization.ensembler import Ensembler

ensembler = Ensembler(fld=bmech.in_folder, ch=['RHipAngles_x', 'RHipAngles_y', 'RHipAngles_z'], conditions=['Straight', 'Turn'])
ensembler.plot_lines()
