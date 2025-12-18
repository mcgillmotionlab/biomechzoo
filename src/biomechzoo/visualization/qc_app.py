import os
import json
import pandas as pd
from dash import Dash,dcc, html, Input, Output, State, no_update

from biomechzoo.visualization.ensembler import Ensembler

def run_quality_check(fld, ch, out_folder, subj_pattern, conditions=None, name_contains=None, ):

    if isinstance(ch, str):
        ch = [ch]

    if isinstance(conditions, str):
        conditions = [conditions]

    if isinstance(name_contains, str):
        name_contains = [name_contains]

    ensembler = Ensembler(fld=fld, ch=ch, conditions=conditions, name_contains=name_contains, subj_pattern=subj_pattern)
    ensembler.quality_check_cycles()

    external_stylesheets = [
        {"href": ("https://fonts.googleapis.com/css2?"
                  "family=Lato:wght@400;700&display=swap"),
         "rel": "stylesheet", }
    ]

    app = Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = html.Div(children=[
        # ---- Header----
        html.Div(
            children=[
                html.H2(children="Quality check", className="header-title"),
                html.P(children='''
                Click on the lines that are wrongfully segmented to remove, 
                and press download to save the csv file for removed cycles
                ''', className="header-description"),
                    ],className="header",
                ),
        # ----Layout of the figure----
        html.Div(
            children=
                dcc.Graph(id='cycle-graph',
                    figure={"data": ensembler.fig.data,
                            "layout":{"title": {"text": f"{ch[0]}", "x": 0.05, "xanchor": "left"},
                                      }
                            },
                          ), className="card",
            style={'width': '60%', 'float': 'right', 'display': 'inline-block',},

        ),
        # ----Click functionality----
        html.Div(children=[
            html.H4("Last click"),
            html.Pre(id="last-click"),
            html.H4("Clicks captured"),
            html.Pre(id="click-count"),
        ]),
        # ----Download button----
        html.Div([
            html.Button("Download CSV", id="btn-download", n_clicks=0),
            dcc.Download(id="download-csv"),
            dcc.Store(id="click-store", data=[])

        ]),
        html.Div([
            html.Img(src=app.get_asset_url("(Preferred) - Red on white logo (1).png"), alt="The official McGill logo",
                     style={"width": "20%", 'float': 'right'}),
        ], style={'display': 'inline-block', 'vertical-align': 'bottom'}),
        ], className="wrapper"
    )

    @app.callback(
        Output("last-click", "children"),
        Output("click-count", "children"),
        Output("click-store", "data"),
        Output("cycle-graph", "figure"),
        Input("cycle-graph", "clickData"),
        State("click-store", "data"),
        State("cycle-graph", "figure"),
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
            out_dir = os.path.join(out_folder, "click_exports")
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

    app.run(debug=True)




