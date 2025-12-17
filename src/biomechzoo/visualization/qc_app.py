import os
import json
import pandas as pd
from dash import Dash,dcc, html, Input, Output, State, no_update, callback_context

from biomechzoo.visualization.ensembler import Ensembler

def run_quality_check(fld, ch, out_folder, subj_pattern, conditions=None, name_contains=None, event_name=None):

    if isinstance(ch, str):
        ch = [ch]

    if isinstance(conditions, str):
        conditions = [conditions]

    if isinstance(name_contains, str):
        name_contains = [name_contains]

    ensembler = Ensembler(fld=fld, ch=ch, conditions=conditions, name_contains=name_contains, subj_pattern=subj_pattern)
    ensembler.quality_check_cycles(event_name=event_name)

    # snapshot of base figure
    base_fig = ensembler.fig.to_dict() if hasattr(ensembler.fig, "to_dict") else {
        "data": ensembler.fig.data,
        "layout": ensembler.fig.layout,
    }
    # base_fig.setdefault("layout", {})["uirevision"] = "ensembler"

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

        # ----Controls undo/reset----
        html.Div(
            children=[
                html.Button("Undo last removal", id="btn-undo", n_clicks=0, disabled=True),
                html.Button("Reset figure", id="btn-reset", n_clicks=0),
                dcc.Store(id="undo-stack", data=[]),
                dcc.Store(id="base-figure", data=base_fig),
            ], className="card",
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
                     style={"width": "15%", 'float': 'right'}),
        ], style={'display': 'inline-block', 'vertical-align': 'bottom'}),
        ], className="wrapper"
    )

    @app.callback(
        Output("last-click", "children"),
        Output("click-count", "children"),
        Output("click-store", "data"),
        Output("cycle-graph", "figure"),
        Output("undo-stack", "data"),
        Output("btn-undo", "disabled"),
        Input("cycle-graph", "clickData"),
        Input("btn-undo", "n_clicks"),
        Input("btn-reset", "n_clicks"),
        State("click-store", "data"),
        State("cycle-graph", "figure"),
        State("undo-stack", "data"),
        State("base-figure", "data"),
        prevent_initial_call=True
    )
    def multi_action(clickData, n_undo, n_reset, clicks, fig, undo_stack, base_fig):
        # Default passthroughs
        last_click_msg = no_update
        click_count_msg = no_update
        clicks_out = clicks
        fig_out = fig
        undo_out = undo_stack or []
        undo_disabled_out = len(undo_out) == 0

        # Which input fired?
        ctx = callback_context
        trigger = ctx.triggered[0]["prop_id"] if ctx.triggered else ""

        # ---- RESET ----
        if trigger.startswith("btn-reset.n_clicks"):
            if base_fig:
                fig_out = {
                    "data": base_fig.get("data", []),
                    "layout": base_fig.get("layout", {})
                }
                # fig_out.setdefault("layout", {})["uirevision"] = "ensembler"
                undo_out = []
                undo_disabled_out = True
            return last_click_msg, click_count_msg, clicks_out, fig_out, undo_out, undo_disabled_out

        # ---- UNDO ----
        if trigger.startswith("btn-undo.n_clicks"):
            if undo_out:
                last = undo_out[-1]
                idx = last.get("index")
                trace = last.get("trace")
                click_idx = last.get("click_idx")

                data = list(fig_out.get("data", []))
                insert_at = max(0, min(idx if isinstance(idx, int) else len(data), len(data)))
                data.insert(insert_at, trace)
                fig_out["data"] = data
                fig_out.setdefault("layout", {})["uirevision"] = "ensembler"

                if isinstance(click_idx, int) and 0 <= click_idx < len(clicks_out or []):
                    clicks_out = list(clicks_out)
                    # Choose ONE label and use it consistently:
                    clicks_out[click_idx]["action"] = "reinstated"  # or "restated" if you prefer

                undo_out = undo_out[:-1]

            undo_disabled_out = len(undo_out) == 0
            return last_click_msg, click_count_msg, clicks_out, fig_out, undo_out, undo_disabled_out

        # ---- CLICK-TO-REMOVE ----
        if trigger.startswith("cycle-graph.clickData"):
            if not clickData or fig_out is None:
                return last_click_msg, click_count_msg, clicks_out, no_update, undo_out, undo_disabled_out

            pt = clickData["points"][0]
            if pt.get("y") is None or pt.get("curveNumber") is None:
                return last_click_msg, click_count_msg, clicks_out, no_update, undo_out, undo_disabled_out

            cd = pt.get("customdata") or {}

            def _get(k, default=None):
                if isinstance(cd, dict):
                    return cd.get(k, default)
                if isinstance(cd, list) and cd and isinstance(cd[0], dict):
                    return cd[0].get(k, default)
                return default

            record = {
                "subject": _get("subject"),
                "channel": _get("channel"),
                "condition": _get("condition"),
                "source_file": _get("source_file"),
                "row": _get("row"),
                "col": _get("col"),
                "index": _get("index"),
                "value": _get("value"),
                "curveNumber": pt.get("curveNumber"),
                "pointNumber": pt.get("pointNumber"),
                "x": pt.get("x"),
                "y": pt.get("y"),
                "action": "remove"
            }

            clicks_out = (clicks_out or []) + [record]
            click_idx = len(clicks_out) - 1  # index of the removal record in click-store

            try:
                out_dir = os.path.join(out_folder, "click_exports")
                os.makedirs(out_dir, exist_ok=True)
                # pd.DataFrame(clicks_out).to_csv(os.path.join(out_dir, "clicks_latest.csv"), index=False)
            except Exception:
                pass

            data = list(fig_out.get("data", []))
            idx = pt["curveNumber"]
            if 0 <= idx < len(data):
                removed_trace = data.pop(idx)
                fig_out["data"] = data
                fig_out.setdefault("layout", {})["uirevision"] = "ensembler"
                undo_out = (undo_out or []) + [{"index": idx, "trace": removed_trace, "click_idx": click_idx}]
                undo_disabled_out = False

            last_click_msg = json.dumps(record, indent=2)
            click_count_msg = f"Total clicks: {len(clicks_out)}"

            return last_click_msg, click_count_msg, clicks_out, fig_out, undo_out, undo_disabled_out

        # Fallback: nothing recognized
        return last_click_msg, click_count_msg, clicks_out, fig_out, undo_out, undo_disabled_out

    # def save_and_remove(clickData, clicks, fig, undo_stack):
    #     if not clickData or fig is None:
    #         return no_update, no_update, clicks, no_update, no_update, no_update
    #
    #     pt = clickData["points"][0]
    #     # Ignore helper/legend traces that use y=[None]
    #     if pt.get("y") is None or pt.get("curveNumber") is None:
    #         return no_update, no_update, clicks, no_update, no_update, no_update
    #
    #     # Build record (flat customdata: [subject, channel, condition, file, row, col, index, value])
    #     cd = pt.get("customdata") or []
    #     record = {
    #         "subject": cd.get("subject"),
    #         "channel": cd.get("channel"),
    #         "condition": cd.get("condition"),
    #         "source_file": cd.get("source_file"),
    #         "row": cd.get("row"),
    #         "col": cd.get("col"),
    #         "index": cd.get("index"),
    #         "value": cd.get("value"),
    #         # native plotly info as well
    #         "curveNumber": pt.get("curveNumber"),
    #         "pointNumber": pt.get("pointNumber"),
    #         "x": pt.get("x"),
    #         "y": pt.get("y"),
    #     }
    #
    #     # Append & persist
    #     clicks = (clicks or []) + [record]
    #     try:
    #         out_dir = os.path.join(out_folder, "click_exports")
    #         os.makedirs(out_dir, exist_ok=True)
    #         # pd.DataFrame(clicks).to_csv(os.path.join(out_dir, "clicks_latest.csv"), index=False)
    #     except Exception:
    #         pass  # keep UI responsive even if write fails
    #
    #     # Remove the clicked trace and push to undo stack
    #     data = list(fig.get("data", []))
    #     idx = pt["curveNumber"]
    #     if 0 <= idx < len(data):
    #         removed_trace = data[idx]
    #         fig["data"] = data
    #         fig.setdefault("layout", {})["uirevision"] = "ensembler"
    #
    #         undo_stack = (undo_stack or []) + [{
    #             "index": idx,
    #             "trace": removed_trace
    #         }]
    #
    #     # enable undo if undo-stack is not empty
    #     undo_disabled = len(undo_stack or []) == 0
    #
    #
    #     return json.dumps(record, indent=2), f"Total clicks: {len(clicks)}", clicks, fig, undo_stack


    @app.callback(
        Output("download-csv", "data"),
        Input("btn-download", "n_clicks"),
        State("click-store", "data"),
        prevent_initial_call=True
    )
    def download_csv(n, clicks_out):
        if not n or not clicks_out:
            return no_update

        removed = [
            r for r in (clicks_out or [])
            if r.get("action") == "remove" and not r.get("undone", False)
        ]

        if not removed:
            return no_update
        df = pd.DataFrame(removed)
        # For client-side download
        return dcc.send_data_frame(df.to_csv, "removed_cycles.csv", index=False)

    app.run(debug=True)




