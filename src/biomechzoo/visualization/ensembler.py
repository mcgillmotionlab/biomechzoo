import numpy as np
import os
import re
import pandas as pd
import json

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.colors as pc
from dash import Dash, dcc, html, Input, Output, State, no_update

from biomechzoo.utils.engine import engine
from biomechzoo.utils.zload import zload

class Ensembler:
    def __init__(self, fld, ch, conditions, out_folder=None, name_contains=None, show_legend=True, match_all=True, subj_pattern=None):
        if isinstance(subj_pattern,str):
            subj_pattern = [subj_pattern]

        self.fld = fld
        self.conditions = conditions
        self.channels = ch
        self.out_folder = out_folder
        self.show_legend = show_legend
        self.subj_pattern = subj_pattern
        self.zoo_files = engine(fld, extension=".zoo", subfolders=conditions, name_contains=name_contains, match_all=match_all)
        self.fig = self._create_subplots()
        self.subject_colors = self._assign_subject_colors()

    def _assign_subject_colors(self):
        unique_subjects = self._get_unique_subjects()
        subject_colors = {}
        for idx, subj in enumerate(unique_subjects):
            line_color, shade_color, marker_color = self._assign_colors(idx)
            subject_colors[subj] = {
                "line": line_color,
                "shade": shade_color,
                "event": marker_color
            }
        return subject_colors

    def _get_unique_subjects(self):
        # TODO: get an option when subj_pattern is None.
        #  Get from biomechzoo zoosystem?

        subjects = set()
        for fl in self.zoo_files:
            match = re.search(self.subj_pattern[0], fl)
            if match:
                subjects.add(match.group(0))
            elif match is None:
                match = re.search(self.subj_pattern[1], fl)
                if match:
                    subjects.add(match.group(0))
                else:
                    subjects.add("unknown")
        return sorted(subjects)

    def  _assign_colors(self, i):
        hex_code = pc.qualitative.D3[i % len(pc.qualitative.D3)]
        h = hex_code.lstrip('#')
        RGB =tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

        #shade color with opacity
        opacity = 0.3
        shade_color = f"rgba({RGB[0]}, {RGB[1]}, {RGB[2]}, {opacity})"

        #Get complementary color for marker
        comp = ['%02X' % (255 - a) for a in RGB]
        marker_color =  '#' + ''.join(comp)

        return hex_code, shade_color, marker_color


    def _create_subplots(self):
        self.rows = len(self.channels)
        self.cols = len(self.conditions)
        titles = [f"{ch} - {cond}" for ch in self.channels for cond in self.conditions]
        fig = make_subplots(rows=self.rows, cols=self.cols, shared_xaxes=True, shared_yaxes=False,
                             subplot_titles=titles)
        return fig

    def _create_subplots_combine(self):
        self.rows = len(self.channels)
        self.cols = 1
        titles = [f"{ch}" for ch in self.channels ]
        fig = make_subplots(rows=self.rows, cols=self.cols, shared_xaxes=True, shared_yaxes=True,
                            subplot_titles=titles)
        return fig

    def _get_condition_from_path(self, path):
        for cond in self.conditions:
            if cond in path:
                return cond
        return "Unknown"

    def _make_point_customdata(self, subj, channel, condition, fname, row, col, x, y):
        # Ensure x is an array of indices when None
        if x is None:
            x = list(range(len(y)))
        return [
            {
                "subject": subj,
                "channel": channel,
                "condition": condition,
                "source_file": fname,
                "row": row,
                "col": col,
                "index": int(xi) if isinstance(xi, (int, np.integer)) else xi,
                "value": float(yi) if isinstance(yi, (float, np.floating)) else yi
            } for xi, yi in zip(x, y)
        ]

    def _default_hovertemplate(self):
        # Compact, informative hover
        return (
            "Subject: %{customdata.subject}<br>"
            "Channel: %{customdata.channel}<br>"
            "Condition: %{customdata.condition}<br>"
            "File: %{customdata.source_file}<br>"
            "x: %{x}<br>y: %{y}"
            "<extra></extra>"
        )

    def cycles(self, plot_markers=False):
        # check if fig is populated
        if self.fig.data:
            self.fig.data = []

        # loop thought the zoofiles and plot the traces
        for fl in self.zoo_files:
            data = zload(fl)
            fname = os.path.basename(fl)
            condition = self._get_condition_from_path(fl)

            subj_not_found = True
            while subj_not_found:
                for key in self.subject_colors:
                    if key in fl:
                        subj = key
                        subj_not_found = False

            if subj_not_found:
                subj = "Unknown"

            line_color = self.subject_colors[subj]["line"]
            marker_color = self.subject_colors[subj]["event"]

            if not any(t.legendgroup == subj for t in self.fig.data):
                self.add_line(y=[None],name=f"Subject - {subj}", color=line_color,legendgroup=subj, showlegend=True )

            for i, channel in enumerate(self.channels):
                ch_data_line = data[channel]["line"]
                row = i + 1
                col = self.conditions.index(condition) + 1

                # Built metadata for click/hover
                x_line = list(range(len(ch_data_line)))
                cdata = self._make_point_customdata(subj, channel, condition, fname, row, col, x_line, ch_data_line)

                self.add_line(y=ch_data_line, x=x_line, row=row, col=col,
                              name=f"{fname} - {channel}", color=line_color,
                              legendgroup=subj, showlegend=False,
                              customdata=cdata, hovertemplate=self._default_hovertemplate())

                if plot_markers:
                    ch_data_event = data[channel]["event"]
                    for event in ch_data_event:
                        ch_event_data = data[channel]["event"][event]
                        eyd = np.array(ch_event_data[1]) # prep for plotting
                        exd = np.array(ch_event_data[0]) # prep for plotting
                        cdata_m = self._make_point_customdata(subj, channel, condition, fname, row, col, exd.tolist(), eyd.tolist())

                        self.add_marker(y=eyd, x=exd, row=row, col=col,
                                        name=event, color=marker_color,
                                        customdata=cdata_m, hovertemplate=self._default_hovertemplate())

        self.show(title="Cycles per Subject")


    def quality_check_cycles(self):
        # check if fig is populated
        if self.fig.data:
            self.fig.data = []

        # loop thought the zoofiles and plot the traces
        for fl in self.zoo_files:
            data = zload(fl)
            fname = os.path.basename(fl)
            condition = self._get_condition_from_path(fl)

            subj_not_found = True
            while subj_not_found:
                for key in self.subject_colors:
                    if key in fl:
                        subj = key
                        subj_not_found = False

            if subj_not_found:
                subj = "Unknown"

            line_color = self.subject_colors[subj]["line"]
            marker_color = self.subject_colors[subj]["event"]

            if not any(t.legendgroup == subj for t in self.fig.data):
                self.add_line(y=[None], name=f"Subject - {subj}", color=line_color, legendgroup=subj,
                              showlegend=True)

            for i, channel in enumerate(self.channels):
                ch_data_line = data[channel]["line"]
                row = i + 1
                col = self.conditions.index(condition) + 1

                # Built metadata for click/hover
                x_line = list(range(len(ch_data_line)))
                cdata = self._make_point_customdata(subj, channel, condition, fname, row, col, x_line, ch_data_line)

                self.add_line(y=ch_data_line, x=x_line, row=row, col=col,
                              name=f"{fname} - {channel}", color=line_color,
                              legendgroup=subj, showlegend=False,
                              customdata=cdata, hovertemplate=self._default_hovertemplate())

        # self.fig.show()



    def combine(self):
        # check if fig is populated
        if self.fig:
            self.fig.layout = {}
            self.fig.data = []

        # Create new figure object
        self.fig = self._create_subplots_combine()

        data = self._calculate_average()
        for c, condition in enumerate(data):
            line_color, shade_color, marker_color = self._assign_colors(c)

            if not any(t.legendgroup == condition for t in self.fig.data):
                self.add_line(y=[None],name=f"{condition}", color=line_color,legendgroup=condition, showlegend=True )

            for i, channel in enumerate(data[condition]):
                average = data[condition][channel]["average"]
                standard_dev = data[condition][channel]["standard_dev"]

                # populate the figure
                row = i + 1
                self.add_line(y=average, row=row, col=1, name=f"{condition} - {channel}", color=line_color, legendgroup=condition, showlegend=False)
                self.add_errorbar(y=average, yerr=standard_dev, row=row, col=1,
                                  color=shade_color)

        self.show()


    def combine_within(self):
        raise NotImplementedError

    def average(self):
        # check if fig is populated
        if self.fig.data:
            self.fig.data = []

        data = self._calculate_average()
        for c, condition in enumerate(data):
            line_color, shade_color, marker_color = self._assign_colors(c)

            if not any(t.legendgroup == condition for t in self.fig.data):
                self.add_line(y=[None],name=f"{condition}", color=line_color,legendgroup=condition, showlegend=True )

            for i, channel in enumerate(data[condition]):
                average = data[condition][channel]["average"]
                standard_dev = data[condition][channel]["standard_dev"]

                # populate the figure
                row = i + 1
                col = self.conditions.index(condition) + 1
                self.add_line(y=average, row=row, col=col, name=f"{condition} - {channel}", color=line_color, legendgroup=condition, showlegend=False ) # color='#1F77B4')
                self.add_errorbar(y=average, yerr=standard_dev, row=row, col=col, color = shade_color,) #="rgba(31,119,180,0.3)")

        self.show()

    def _calculate_average(self):
        """Calculates the average timeseries for the channels"""
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
        average_dict = {c: {ch: {} for ch in self.channels} for c in self.conditions}
        for c, condition in enumerate(data_new):
            for i, channel in enumerate(data_new[condition]):
                line_data = data_new[condition][channel]
                array_data = np.array(line_data)
                average = np.nanmean(array_data, axis=0)
                standard_dev = np.nanstd(array_data, axis=0)

                average_dict[condition][channel].update({"average": average, "standard_dev": standard_dev})

        return average_dict

    def add_line(self, y, x=None, row=1, col=1, name=None, color=None, legendgroup=None, showlegend=True, customdata=None, hovertemplate=None):
        trace = go.Scatter(x=x, y=y, mode="lines", name=name,
                           line=dict(color=color), showlegend=showlegend, legendgroup=legendgroup,
                           customdata=customdata, hovertemplate=hovertemplate)
        self.fig.add_trace(trace, row=row, col=col)

    def add_marker(self, y, x, row=1, col=1, name=None, color=None, customdata=None, hovertemplate=None):
        trace = go.Scatter(x=x, y=y, mode="markers", name=name, line=dict(color=color),
                           customdata=customdata, hovertemplate=hovertemplate)
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

    def show(self, title=None):
        # Dynamic sizing
        base_height = 350
        base_width = 550
        height = base_height * self.rows
        width = base_width * self.cols

        # Default title if not provided
        if title is None:
            if self.cols == 1:
                title = "Combined Conditions"
            else:
                title = "Conditions by Channel"

        # Update layout
        self.fig.update_layout(
            height=height,
            width=width,
            title=dict(text=title, x=0.5, font=dict(size=24)),
            template="simple_white",
            margin=dict(l=50, r=50, t=50, b=50),
            font=dict(size=18), showlegend=True,
        )

        self.fig.show()

    def save(self, file_name, extension="html", folder=None):
        if folder is None:
            folder = self.fld

        os.makedirs(folder, exist_ok=True)
        if extension == "html":
            self.fig.write_html(os.path.join(folder, f"{file_name}.{extension}"))
        else:
            self.fig.write_image(os.path.join(folder, f"{file_name}.{extension}"))



