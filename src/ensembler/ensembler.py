from plotly.subplots import make_subplots

from src.data_store import DataStore
from src.helpers import ConditionSpec
from src.plot_spec import PlotSpec
from src.style_content import StyleContext
import plotly.graph_objs as go



class Ensembler:

    def __init__(self,
                 in_folder: str,
                 channels: list[str],
                 n_rows: int,
                 n_cols: int,
                 condition_spec: ConditionSpec | None = None,
                 subj_list: list[str] | None = None,
                 str_match: list[str] | None = None,
                 events: list[str] = None,):

        self.store = DataStore(fld=in_folder, condition_spec=condition_spec, events=events, subj_list=subj_list, str_match=str_match)
        self.style = StyleContext(self.store.subjects, self.store.conditions)
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.channels = channels
        self.specs: list[PlotSpec] = []

    def add_subplot(self, spec: PlotSpec):
        self.specs.append(spec)
        return self

    def build(self, title: str = "Ensembler", height: int = 400, width: int = 500) -> go.Figure:
        subplot_titles = [""] * (self.n_rows * self.n_cols)
        for s in self.specs:
            subplot_titles[(s.row - 1) * self.n_cols + (s.col - 1)] = s.title

        fig = make_subplots(
            rows=self.n_rows, cols=self.n_cols,
            subplot_titles=subplot_titles,
            vertical_spacing=0.12,
            horizontal_spacing=0.08,
            shared_xaxes=False,
            shared_yaxes=False,
        )

        for spec in self.specs:
            spec.renderer.render(
                fig, self.store, self.style,
                spec,spec.row, spec.col
            )
            fig.update_xaxes(title_text=spec.x_label, row=spec.row, col=spec.col)
            fig.update_yaxes(title_text=spec.y_label, row=spec.row, col=spec.col)

        fig.update_layout(
            title=dict(text=title),
            height=height * self.n_rows,
            width=width * self.n_cols,
            template="plotly_white",
            legend=dict(orientation="h", yanchor="top", y=-0.5, xanchor="right", x=1),
        )
        return fig
