from plotly.subplots import make_subplots
import numpy as np


def _create_subplots(ens, nrows, ncols, ):
    """
    Creates the subplot for the ensembler class.

    Parameters
    ----------
    ens: Class
        Ensembler class
    nrows : int
        Number of rows
    ncols : int
        Number of columns

    """

    if nrows is None:
        nrows = len(ens.channels)
    if ncols is None:
        ncols = len(ens.conditions)

    titles = [f"{ch} - {cond}" for ch in ens.channels for cond in ens.conditions]
    fig = make_subplots(rows=nrows, cols=ncols, shared_xaxes=True, shared_yaxes=False,
                        subplot_titles=titles)
    return fig


def make_point_customdata(subj, channel, condition, fname, row, col, x, y):
    """Curate data for the hover functionality in plotly figure

    Parameters
    ----------
    subj : str
    channel: str
    condition : str
    fname : str
    row : str
    col : str
    x : list of int
    y : list of float

    Returns
    -------
    custom_template :  list[dict[str, str | int | float | Any]] | list[dict[str, str | int | list[int] | float | array.pyi]]
    """
    # Ensure x is an array of indices when None
    if x is None:
        x = list(range(len(y)))

    if isinstance(y, float):
        custom_template = [
            {
                "subject": subj,
                "channel": channel,
                "condition": condition,
                "source_file": fname,
                "row": row,
                "col": col,
                "index": int(x) if isinstance(x, (int, np.integer)) else x,
                "value": float(y) if isinstance(y, (float, np.floating)) else y
            }
        ]
        return custom_template

    custom_template =  [
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
    return custom_template

def default_hovertemplate(self):
    """Curate default hover template"""
    # Compact, informative hover
    return (
        "Subject: %{customdata.subject}<br>"
        "Channel: %{customdata.channel}<br>"
        "Condition: %{customdata.condition}<br>"
        "File: %{customdata.source_file}<br>"
        "x: %{x}<br>y: %{y}"
        "<extra></extra>"
    )