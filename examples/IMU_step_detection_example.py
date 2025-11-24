import os
from biomechzoo.biomechzoo import BiomechZoo

# get raw data folder
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fld_data = os.path.join(project_root, 'data', 'imu', 'movement-onset')


#%% set up a new 'bmech' object for processing
bmech = BiomechZoo(fld_data, inplace=True, verbose='all')

#%% IMU step detection
bmech.addevent(ch="gy_shank", event_type="mcgrath_fs", event_name="FS")

bmech.split_trial_by_gait_cycle("FS_1")