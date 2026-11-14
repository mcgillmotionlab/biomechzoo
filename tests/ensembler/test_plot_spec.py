from biomechzoo.ensembler.plot_spec import PlotSpec


def test_title_defaults_to_channel_name():
    spec = PlotSpec(channel="RKneeAngles_x")

    assert spec.title == "RKneeAngles_x"


def test_title_not_overwritten_when_provided():
    spec = PlotSpec(channel="RKneeAngles_x", title="Knee flexion")

    assert spec.title == "Knee flexion"


def test_all_conditions_combines_condition_and_companions():
    spec = PlotSpec(
        channel="ch", condition="Straight", companions=["Turn", "Run"],
    )

    assert spec.all_conditions == ["Straight", "Turn", "Run"]


def test_all_conditions_with_no_condition_set():
    spec = PlotSpec(channel="ch", companions=["Turn"])

    assert spec.all_conditions == [None, "Turn"]


def test_defaults():
    spec = PlotSpec(channel="ch")

    assert spec.condition is None
    assert spec.row == 1
    assert spec.col == 1
    assert spec.renderer is None
    assert spec.events == []
    assert spec.companions == []
    assert spec.companion_channel is None
    assert spec.line_scalar == "mean"
    assert spec.x_label == ""
    assert spec.y_label == ""
