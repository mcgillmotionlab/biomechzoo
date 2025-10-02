import os
from biomechzoo.biomechzoo import BiomechZoo

# get raw data folder
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fld_data = os.path.join(project_root, 'data')


#### Testing conversion functions #############

# parquet2zoo for all files in fld_data_parquet containing the word Subject in the file name
# fld_data_parquet = os.path.join(fld_data, 'other')
# bmech = BiomechZoo(fld_data_parquet, inplace=False, verbose='all', name_contains='Subject')
# bmech.parquet2zoo(out_folder='parquet2zoo')


# csv2zoo for opencap for all subfolders called opencap_csv within fld_data_csv (only 1 file should process)
fld_data_csv = os.path.join(fld_data, 'other')
bmech = BiomechZoo(fld_data_csv, inplace=False, verbose='all', subfolders='opencap_csv')
bmech.csv2zoo(out_folder='csv2zoo', skip_rows=10)  # this csv has 10 header rows

# mvnx2zoo
fld_data_mvnx = os.path.join(fld_data, 'other')
bmech = BiomechZoo(fld_data_mvnx, inplace=False, verbose='all')
bmech.mvnx2zoo(out_folder='mvnx2zoo')

# c3d2zoo
fld_data_c3d = os.path.join(project_root, 'data', 'sample_study', 'raw c3d files')
bmech = BiomechZoo(fld_data_c3d, inplace=False, verbose='all')
bmech.c3d2zoo(out_folder='c3d2zoo')


# get raw data folder
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fld_raw_data = os.path.join(project_root, 'data', 'sample_study', 'raw c3d files')



# step 2: cleaning
ch = ['RHipAngles', 'RKneeAngles', 'RAnkleAngles', 'SACR']
bmech.removechannel(ch, mode='keep', out_folder='removechannel')
#
# step 3: explode channels
bmech.explodechannel(out_folder='explodechannels')

# rename events
bmech.renameevent(evt='Right_FootStrike1', nevt='RFS1', out_folder='rename event')

# normalize data
bmech.normalize(nlen=101, out_folder='normalize')


# Commented methods not yet tested

# Split trials by gait cycle
# bmech.split_trial_by_gait_cycle(first_event_name='Right_FootStrike1', out_folder='4-split_by_cycle')
#
# # step 4: add Right foot strike event
# bmech.addevent(out_folder='4-addevent')
#
# # step 5 filter data
# bmech.filter(out_folder='5-filter')
#
# # step 6: partition from right foot strike 1 to right foot strike 2
# bmech.partition(out_folder='6-partition')
#
#