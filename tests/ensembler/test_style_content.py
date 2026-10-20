from biomechzoo.ensembler.style_content import StyleContext


def test_subject_color_assigned_in_order():
    style = StyleContext(subjects=["S1", "S2"], conditions=[])

    assert style.subject_color("S1") == style._SUBJECT_COLORS[0]
    assert style.subject_color("S2") == style._SUBJECT_COLORS[1]


def test_subject_color_unassigned_subject_falls_back():
    style = StyleContext(subjects=["S1"], conditions=[])

    assert style.subject_color("unknown") == "#333"


def test_condition_color_and_dash_assigned_in_order():
    style = StyleContext(subjects=[], conditions=["A", "B"])

    assert style.condition_color("A") == style._CONDITION_COLORS[0]
    assert style.condition_color("B") == style._CONDITION_COLORS[1]
    assert style.condition_dash("A") == "solid"
    assert style.condition_dash("B") == "dash"


def test_condition_color_cycles_when_more_conditions_than_colors():
    n_colors = len(StyleContext._CONDITION_COLORS)
    conditions = [f"cond_{i}" for i in range(n_colors + 1)]
    style = StyleContext(subjects=[], conditions=conditions)

    assert style.condition_color(conditions[0]) == style.condition_color(
        conditions[n_colors]
    )


def test_condition_color_unassigned_falls_back():
    style = StyleContext(subjects=[], conditions=["A"])

    assert style.condition_color("unknown") == "#333"


def test_condition_dash_unassigned_falls_back_to_solid():
    style = StyleContext(subjects=[], conditions=["A"])

    assert style.condition_dash("unknown") == "solid"


def test_conditions_none_behaves_like_empty_list():
    style = StyleContext(subjects=["S1"], conditions=None)

    assert style.condition_color("A") == "#333"
    assert style.condition_dash("A") == "solid"


def test_should_show_legend_true_once_then_false():
    style = StyleContext(subjects=["S1"], conditions=["A"])

    assert style.should_show_legend("subj", "S1") is True
    assert style.should_show_legend("subj", "S1") is False


def test_should_show_legend_distinguishes_namespace():
    style = StyleContext(subjects=["S1"], conditions=["A"])

    assert style.should_show_legend("subj", "S1") is True
    assert style.should_show_legend("event", "S1") is True
