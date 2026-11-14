from biomechzoo.ensembler.ensembler import Ensembler
from biomechzoo.ensembler.plot_spec import PlotSpec


class RecordingRenderer:
    """Stub renderer recording every render() call it receives."""

    def __init__(self):
        self.calls = []

    def render(self, fig, store, style, spec, row, col):
        self.calls.append((spec, row, col))


def test_init_builds_store_and_style_from_empty_folder(tmp_path):
    ensembler = Ensembler(
        in_folder=str(tmp_path), channels=["ch"], n_rows=1, n_cols=1,
    )

    assert ensembler.store.subjects == []
    assert ensembler.n_rows == 1
    assert ensembler.n_cols == 1
    assert ensembler.specs == []


def test_add_subplot_returns_self_and_registers_spec(tmp_path):
    ensembler = Ensembler(
        in_folder=str(tmp_path), channels=["ch"], n_rows=1, n_cols=1,
    )
    spec = PlotSpec(channel="ch")

    result = ensembler.add_subplot(spec)

    assert result is ensembler
    assert ensembler.specs == [spec]


def test_add_subplot_is_chainable(tmp_path):
    ensembler = Ensembler(
        in_folder=str(tmp_path), channels=["ch"], n_rows=1, n_cols=2,
    )
    spec_a = PlotSpec(channel="ch", row=1, col=1)
    spec_b = PlotSpec(channel="ch", row=1, col=2)

    ensembler.add_subplot(spec_a).add_subplot(spec_b)

    assert ensembler.specs == [spec_a, spec_b]


def test_build_calls_render_once_per_registered_spec(tmp_path):
    renderer = RecordingRenderer()
    ensembler = Ensembler(
        in_folder=str(tmp_path), channels=["ch"], n_rows=1, n_cols=2,
    )
    spec_a = PlotSpec(channel="ch", row=1, col=1, renderer=renderer)
    spec_b = PlotSpec(channel="ch", row=1, col=2, renderer=renderer)
    ensembler.add_subplot(spec_a).add_subplot(spec_b)

    ensembler.build()

    assert renderer.calls == [(spec_a, 1, 1), (spec_b, 1, 2)]


def test_build_returns_figure_with_requested_dimensions(tmp_path):
    renderer = RecordingRenderer()
    ensembler = Ensembler(
        in_folder=str(tmp_path), channels=["ch"], n_rows=2, n_cols=3,
    )
    ensembler.add_subplot(
        PlotSpec(channel="ch", row=1, col=1, renderer=renderer)
    )

    fig = ensembler.build(height=100, width=200)

    assert fig.layout.height == 100 * 2
    assert fig.layout.width == 200 * 3


def test_build_sets_subplot_titles_from_spec_title(tmp_path):
    renderer = RecordingRenderer()
    ensembler = Ensembler(
        in_folder=str(tmp_path), channels=["ch"], n_rows=1, n_cols=2,
    )
    ensembler.add_subplot(
        PlotSpec(
            channel="ch", row=1, col=2, title="My title", renderer=renderer,
        )
    )

    fig = ensembler.build()

    titles = [a.text for a in fig.layout.annotations]
    assert "My title" in titles
