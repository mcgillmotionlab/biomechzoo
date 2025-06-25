import os
import shutil
import biomechzoo as bmech
from biomechzoo.utils.copy_files import copy_files
from biomechzoo.engine import engine
from biomechzoo.utils.zload import zload


# Here we demonstrate capabilities of the biomechzoo python
# implementation using the sample study data

# step 0: get root folder of the sample study
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
fld0 = os.path.join(project_root, 'biomechzoo', 'biomechzoo', 'data', 'sample_study', 'raw c3d files')

# step 1: convert c3d files to zoo format (mat files saved with the
# extension '.zoo' and compatible with Matlab)
fld1 = fld0.replace('raw c3d files', '1-c3d2zoo')
shutil.copytree(fld0, fld1, dirs_exist_ok=True)
copy_files(fld0, fld1)
bmech.conversion.c3d2zoo(fld1)

# Step 2: remove uncessary channels
ch = {'LFHD', 'LBHD', 'RFHD', 'RBHD', 'C7', 'T10', 'T12', 'RBAK', 'CLAV', 'STRN', ... % PiG markers
      'LSHO', 'LELB', 'LWRA', 'LWRB', 'LFIN', 'RSHO', 'RELB', 'RWRA', 'RWRB', ...
      'RFIN', 'SACR', 'RASI', 'LASI', 'LTHI', 'LTIB', 'LKNE', 'LANK', 'LHEE', ...
      'LTOE', 'RTHI', 'RTIB', 'RKNE', 'RANK', 'RHEE', 'RTOE', ...
      'LHeadAngles', 'RHeadAngles', 'LThoraxAngles', 'RThoraxAngles', ...
      'LPelvisAngles', 'LHipAngles', 'LKneeAngles', 'LAnkleAngles', ... % PiG kinemat
      'RPelvisAngles', 'RHipAngles', 'RKneeAngles', 'RAnkleAngles', ...
      'LHipForce', 'LKneeForce', 'LAnkleForce', 'LHipMoment', 'LKneeMoment', ... % PiG kinetics
      'LAnkleMoment', 'LHipPower', 'LKneePower', 'LAnklePower', 'RHipForce', ...
      'RKneeForce', 'RAnkleForce', 'RHipMoment', 'RKneeMoment', ...
      'RAnkleMoment', 'RHipPower', 'RKneePower', 'RAnklePower', ...
      'LGroundReactionForce', 'LGroundReactionMoment', ... % PiG proc GRF
      'RGroundReactionForce', 'RGroundReactionMoment', ...
      'ForceFx1', 'ForceFy1', 'ForceFz1', 'MomentMx1', 'MomentMy1', ... % raw GRF
      'MomentMz1', 'ForceFx2', 'ForceFy2', 'ForceFz2', 'MomentMx2', ...
      'MomentMy2', 'MomentMz2'};

# bmech_removechannel(fld, ch, 'keep')