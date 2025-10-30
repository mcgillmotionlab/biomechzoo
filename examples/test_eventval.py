""" demonstrate usage of eventval to extract event data from zoo files"""

import os
from biomechzoo.biomechzoo import BiomechZoo
from biomechzoo.statistics.eventval import eventval

# get raw data folder
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fld_data = os.path.join(project_root, 'data', 'sample_study', 'raw c3d files')

# initialize biomechzoo object
bmech = BiomechZoo(fld_data, inplace=False, verbose='all')

# do some basic processing to showcase eventval functionality
bmech.c3d2zoo(out_folder='processing_for_eventval') # Conversion to the biomechZoo format
bmech.inplace = True                                # keep writing to same folder
bmech.removechannel(ch=['RHipAngles','RKneeAngles','RAnkleAngles'], mode='keep')
bmech.explodechannel()
bmech.addevent(ch='RHipAngles_x', event_type='max', event_name='max')     # Find FS & FO
bmech.addevent(ch='RKneeAngles_x', event_type='min', event_name='min')     # Find FS & FO
bmech.addevent(ch='RKneeAngles_x', event_type='first', event_name='first', constant=2)     # Find FS & FO

# run eventval
dim1 = ['Straight', 'Turn']
dim2 = ['HC002D', 'HC030A', 'HC033A', 'HC040A']
local_events = ['max', 'min']
global_events = ['first']
ch = ['RHipAngles_x', 'RKneeAngles_x', 'RAnkleAngles_x', 'bad channel']
df = eventval(fld=bmech.in_folder,
              dim1=dim1,
              dim2=dim2,
              ch=ch,
              localevts=local_events,
              globalevts=global_events)

a = 1

