import numpy as np
import pytest
from plotly.subplots import make_subplots

from biomechzoo.ensembler.helpers import ZooEvent
from biomechzoo.ensembler.plot_spec import PlotSpec
from biomechzoo.ensembler.style_content import StyleContext
from biomechzoo.ensembler.renderers import (
    BlandAltmanRenderer,
    CompositeRenderer,
    EventOverlayRenderer,
    IndividualLinesRenderer,
    MeanSDRenderer,
    ScatterRenderer,
    ViolinRenderer,
)


class StubPairedStore:
    """Stub DataStore recording the kwargs it was called with."""

    def __init__(self, vals_a=None, vals_b=None, subjects=None):
        self.vals_a = vals_a if vals_a is not None else [1.0, 2.0]
        self.vals_b = vals_b if vals_b is not None else [1.1, 2.2]
        self.subjects = subjects if subjects is not None else ["S1", "S2"]
        self.calls = []

    def get_paired(self, **kwargs):
        self.calls.append(("get_paired", kwargs))
        return self.vals_a, self.vals_b, self.subjects

    def get_intra_channel(self, **kwargs):
        self.calls.append(("get_intra_channel", kwargs))
        return self.vals_a, self.vals_b, self.subjects


class StubLineStore:
    """Stub DataStore for line-based renderers (Individual/MeanSD)."""

    def __init__(self, arrays, subjects):
        self.arrays = arrays
        self.subjects = subjects

    def get_lines(self, channel, condition):
        return self.arrays

    def get_subject_ids(self, channel, condition):
        return self.subjects


class StubEventStore:
    """Stub DataStore for event-based renderers (EventOverlay/Violin)."""

    def __init__(self, events, values, subjects):
        self.events = events
        self.values = values
        self.subjects = subjects

    def get_events(self, channel, condition, event_name):
        return self.events

    def get_event_values(self, channel, condition, event_name):
        return self.values

    def get_event_subject_ids(self, channel, condition, event_name):
        return self.subjects


def make_style(subjects, conditions):
    return StyleContext(subjects, conditions)


def make_fig():
    return make_subplots(rows=1, cols=1)


# -- BlandAltmanRenderer: companion_channel branch (regression for #60) --

def test_bland_altman_companion_channel_uses_condition():
    store = StubPairedStore()
    spec = PlotSpec(
        channel="ch", companion_channel="ch2", condition="A",
        events=["max"],
    )
    BlandAltmanRenderer(line_scalar="mean").render(
        make_fig(), store, make_style(["S1", "S2"], ["A"]), spec, 1, 1,
    )
    name, kwargs = store.calls[0]
    assert name == "get_intra_channel"
    assert kwargs["condition"] == "A"


# -- BlandAltmanRenderer: two-condition branch (regression for #61) --

def test_bland_altman_two_condition_uses_line_scalar():
    store = StubPairedStore()
    spec = PlotSpec(
        channel="ch", condition="A", companions=["B"], events=["max"],
    )
    BlandAltmanRenderer(line_scalar="max").render(
        make_fig(), store, make_style(["S1", "S2"], ["A", "B"]), spec, 1, 1,
    )
    name, kwargs = store.calls[0]
    assert name == "get_paired"
    assert kwargs["line_scalar"] == "max"


def test_bland_altman_rejects_non_two_conditions():
    store = StubPairedStore()
    spec = PlotSpec(channel="ch", condition="A", events=["max"])
    with pytest.raises(ValueError, match="exactly two conditions"):
        BlandAltmanRenderer().render(
            make_fig(), store, make_style(["S1"], ["A"]), spec, 1, 1,
        )


def test_bland_altman_rejects_invalid_line_scalar():
    with pytest.raises(ValueError, match="line_scaler"):
        BlandAltmanRenderer(line_scalar="bogus")


# -- ScatterRenderer: spec.line_scalar field exists (regression for #62) --

def test_scatter_two_condition_uses_spec_line_scalar():
    store = StubPairedStore()
    spec = PlotSpec(
        channel="ch", condition="A", companions=["B"], events=["max"],
        line_scalar="median",
    )
    ScatterRenderer().render(
        make_fig(), store, make_style(["S1", "S2"], ["A", "B"]), spec, 1, 1,
    )
    name, kwargs = store.calls[0]
    assert name == "get_paired"
    assert kwargs["line_scalar"] == "median"


# -- ScatterRenderer: cond_a fallback on companion_channel branch
# -- (regression for the masked UnboundLocalError in #62) --

def test_scatter_companion_channel_show_subjects_false_does_not_crash():
    store = StubPairedStore()
    spec = PlotSpec(
        channel="ch", companion_channel="ch2", condition="A",
        events=["max"],
    )
    fig = make_fig()
    ScatterRenderer(show_subjects=False).render(
        fig, store, make_style(["S1", "S2"], ["A"]), spec, 1, 1,
    )
    # one marker trace per subject + the default identity line
    assert len(fig.data) == 3


def test_scatter_companion_channel_show_subjects_true():
    store = StubPairedStore()
    spec = PlotSpec(
        channel="ch", companion_channel="ch2", condition="A",
        events=["max"],
    )
    fig = make_fig()
    ScatterRenderer(show_subjects=True).render(
        fig, store, make_style(["S1", "S2"], ["A"]), spec, 1, 1,
    )
    assert len(fig.data) == 3


