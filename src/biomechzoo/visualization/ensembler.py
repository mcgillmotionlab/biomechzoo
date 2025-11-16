import numpy as np
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.colors as pc


from biomechzoo.utils.engine import engine
from biomechzoo.utils.zload import zload


class Ensembler:
    def __init__(self, fld, ch, conditions, name_contains=None, side=None, show_legend=False):
        self.fld = fld
        self.conditions = conditions
        self.channels = ch
        self.show_legend = show_legend
        self.zoo_files = engine(fld, extension=".zoo", subfolders=conditions, name_contains=name_contains)
        self.fig = self._create_subplots()
        if side is not None:
            self.side = side
            self._filter_side_from_path()

    def _assign_subject_colors(self):
        NotImplementedError()


    def  _assign_colors(self, i):
        hex_code = pc.qualitative.D3[i]
        h = hex_code.lstrip('#')
        RGB =tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
        opacity = (0.3,)
        rgba = RGB + opacity

        line_color = hex_code
        shade_color = f"rgba{rgba}"

        return line_color, shade_color


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


    def _filter_side_from_path(self):
        self.zoo_files = [zoo_file for zoo_file in self.zoo_files if self.side in zoo_file]


    def cycles(self):
        # check if fig is populated
        if self.fig.data:
            self.fig.data = []

        # loop thought the zoofiles and plot the traces
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

    def combine(self):
        raise NotImplementedError

    def combine_within(self):
        raise NotImplementedError

    def average(self):
        # check if fig is populated
        if self.fig.data:
            self.fig.data = []

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

        for c, condition in enumerate(data_new):
            line_color, shade_color = self._assign_colors(c)
            for i, channel in enumerate(data_new[condition]):
                line_data = data_new[condition][channel]
                array_data = np.array(line_data)
                average = np.nanmean(array_data, axis=0)
                standard_dev = np.nanstd(array_data, axis=0)

                # populate the figure
                row = i + 1
                col = self.conditions.index(condition) + 1
                self.add_line(y=average, row=row, col=col, name=f"{condition} - {channel}", color=line_color) # color='#1F77B4')
                self.add_errorbar(y=average, yerr=standard_dev, row=row, col=col, color = shade_color) #="rgba(31,119,180,0.3)")

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
        self.fig.update_layout(height=350 * len(self.channels), width=450 * len(self.conditions),
                               template="simple_white",
                               showlegend=self.show_legend)
        self.fig.show()

    def save(self, file_name, extension="html", folder=None):
        if folder is None:
            folder = self.fld

        os.makedirs(folder, exist_ok=True)
        if extension == "html":
            self.fig.write_html(os.path.join(folder, f"{file_name}.{extension}"))
        else:
            self.fig.write_image(os.path.join(folder, f"{file_name}.{extension}"))