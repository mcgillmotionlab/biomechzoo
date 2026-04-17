from abc import ABC, abstractmethod
from src.data_store import DataStore
import plotly.graph_objs as go
import plotly.express as px
import numpy as np

from src.style_content import StyleContext
from src.helpers import compute_ensemble, _compute_bandwidth, align_by_subject, resolve_shade

# to test my bland-altman plot
import pyCompare


#### Plot options to add
# Scatter plot/correlation plots --> regression line option?
# Violinplots
# MeanSD
# RainCloud?

class Renderer(ABC):
    """
    Knows how to add traces for ONE (channel, condition) into a subplot
    Receives the DataStore and shared style context - Nothing else.
    """

    @abstractmethod
    def render(self,
               fig: go.Figure,
               store: DataStore,
               style: StyleContext,
               spec: "PlotSpec",
               row: int,
               col: int,
               ) -> None: ...


class IndividualLinesRenderer(Renderer):
    def render(self, fig, store, style, spec, row, col):
        for condition in spec.all_conditions:
            arrays = store.get_lines(spec.channel, condition)
            subjects = store.get_subject_ids(spec.channel, condition)
            x_norm = np.linspace(0, 100, max((len(a) for a in arrays), default=1))

            for arr, subj in zip(arrays, subjects):
                color = style.subject_color(subj)
                dash = style.condition_dash(condition)
                show_leg = style.should_show_legend("subj", subj)

                fig.add_trace(go.Scatter(
                    x=x_norm, y=arr,
                    mode="lines",
                    name=subj,
                    legendgroup=subj,
                    line=dict(color=color, dash=dash, width=1.2),
                    opacity=0.45,
                    showlegend=show_leg,
                    hovertemplate=f"<b>{subj}</b><br>%{{x:.1f}}% | %{{y:.2f}}<extra></extra>",
                ), row=row, col=col)


class MeanSDRenderer(Renderer):
    def render(self, fig, store, style, spec, row, col):
        for condition in spec.all_conditions:
            arrays = store.get_lines(spec.channel, condition)
            if not arrays:
                return

            n = len(arrays[0])
            x = np.linspace(0, 100, n)
            mean, upper, lower = compute_ensemble(arrays)
            color = style.condition_color(condition)
            dash = style.condition_dash(condition)
            shade_color = resolve_shade(color)
            # Standard deviation ribbon lower limit
            fig.add_trace(go.Scatter(
                x=x,
                y=lower,
                fillcolor=shade_color,
                line=dict(color="rgba(0,0,0,0)"),
                showlegend=False,
            ), row=row, col=col)

            # Standard deviation ribbon upper limit
            fig.add_trace(go.Scatter(
                x=x,
                y=upper,
                fill="tonexty",
                fillcolor=shade_color,
                line=dict(color="rgba(0,0,0,0)"),
                showlegend=False,
            ), row=row, col=col)

            # mean line
            show_leg = style.should_show_legend("mean", condition)
            fig.add_trace(go.Scatter(
                x=x, y=mean,
                name=f"Mean_{condition}",
                legendgroup=f"Mean_{condition}",
                line=dict(color=color, width=3, dash=dash),
                hovertemplate=f"<b>Mean – {condition}</b><br>%{{x:.1f}}% | %{{y:.2f}}<extra></extra>",
                showlegend=show_leg,
            ), row=row, col=col)


class EventOverlayRenderer(Renderer):
    def render(self, fig, store, style, spec, row, col):
        if not spec.events:
            return

        for event_name in spec.events:
            for condition in spec.all_conditions:
                evs = store.get_events(spec.channel, condition, event_name)  # list[ZooEvent]
                subjects = store.get_event_subject_ids(spec.channel, condition, event_name)
                for ev, subj in zip(evs, subjects):
                    color = style.subject_color(subj)
                    show_leg = style.should_show_legend("event", f"{subj}_{event_name}")
                    fig.add_trace(go.Scatter(
                        x=[ev.x], y=[ev.y],
                        mode="markers",
                        name=f"{subj} – {event_name}",
                        legendgroup=subj,
                        marker=dict(color=color, size=8),
                        showlegend=show_leg,
                        hovertemplate=(
                            f"<b>{subj} – {event_name}</b><br>"
                            f"x: %{{x:.1f}} | y: %{{y:.2f}}<extra></extra>"
                        ),
                    ), row=row, col=col)


