import os
from biomechzoo.biomechzoo import BiomechZoo
from biomechzoo.utils.zplot import zplot
from biomechzoo.utils.zload import zload
from biomechzoo.utils.engine import engine

# get raw data folder
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fld_data = os.path.join(project_root, 'data', 'sample_study', 'raw c3d files')

#### test the processing methods using sample study c3d files  #############


# set up a new 'bmech' object for processing, ignoring the static trials
bmech = BiomechZoo(fld_data, inplace=False, verbose='all', name_contains= ['Straight'])

# Conversion to the biomechZoo format -------------------------------------------
bmech.c3d2zoo(out_folder='c3d2zoo')

# remove channels
ch_keep = ['SACR','RHipAngles','RKneeAngles','RAnkleAngles', 'RGroundReactionForce']
ch_remove = ['RHipAngles']
bmech.removechannel(ch_keep, mode='keep', out_folder='removechannel')
bmech.removechannel(ch_remove, mode='remove', out_folder='removechannel')

# explode channels
bmech.explodechannel(out_folder='explodechannels')

# add events
evtn1 = 'RFS'       # start name
evtn2 = 'RFO'       # end name
evtt1 = 'FS_FP'     # start type
evtt2 = 'FO_FP'     # end type
ch    = 'RGroundReactionForce_x'  # event ch
bmech.addevent(ch,evtn1,evtt1, out_folder='addevent')     # Find FS & FO
bmech.addevent(ch,evtn2,evtt2, out_folder='addevent')     # based on Fz
bmech.addevent(ch,'max', 'max', out_folder='addevent')
bmech.addevent(ch, 'min', 'min', out_folder='addevent')

# rename events
bmech.renameevent(evt='RFS', nevt='R_FS', out_folder='renameevent')
bmech.renameevent(evt='RFO', nevt='R_FO', out_folder='renameevent')

# remove events
evts = ['max' , 'min', 'bob']
bmech.removeevent(evts, mode='remove', out_folder='removeevent')

# filter data
filt = {
    'order': 4,
    'ftype': 'butter',
    'cutoff': 10,
    'btype': 'lowpass',
    'filtfilt': True}
bmech.filter(ch='RKneeAngles_x', filt=filt, out_folder='filter')

# partition to right stance phase
bmech.partition('R_FS','R_FO', out_folder='partition')

# normalize data
bmech.normalize(nlen=101, out_folder='normalize')


# Commented methods not yet tested

# Split trials by gait cycle
# bmech.split_trial_by_gait_cycle(first_event_name='Right_FootStrike1', out_folder='4-split_by_cycle')

