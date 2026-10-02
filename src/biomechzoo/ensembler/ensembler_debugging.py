import os
# import statements
from ensembler import Ensembler
from plot_spec import PlotSpec
from data_store import DataStore
# line plot and event renderers
from renderers import IndividualLinesRenderer, MeanSDRenderer, EventOverlayRenderer
from renderers import ViolinRenderer, BlandAltmanRenderer, ScatterRenderer
# combiner renderers
from renderers import CompositeRenderer
from helpers import ConditionSpec, ConditionSource


#%%
current_dir = os.getcwd()
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
fld = os.path.join(project_root, 'data', 'sample_study', 'normalized')
str_match = [r'\bHC\d{3}[A-Z]\b']

channels = ['RightAnklePower']
events = ['max']
rows = 1
cols = 2
events = ['max']
rows = 1
cols = 2
events = ['max']

store = DataStore(fld = fld,  condition_spec= ConditionSpec(source = ConditionSource.BETWEEN, conditions = ['Straight', 'Turn']),  str_match=str_match,)
df = store.to_events_dataframe(channels=channels, event_names=events)
print(df.head())

subset = df.query(f"condition == 'Turn'")
print(subset.head())