class ViolinRenderer(Renderer):
    def __init__(self, show_points: bool = True, bandwidth: float | None = None):
        self.show_points = show_points
        self.bandwidth = bandwidth

    def render(self, fig, store, style, spec, row, col):
        if not spec.events:
            return

        for event_name in spec.events:
            for condition in spec.all_conditions:
                values = store.get_event_values(spec.channel, condition, event_name)  # y-only
                subjects = store.get_event_subject_ids(spec.channel, condition, event_name)
                if not values:
                    continue

                if spec.group_by and spec.group_map:
                    groups = [spec.group_map.get(s, "Unknown") for s in subjects]
                else:
                    groups = [condition] * len(values)

                unique_groups = dict.fromkeys(groups)
                for grp in unique_groups:
                    grp_values = [v for v, g in zip(values, groups) if g == grp]
                    bw = self.bandwidth if self.bandwidth is not None else _compute_bandwidth(grp_values)

                    color = style.condition_color(condition)
                    label      = f"{condition} – {event_name} – {grp}" if spec.group_by else f"{condition} – {event_name}"
                    show_leg = style.should_show_legend("violin", grp)

                    fig.add_trace(go.Violin(
                        x = [f"{grp}"] * len(grp_values),
                        y = grp_values,
                        name=grp,
                        legendgroup=label,
                        line_color=color,
                        fillcolor=color,
                        opacity=0.6,
                        box_visible=True,
                        points="all" if self.show_points else False,
                        bandwidth=bw,
                        showlegend=show_leg,
                    ), row=row, col=col)


class BlandAltmanRenderer(Renderer):
    """
    Plots a BlandAltman agreement plot between two conditions

    Requires exactly two conditions via spec.all_conditions.

    Computes:
    mean = (method_A - method_B) / 2
    diff = methodA - method_B
    bias = mean(diff)
    LoA = bias +/- 1.96 * std(diff)

    Works with either:
    - line data (Uses a scaler per trial, e.g. mean of the line)
    - event data (Uses event scaler directly, e.g. "max")
    """

    def __init__(self, use_events: bool = False, show_subjects: bool = False, loa_multiplier: float = 1.96, line_scaler : str = "mean"):

        if line_scaler not in ("mean", "max", "min", "median"):
            raise ValueError("line_scaler must be one of 'mean', 'max', 'min', or 'median'")
        self.use_events = use_events
        self.show_subjects = show_subjects
        self.loa_multiplier = loa_multiplier
        self.line_scaler = line_scaler


    def render(self, fig, store, style, spec, row, col):
        if len(spec.all_conditions) != 2:
            raise ValueError(f"BlandAltmanRenderer requires exactly two conditions, "
                             f"got {spec.all_conditions}. Use companions= to specify the second")

        cond_a, cond_b = spec.all_conditions

        if self.use_events:
            if not spec.events:
                raise ValueError(f"BlandAltmanRenderer with use_events=True requires events to be specified ")
            event_name = spec.events[0]

            vals_a = store.get_event_values(spec.channel, cond_a, event_name)
            vals_b = store.get_event_values(spec.channel, cond_b, event_name)

            # pyCompare.blandAltman(vals_a, vals_b)
            subjects_a = store.get_event_subject_ids(spec.channel, cond_a, event_name)
            subjects_b = store.get_event_subject_ids(spec.channel, cond_b, event_name)

            vals_a, vals_b, subjects = align_by_subject(vals_a, subjects_a, vals_b, subjects_b)

            if not vals_a:
                return

            arr_a = np.asarray(vals_a)
            arr_b = np.asarray(vals_b)
            means = np.mean([arr_a, arr_b], axis=0)
            diffs = arr_a - arr_b

            bias = float(np.mean(diffs))
            sd = float(np.std(diffs))
            loa_upper = bias + self.loa_multiplier * sd
            loa_lower = bias - self.loa_multiplier * sd

            x_min, x_max = np.min(arr_a), np.max(arr_a)
            x_pad = (x_max - x_min) * 0.1
            x_range = [x_min - x_pad, x_max + x_pad]

            for mean_val, diff_val, subj in zip(means, diffs, subjects):
                color = style.subject_color(subj) if self.show_subjects else "#1f77b4"
                show_leg = style.should_show_legend("ba_subj", subj) if self.show_subjects else False

                # subject scatter
                fig.add_trace(go.Scatter(
                    x = [mean_val], y=[diff_val],
                    mode = "markers", name=subj,
                    marker=dict(color=color, size=8,),
                    legendgroup=subj,
                    showlegend=show_leg,
                ), row=row, col=col)

            # bias, loa, and reference lines
            fig.add_hline(y = bias, line_color="black", line_dash="dash",
                          annotation_text=f"Bias: {bias:.2f}",
                          annotation_position="bottom right", row=row, col=col)

            fig.add_hline(y = loa_upper, line_color="red", line_dash="dash",
                          annotation_text = f"LoA: {loa_upper:.2f}",
                          annotation_position = "top right", row=row, col=col)
            fig.add_hline(y = loa_lower, line_color="red", line_dash="dash",
                          annotation_text = f"LoA: {loa_lower:.2f}",
                          annotation_position = "bottom right", row=row, col=col)

            fig.add_hline(y=0, line_color="grey", line_dash="dash", row=row, col=col)


