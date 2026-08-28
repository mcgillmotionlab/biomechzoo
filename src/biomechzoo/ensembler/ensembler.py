from plotly.subplots import make_subplots
import plotly.graph_objs as go

from biomechzoo.ensembler.data_store import DataStore
from biomechzoo.ensembler.helpers import ConditionSpec
from biomechzoo.ensembler.plot_spec import PlotSpec
from biomechzoo.ensembler.style_content import StyleContext


class Ensembler:
    """Builds a multi-subplot figure of ensembled/individual zoo data."""

    def __init__(
            self, in_folder: str, channels: list[str],
            n_rows: int, n_cols: int,
            condition_spec: ConditionSpec | None = None,
            subj_list: list[str] | None = None,
            str_match: list[str] | None = None,
            events: list[str] | None = None,
    ) -> None:
        """
        Parameters
        ----------
        in_folder : str
            Root folder containing .zoo files.
        channels : list of str
            Channel names available for plotting.
        n_rows : int
            Number of subplot rows.
        n_cols : int
            Number of subplot columns.
        condition_spec : ConditionSpec, optional
            Describes how conditions are encoded in the data.
        subj_list : list of str, optional
            Known subject IDs, used to resolve subject IDs from filenames.
        str_match : list of str, optional
            Regex pattern(s) used to resolve subject IDs from filenames.
        events : list of str, optional
            Event names available for event-based renderers.
        """
        self.store = DataStore(
            fld=in_folder, condition_spec=condition_spec, events=events,
            subj_list=subj_list, str_match=str_match,
        )
        self.style = StyleContext(self.store.subjects, self.store.conditions)
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.channels = channels
        self.specs: list[PlotSpec] = []

    def add_subplot(self, spec: PlotSpec) -> "Ensembler":
        """Register a :class:`PlotSpec` to be rendered by :meth:`build`."""
        self.specs.append(spec)
        return self

    def build(
            self, title: str = "Ensembler", height: int = 400,
            width: int = 500,
    ) -> go.Figure:
        """
        Build the multi-subplot figure from all registered subplot specs.

        Parameters
        ----------
        title : str, optional
            Overall figure title. Default is "Ensembler".
        height : int, optional
            Height per subplot row, in pixels. Default is 400.
        width : int, optional
            Width per subplot column, in pixels. Default is 500.

        Returns
        -------
        fig : plotly.graph_objs.Figure
            The assembled figure.
        """
        subplot_titles = [""] * (self.n_rows * self.n_cols)
        for s in self.specs:
            subplot_titles[(s.row - 1) * self.n_cols + (s.col - 1)] = s.title

        fig = make_subplots(
            rows=self.n_rows, cols=self.n_cols,
            subplot_titles=subplot_titles,
            vertical_spacing=0.20,
            horizontal_spacing=0.10,
            shared_xaxes=False,
            shared_yaxes=False,
        )

        for spec in self.specs:
            spec.renderer.render(
                fig, self.store, self.style,
                spec,spec.row, spec.col
            )
            fig.update_xaxes(
                title_text=spec.x_label, row=spec.row, col=spec.col,
            )
            fig.update_yaxes(
                title_text=spec.y_label, row=spec.row, col=spec.col,
            )

        fig.update_layout(
            title=dict(text=title),
            height=height * self.n_rows,
            width=width * self.n_cols,
            template="plotly_white",
            legend=dict(
                orientation="h", yanchor="top", y=-0.5,
                xanchor="right", x=1,
            ),
        )
        return fig
