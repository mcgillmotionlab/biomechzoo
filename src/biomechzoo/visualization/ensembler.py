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

    def plot_lines(self):
        for fl in self.zoo_files:
            data = zload(fl)
            fname = os.path.basename(fl)
            condition = self._get_condition_from_path(fl)

            for i, channel in enumerate(self.channels):
                ch_data_line = data[channel]["line"]
                row = i + 1
                col = self.conditions.index(condition) + 1
                self.add_line(y=ch_data_line, row=row, col=col, name=f"{fname} - {channel}")

        # show plot after all
        self.show()

    def average(self):
        #Initialize dictionary to store data
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





    def add_line(self, y, x=None, row=1, col=1, name=None, color=None):
        trace = go.Scatter(x=x, y=y, mode="lines", name=name, line=dict(color=color))
        self.fig.add_trace(trace, row=row, col=col)


    def show(self):
        self.fig.update_layout(height=500 * len(self.channels), width=700 * len(self.conditions),
                               template="simple_white",)
        self.fig.show()