class ScatterRenderer(Renderer):
    """
    """

    def __init__(self, regression_line: bool = False, show_subjects: bool = False, identity_line: bool = True,):
        self.regression_line = regression_line
        self.show_subjects = show_subjects
        self.identity_line = identity_line


    def render(self, fig, store, style, spec, row, col):
        if len(spec.all_conditions) != 2:
            raise ValueError(f"ScatterRenderer requires exactly two conditions, "
                             f"got {spec.all_conditions}. Use companions= to specify the second")

        cond_a, cond_b = spec.all_conditions

        if not spec.events:
            raise ValueError(f"ScatterRenderer requires events to be specified ")

        event_name = spec.events[0]

        vals_a = store.get_event_values(spec.channel, cond_a, event_name)
        vals_b = store.get_event_values(spec.channel, cond_b, event_name)

        # pyCompare.blandAltman(vals_a, vals_b)
        subjects_a = store.get_event_subject_ids(spec.channel, cond_a, event_name)
        subjects_b = store.get_event_subject_ids(spec.channel, cond_b, event_name)

        vals_a, vals_b, subjects = align_by_subject(vals_a, subjects_a, vals_b, subjects_b)

        if not vals_a:
            return

        arr_a = np.asarray(vals_a)
        arr_b = np.asarray(vals_b)

        for a, b, subj in zip(arr_a, arr_b, subjects):
            color = style.subject_color(subj) if self.show_subjects else style.condition_color(cond_a)
            show_leg = style.should_show_legend("scatter_subj", subj) if self.show_subjects else False

            # subject scatter
            fig.add_trace(go.Scatter(
                x=[a], y=[b],
                mode="markers", name=subj,
                marker=dict(color=color, size=8, ),
                legendgroup=subj,
                showlegend=show_leg,
            ), row=row, col=col)

        # Plot the identity line
        if self.identity_line:
            all_vals = np.concatenate([arr_a, arr_b])
            lim = [float(all_vals.min()), float(all_vals.max())]
            fig.add_trace(go.Scatter(
                x=lim, y=lim,
                mode="lines", name="Identity (y=x)",
                line=dict(color="grey", width=1.5, dash="dot"),
                showlegend=True,
            ), row=row, col=col)


        # Get the OLS regression line
        if self.regression_line:
            coeffs = np.polyfit(arr_a, arr_b, 1)
            x_line = np.linspace(arr_a.min(), arr_a.max(), 100)
            y_line = np.polyval(coeffs, x_line)
            r_sq = np.corrcoef(arr_a, arr_b)[0, 1] ** 2

            fig.add_trace(go.Scatter(
                x=x_line, y=y_line,
                mode="lines", name=f"OLS (R²={r_sq:.2f})",
                line=dict(color="#333", width=2.5),
                showlegend=True,
            ), row=row, col=col)


#==================================================
#All future renders be placed right above this line
#==================================================

# Compose renderers freely
class CompositeRenderer(Renderer):
    """Run multiple renderers on the same subplot"""

    def __init__(self, *renderers: Renderer):
        self._renderers = renderers

    def render(self, fig, store, style, spec, row, col):
        for r in self._renderers:
            r.render(fig, store, style, spec, row, col)
