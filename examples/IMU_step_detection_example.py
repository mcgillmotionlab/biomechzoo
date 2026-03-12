import os
from biomechzoo.biomechzoo import BiomechZoo
from biomechzoo.visualization.ensembler import Ensembler

# get raw data folder
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fld_data = os.path.join(project_root, 'data', 'imu', 'movement-onset')


#%% set up a new 'bmech' object for processing
bmech = BiomechZoo(fld_data, inplace=True, verbose='all')

#%% IMU step detection
bmech.addevent(ch="gy_shank", event_type="mcgrath_fs", event_name="FS")

bmech.split_trial_by_gait_cycle(first_event_name="FS_1", out_folder="split_trial_by_gait_event", inplace=False)

#%% Normalize
bmech.normalize(out_folder="normalized")

#%% Plot
subject_pattern = [r"\b\d{3}[A-Z]{2}\b", r"\b\d{3}[A-Z]{3}\b"]

ensembler = Ensembler(fld=bmech.in_folder, ch=["gy_shank"],name_contains=["Jogging", "002"], conditions=["pre"], subject_pattern=subject_pattern)
ensembler.cycles()

ensembler.save("cycles")
