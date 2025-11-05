import os
from biomechzoo.biomechzoo import BiomechZoo

# get raw data folder
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fld_data = os.path.join(project_root, 'data', 'sample_study', 'raw c3d files')


# set up a new 'bmech' object for processing
bmech = BiomechZoo(fld_data, inplace=False, verbose='all')

# Step 1: Conversion to the biomechZoo format -------------------------------------------
bmech.c3d2zoo(out_folder='visualization')
bmech.inplace = True

# Step 2: Normalize-------
bmech.normalize()

ensembler(fld=bmech.in_folder, ch=[], conditions=['Straight', 'Turn'])

ensembler.average()