class EnsemblerQualityChecker:
    def __init__(self, figure, out_folder):
        self.figure = figure
        self.out_folder = out_folder
        self.app = Dash(__name__)
        self._built_layout()
        self._register_callbacks()


    def _built_layout(self):
        self.app.layout = html.Div([
            # The graph
            html.Div([
                dcc.Graph(id="ensemble-graph", figure=self.figure, clear_on_unhover=True),
            ]),
            html.Hr(),
            # click output
            html.Div([
                html.H4("Last click"),
                html.Pre(id="last-click", style={"whiteSpace": "pre-wrap"}),
                html.H4("Clicks captured"),
                html.Pre(id="click-count")
            ]),
            # Download button
            html.Div([
                html.Button("Download CSV", id="btn-download", n_clicks=0),
                dcc.Download(id="download-csv"),
                dcc.Store(id="click-store", data=[])
            ]),
        ])

    def _register_callbacks(self):
        app=self.app

        @app.callback(
            Output("last-click", "children"),
            Output("click-count", "children"),
            Output("click-store", "data"),
            Output("ensemble-graph", "figure"),
            Input("ensemble-graph", "clickData"),
            State("click-store", "data"),
            State("ensemble-graph", "figure"),
            prevent_initial_call=True
        )
        def save_and_remove(clickData, clicks, fig):
            if not clickData or fig is None:
                return no_update, no_update, clicks, no_update

            pt = clickData["points"][0]
            # Ignore helper/legend traces that use y=[None]
            if pt.get("y") is None or pt.get("curveNumber") is None:
                return no_update, no_update, clicks, no_update

            # Build record (flat customdata: [subject, channel, condition, file, row, col, index, value])
            cd = pt.get("customdata") or []
            record = {
                "subject": cd.get("subject"),
                "channel": cd.get("channel"),
                "condition": cd.get("condition"),
                "source_file": cd.get("source_file"),
                "row": cd.get("row"),
                "col": cd.get("col"),
                "index": cd.get("index"),
                "value": cd.get("value"),
                # native plotly info as well
                "curveNumber": pt.get("curveNumber"),
                "pointNumber": pt.get("pointNumber"),
                "x": pt.get("x"),
                "y": pt.get("y"),
            }

            # Append & persist
            clicks = (clicks or []) + [record]
            try:
                out_dir = os.path.join(self.out_folder, "click_exports")
                os.makedirs(out_dir, exist_ok=True)
                # pd.DataFrame(clicks).to_csv(os.path.join(out_dir, "clicks_latest.csv"), index=False)
            except Exception:
                pass  # keep UI responsive even if write fails

            # Remove the clicked trace
            data = list(fig.get("data", []))
            idx = pt["curveNumber"]
            if 0 <= idx < len(data):
                t = data[idx]
                if t.get("type") == "scatter" and t.get("mode") in ("lines", "lines+markers", "markers"):
                    data.pop(idx)
                    fig["data"] = data
                    fig.setdefault("layout", {})["uirevision"] = "ensembler"  # preserve zoom/state

            return json.dumps(record, indent=2), f"Total clicks: {len(clicks)}", clicks, fig

        @app.callback(
            Output("download-csv", "data"),
            Input("btn-download", "n_clicks"),
            State("click-store", "data"),
            prevent_initial_call=True
        )
        def download_csv(n, clicks):
            if not clicks:
                return no_update
            df = pd.DataFrame(clicks)
            # For client-side download
            return dcc.send_data_frame(df.to_csv, "ensembler_clicks.csv", index=False)

    def run(self, **kwargs):
        # Default values if not provided
        kwargs.setdefault("host", "127.0.0.1")
        kwargs.setdefault("port", 8050)
        kwargs.setdefault("debug", True)
        self.app.run(**kwargs)
