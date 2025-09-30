import os
from src.biomechzoo.biomechzoo import BiomechZoo


# get raw data folder
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fld_data = os.path.join(project_root, 'data')


#### Testing conversion functions #############

# mvnx2zoo
fld_data_mvnx = os.path.join(fld_data, 'other')
bmech = BiomechZoo(fld_data_mvnx, verbose='all', inplace=False)
bmech.mvnx2zoo(out_folder='mvnx2zoo')

# c3d2zoo
fld_data_c3d = os.path.join(project_root, 'data', 'sample_study', 'raw c3d files')
bmech = BiomechZoo(fld_data_c3d, verbose='all', inplace=False)
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