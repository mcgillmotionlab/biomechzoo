import os
from biomechzoo.biomechzoo import BiomechZoo

# get raw data folder
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# fld_data = os.path.join(project_root, 'data', 'csv', 'opencap')
# fld_data = os.path.join(project_root, 'data', 'csv', 'opencap')
fld_data = "/Users/Werk/Documents/Postdoc-McGill/breast-reduction/data/addevent mcgrath_fs"

#%% set up a new 'bmech' object for processing
bmech = BiomechZoo(fld_data, inplace=True, verbose='all')

#%% Step 1: Conversion to the biomechZoo format -------------------------------------------
# bmech.c3d2zoo(out_folder='visualization c3d')
# bmech.table2zoo(extension='csv')
# bmech.inplace = True

# ---- test visualisation in script----
from biomechzoo.visualization.ensembler import Ensembler

# out_folder = os.path.join(project_root, 'data', 'csv', 'QC')
# Initialize the ensembler class and create the subplot bones
# ensembler = Ensembler(fld=bmech.in_folder, ch=['gy_shank'],
#                       conditions=['post'],
#                       name_contains=["Jogging", ],
#                       out_folder=None
#                       )

subj_pattern = [r"\b\d{3}[A-Z]{2}\b", r"\b\d{3}[A-Z]{3}\b"]
ensembler = Ensembler(fld=bmech.in_folder, ch=["gy_shank"],name_contains=["Jogging"], conditions=["pre", "post"], subj_pattern=subj_pattern)
ensembler.cycles(event_name='mcgrath_fs_1')

# Populate the figure with individual gait cycles and save it to file
# ensembler.cycles()
# ensembler.save(file_name="individual gait cycles")

# Populate the figure with the average and standard deviation per condition.
# ensembler.average()
# ensembler.save(file_name="average gait cycles")
#
#
# # combine pre and post to the same subplot
# ensembler.combine()
# ensembler.save(file_name="combined figure", extension='png')

