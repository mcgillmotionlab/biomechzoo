import os
from biomechzoo.biomechzoo import BiomechZoo
# get raw data folder
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fld_data = os.path.join(project_root, 'data', 'sample_study', 'raw c3d files')

#### Testing processing functions (assumes c3d files converted above ) #############

# set up a new 'bmech' object for processing
bmech = BiomechZoo(fld_data, inplace=False, verbose='all')

# Step 1: Conversion to the biomechZoo format -------------------------------------------
#
bmech.c3d2zoo(out_folder='1-c3d2zoo')


# STEP 2: Cleaning the data -------------------------------------------------------------
#
# - removes channels (not used in current study)
ch = ['LFHD','LBHD','RFHD','RBHD','C7','T10','T12','RBAK','CLAV','STRN',
      'LSHO','LELB','LWRA','LWRB','LFIN','RSHO','RELB','RWRA','RWRB',
      'RFIN','SACR','RASI','LASI','LTHI','LTIB','LKNE','LANK','LHEE',
      'LTOE','RTHI','RTIB','RKNE','RANK','RHEE','RTOE',
      'LHeadAngles','RHeadAngles','LThoraxAngles','RThoraxAngles',
      'LPelvisAngles','LHipAngles','LKneeAngles','LAnkleAngles',
      'RPelvisAngles','RHipAngles','RKneeAngles','RAnkleAngles',
      'LHipForce','LKneeForce','LAnkleForce','LHipMoment','LKneeMoment',
      'LAnkleMoment','LHipPower','LKneePower','LAnklePower','RHipForce',
      'RKneeForce','RAnkleForce','RHipMoment','RKneeMoment',
      'RAnkleMoment','RHipPower','RKneePower','RAnklePower',
      'LGroundReactionForce','LGroundReactionMoment',
      'RGroundReactionForce','RGroundReactionMoment',
      'ForceFx1','ForceFy1','ForceFz1','MomentMx1','MomentMy1',
      'MomentMz1','ForceFx2','ForceFy2','ForceFz2','MomentMx2',
      'MomentMy2','MomentMz2']
bmech.removechannel(ch, mode='keep', out_folder='2-removechannel')


# STEP 3: Processing force plate data ---------------------------------------------------
#  todo: update this based on matlab version and existing toolboxes
# - In this step, filtering and downsampling of raw force plate data is performed
# - Data are also mass normalized, renamed, and coordinate transformed in order to
#   prepare ground reaction force (GRF) data for use in other processes
# - These processes attempt to replicate the steps performed by the Vicon modeller
# bmech.processGRF
bmech.in_folder = fld_data.replace('raw c3d files', '3-processs fpdata')    # this folder was created in Matlab

# % Step 4: Partitioning the data ---------------------------------------------------------
#
# - This step limits the analysis to a single stance phase for the right limb
# - Data are partitionned based on right limb force plate hits
# - The subfolder 'sfld' will be ignored (i.e., not partitioned, because static data do
#   not contain gait data and do not need to be partitionned)
#

sfld  = 'Static'    # no partition
evtn1 = 'RFS'       # start name
evtn2 = 'RFO'       # end name
evtt1 = 'FS_FP'     # start type
evtt2 = 'FO_FP'     # end type
ch    = 'RightGroundReactionForce'  # event ch

bmech.subfolders = ['Straight', 'Turn']      # there are no events in the static folders

bmech.addevent(ch,evtn1,evtt1, out_folder='4-partition')     # Find FS & FO
bmech.addevent(ch,evtn2,evtt2, out_folder='4-partition')     # based on Fz

bmech.partition(evtn1,evtn2, out_folder='4-partition')


# explode channels
bmech.explodechannel(out_folder='explodechannels')

# rename events
bmech.renameevent(evt='Right_FootStrike1', nevt='RFS1', out_folder='rename event')
bmech.renameevent(evt='Right_FootStrike2', nevt='RFS2', out_folder='rename event')

evts = ['RFS1' , 'RFS2', 'bob']
bmech.removeevent(evts, mode='keep', out_folder='removeevent')

# filter data
filt = {
    'order': 4,
    'ftype': 'butter',
    'cutoff': 10,
    'btype': 'lowpass',
    'filtfilt': True}
bmech.filter(out_folder='filter', ch='RKneeAngles_x', filt=filt)

# normalize data
bmech.normalize(nlen=101, out_folder='normalize')

# partition from right foot strike 1 to right foot strike 2
bmech.name_contains = ['Straight', 'Turn']  # do not partition static trials
bmech.partition(out_folder='partition', evt_start='RFS1', evt_end='RFS2')



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