def test_scatter_identity_line_false_omits_identity_trace():
    store = StubPairedStore()
    spec = PlotSpec(
        channel="ch", condition="A", companions=["B"], events=["max"],
    )
    fig = make_fig()
    ScatterRenderer(identity_line=False).render(
        fig, store, make_style(["S1", "S2"], ["A", "B"]), spec, 1, 1,
    )
    # one marker trace per subject, no identity line
    assert len(fig.data) == 2


def test_scatter_regression_line_adds_ols_trace():
    store = StubPairedStore(
        vals_a=[1.0, 2.0, 3.0], vals_b=[1.0, 2.0, 3.0],
        subjects=["S1", "S2", "S3"],
    )
    spec = PlotSpec(
        channel="ch", condition="A", companions=["B"], events=["max"],
    )
    fig = make_fig()
    ScatterRenderer(regression_line=True).render(
        fig, store, make_style(["S1", "S2", "S3"], ["A", "B"]), spec, 1, 1,
    )
    # 3 marker traces + identity line + OLS regression line
    assert len(fig.data) == 5
    assert "OLS" in fig.data[-1].name


# -- Happy-path tests for the remaining renderers --

def test_individual_lines_renderer_one_trace_per_subject():
    store = StubLineStore(
        arrays=[np.array([1.0, 2.0, 3.0]), np.array([2.0, 3.0, 4.0])],
        subjects=["S1", "S2"],
    )
    spec = PlotSpec(channel="ch", condition="A")
    fig = make_fig()
    IndividualLinesRenderer().render(
        fig, store, make_style(["S1", "S2"], ["A"]), spec, 1, 1,
    )
    assert len(fig.data) == 2


def test_mean_sd_renderer_three_traces():
    store = StubLineStore(
        arrays=[np.array([1.0, 2.0, 3.0]), np.array([2.0, 3.0, 4.0])],
        subjects=["S1", "S2"],
    )
    spec = PlotSpec(channel="ch", condition="A")
    fig = make_fig()
    MeanSDRenderer().render(
        fig, store, make_style(["S1", "S2"], ["A"]), spec, 1, 1,
    )
    # lower ribbon, upper ribbon, mean line
    assert len(fig.data) == 3


def test_event_overlay_renderer_one_marker_per_event():
    store = StubEventStore(
        events=[ZooEvent(x=10.0, y=1.5), ZooEvent(x=12.0, y=1.7)],
        values=None,
        subjects=["S1", "S2"],
    )
    spec = PlotSpec(channel="ch", condition="A", events=["max"])
    fig = make_fig()
    EventOverlayRenderer().render(
        fig, store, make_style(["S1", "S2"], ["A"]), spec, 1, 1,
    )
    assert len(fig.data) == 2


def test_event_overlay_renderer_no_events_is_noop():
    store = StubEventStore(events=[], values=None, subjects=[])
    spec = PlotSpec(channel="ch", condition="A")  # no events configured
    fig = make_fig()
    EventOverlayRenderer().render(
        fig, store, make_style([], ["A"]), spec, 1, 1,
    )
    assert len(fig.data) == 0


def test_violin_renderer_one_trace_per_group():
    store = StubEventStore(
        events=None,
        values=[1.5, 1.7, 1.6, 1.4, 1.8],
        subjects=["S1", "S2", "S3", "S4", "S5"],
    )
    spec = PlotSpec(channel="ch", condition="A", events=["max"])
    fig = make_fig()
    ViolinRenderer().render(
        fig, store, make_style(["S1", "S2", "S3", "S4", "S5"], ["A"]),
        spec, 1, 1,
    )
    assert len(fig.data) == 1


def test_violin_renderer_show_points_false_hides_points():
    store = StubEventStore(
        events=None, values=[1.5, 1.7, 1.6], subjects=["S1", "S2", "S3"],
    )
    spec = PlotSpec(channel="ch", condition="A", events=["max"])
    fig = make_fig()
    ViolinRenderer(show_points=False).render(
        fig, store, make_style(["S1", "S2", "S3"], ["A"]), spec, 1, 1,
    )
    assert fig.data[0].points is False


def test_violin_renderer_uses_fixed_bandwidth_when_given():
    store = StubEventStore(
        events=None, values=[1.5, 1.7, 1.6], subjects=["S1", "S2", "S3"],
    )
    spec = PlotSpec(channel="ch", condition="A", events=["max"])
    fig = make_fig()
    ViolinRenderer(bandwidth=0.5).render(
        fig, store, make_style(["S1", "S2", "S3"], ["A"]), spec, 1, 1,
    )
    assert fig.data[0].bandwidth == 0.5


def test_composite_renderer_runs_all_sub_renderers():
    calls = []

    class RecordingRenderer:
        def __init__(self, name):
            self.name = name

        def render(self, fig, store, style, spec, row, col):
            calls.append(self.name)

    composite = CompositeRenderer(
        RecordingRenderer("a"), RecordingRenderer("b"),
    )
    composite.render(make_fig(), None, None, None, 1, 1)
    assert calls == ["a", "b"]
