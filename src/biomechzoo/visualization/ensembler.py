import numpy as np
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.colors as pc


from biomechzoo.utils.engine import engine
from biomechzoo.utils.zload import zload


class Ensembler:
    def __init__(self, fld, ch, conditions):
        self.fld = fld
        self.conditions = conditions
        self.channels = ch
        self.zoo_files = engine(fld, extension=".zoo", subfolders=conditions)
        self.fig = self._create_subplots()

    def _assign_colors(self):
        NotImplementedError()


    def _create_subplots(self):
        rows = len(self.channels)
        cols = len(self.conditions)
        titles = [f"{ch} - {cond}" for ch in self.channels for cond in self.conditions]
        fig = make_subplots(rows=rows, cols=cols, shared_xaxes=True, shared_yaxes=True,
                             subplot_titles=titles)
        return fig

    def _get_condition_from_path(self, path):
        for cond in self.conditions:
            if cond in path:
                return cond
        return "Unknown"

    def cycles(self):
        for fl in self.zoo_files:
            data = zload(fl)
            fname = os.path.basename(fl)
            condition = self._get_condition_from_path(fl)

            for i, channel in enumerate(self.channels):
                ch_data_line = data[channel]["line"]
                row = i + 1
                col = self.conditions.index(condition) + 1
                self.add_line(y=ch_data_line, row=row, col=col, name=f"{fname} - {channel}")

        self.show()


    def average(self):
        # Initialize dictionary to store data
        data_new = {c: {ch: [] for ch in self.channels} for c in self.conditions}

        for fl in self.zoo_files:
            data = zload(fl)
            condition = self._get_condition_from_path(fl)

            # Create dataframe from the two conditions.
            for channel in self.channels:
                try:
                    ch_data_line = data[channel]["line"]
                    data_new[condition][channel].append(ch_data_line)
                except KeyError:
                    print(f"Channel {channel} not found in file {fl}")

        # Average per condition per channel
        for condition in data_new:
            for i, channel in enumerate(data_new[condition]):
                line_data = data_new[condition][channel]
                array_data = np.array(line_data)
                average = np.nanmean(array_data, axis=0)
                standard_dev = np.nanstd(array_data, axis=0)

                # populate the figure
                row = i + 1
                col = self.conditions.index(condition) + 1
                self.add_line(y=average, row=row, col=col, name=f"{condition} - {channel}", color='#1F77B4')
                self.add_errorbar(y=average, yerr=standard_dev, row=row, col=col, color="rgba(31,119,180,0.3)")

        self.show()



    def add_line(self, y, x=None, row=1, col=1, name=None, color=None):
        trace = go.Scatter(x=x, y=y, mode="lines", name=name, line=dict(color=color))
        self.fig.add_trace(trace, row=row, col=col)


    def add_errorbar(self, y, yerr, row=1, col=1, color=None):
        upper_bound = y + yerr
        lower_bound = y - yerr

        trace_lower = go.Scatter(y=lower_bound,
                                 line=dict(color='rgba(0,0,0,0)'),
                                 showlegend=False,
                                 )

        trace_upper = go.Scatter(y=upper_bound,
                           fill="tonexty",
                           fillcolor=color,
                           line=dict(color='rgba(0,0,0,0)'),
                           showlegend=False)

        self.fig.add_trace(trace_lower, row=row, col=col)
        self.fig.add_trace(trace_upper, row=row, col=col)

    def show(self):
        self.fig.update_layout(height=300 * len(self.channels), width=400 * len(self.conditions),
                               template="simple_white",)
        self.fig.show()