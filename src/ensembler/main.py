# import statements
from ensembler.ensembler import Ensembler
from ensembler.plot_spec import PlotSpec
from ensembler.renderers import IndividualLinesRenderer, MeanSDRenderer
from ensembler.helpers import ConditionSpec, ConditionSource

#%% Set paths:
fld = "/Users/Werk/Documents/Postdoc-McGill/areve-mcgill/data/Phase2/17-Stats"

#%% Set up ConditionSpec.
spec = ConditionSpec(
    source     = ConditionSource.CHANNEL,
    conditions = ["vicon", "areve"],
    channel_map = {
        "vicon": "RS_abduction_vicon",
        "areve": "RS_abduction_areve",
    }
)

# Set ensembler specs.
channels = ['RS_abduction']
str_match = [r"\b\d{3}[A-Z]{2}\b", r"\b\d{3}[A-Z]{3}\b"]
events = ["max"]
rows = 1
cols = 2

# Create the figure
fig = (
    Ensembler(in_folder=fld, channels=channels, n_rows = rows,  n_cols =cols, str_match=str_match, condition_spec=spec)
    .add_subplot(PlotSpec(channel='RS_abduction', condition="areve", companions=["vicon"],
                          row=1, col=1, renderer=IndividualLinesRenderer(), events=events,
                          x_label="% of movement", y_label="Joint angle (deg)"))

    .add_subplot(PlotSpec(channel='RS_abduction', condition="areve", companions=["vicon"],
                          row=1, col=2, renderer=MeanSDRenderer(), events=events,
                          x_label="% of movement", y_label="Joint angle (deg)"))

    .build(title="Shoulder abduction - AReve vs Vicon vs Plug-in Gait")
)

# add annotations
fig.add_annotation(x=80, y=80, showarrow=False,
            text="RMSE: 8.28 deg",
            yshift=10, font=dict(size=12), row=1,col=2)

fig.show()