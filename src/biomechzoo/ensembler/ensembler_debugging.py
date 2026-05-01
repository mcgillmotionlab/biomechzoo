import os
# import statements
from ensembler import Ensembler
from plot_spec import PlotSpec
# line plot and event renderers
from renderers import IndividualLinesRenderer, MeanSDRenderer, EventOverlayRenderer
from renderers import ViolinRenderer, BlandAltmanRenderer, ScatterRenderer
# combiner renderers
from renderers import CompositeRenderer
from helpers import ConditionSpec, ConditionSource


#%%
# Set up variables.
current_dir = os.getcwd()
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
fld = os.path.join(project_root, 'data', 'sample_study', 'normalized')

spec = ConditionSpec(source = ConditionSource.WITHIN,
                     base_channels = ['RKnee', 'RAnkle'],
                     suffix_map = {'Kinemat_x': 'Kinemat_x',
                                   'Angles_x': 'Angles_x'}
                     )
channels = ['RKnee']
subj_list = [name for name in os.listdir(fld) if os.path.isdir(os.path.join(fld, name))]
rows = 2
cols = 2


lines_and_events = CompositeRenderer(IndividualLinesRenderer(), EventOverlayRenderer())     # within stuff
ens = Ensembler( in_folder=fld, channels=channels, n_rows=rows, n_cols=cols, subj_list=subj_list, condition_spec=spec)
ens.add_subplot(PlotSpec('RKnee', 'Kinemat_x', companions=['Angles_x'], row=1, col=1, renderer=IndividualLinesRenderer(), x_label='% stance', y_label='Joint angle (deg)'))
ens.add_subplot(PlotSpec('RKnee', 'Kinemat_x', companions=['Angles_x'], row=1, col=2, renderer=MeanSDRenderer(), x_label='% stance', y_label='Joint angle (deg)'))
ens.add_subplot(PlotSpec('RAnkle', 'Kinemat_x', companions=['Angles_x'], row=2, col=1, renderer=IndividualLinesRenderer(), x_label='% stance', y_label='Joint angle (deg)'))
ens.add_subplot(PlotSpec('RAnkle', 'Kinemat_x', companions=['Angles_x'], row=2, col=2, renderer=MeanSDRenderer(), x_label='% stance', y_label='Joint angle (deg)'))

fig = ens.build(title='Kinemat vs Plug-in Gait')
fig.show()