import numpy as np
import pytest
from scipy.io import savemat

from biomechzoo.ensembler.data_store import DataStore
from biomechzoo.ensembler.helpers import ConditionSource, ConditionSpec


def write_zoo(path, channels):
    """Write a minimal synthetic .zoo file (a dict of channel dicts)."""
    savemat(str(path), {"data": channels})


def make_channel(line, event=None):
    return {"line": np.asarray(line, dtype=float), "event": event or {}}


@pytest.fixture
def between_store(tmp_path):
    """Two conditions (folders) x two subjects, one channel each."""
    for condition in ("Straight", "Turn"):
        folder = tmp_path / condition
        folder.mkdir()
        for subj, scale in (("S1", 1.0), ("S2", 2.0)):
            write_zoo(
                folder / f"{subj}_{condition}.zoo",
                {
                    "RKneeAngles_x": make_channel(
                        [scale, scale + 1, scale + 2],
                        event={"max": [1, scale + 1]},
                    ),
                },
            )
    return DataStore(
        fld=str(tmp_path),
        condition_spec=ConditionSpec(
            source=ConditionSource.BETWEEN, conditions=["Straight", "Turn"],
        ),
        str_match=[r"S\d"],
    )


def test_resolves_subjects(between_store):
    assert sorted(between_store.subjects) == ["S1", "S2"]


def test_get_lines_returns_one_array_per_subject(between_store):
    lines = between_store.get_lines("RKneeAngles_x", "Straight")

    assert len(lines) == 2
    assert sorted(a[0] for a in lines) == [1.0, 2.0]


def test_get_lines_filters_by_condition(between_store):
    straight = between_store.get_lines("RKneeAngles_x", "Straight")
    turn = between_store.get_lines("RKneeAngles_x", "Turn")

    assert len(straight) == 2
    assert len(turn) == 2


def test_get_subject_ids_matches_get_lines_order(between_store):
    lines = between_store.get_lines("RKneeAngles_x", "Straight")
    subjects = between_store.get_subject_ids("RKneeAngles_x", "Straight")

    assert len(subjects) == len(lines)
    assert set(subjects) == {"S1", "S2"}


def test_get_events_returns_zoo_events(between_store):
    events = between_store.get_events("RKneeAngles_x", "Straight", "max")

    assert len(events) == 2
    assert sorted(ev.y for ev in events) == [2.0, 3.0]


def test_get_event_values_is_y_only(between_store):
    values = between_store.get_event_values("RKneeAngles_x", "Straight", "max")

    assert sorted(values) == [2.0, 3.0]


def test_get_event_subject_ids(between_store):
    subjects = between_store.get_event_subject_ids(
        "RKneeAngles_x", "Straight", "max",
    )

    assert set(subjects) == {"S1", "S2"}


def test_get_paired_aligns_by_subject_across_conditions(between_store):
    vals_a, vals_b, subjects = between_store.get_paired(
        "RKneeAngles_x", "Straight", "Turn", line_scalar="mean",
    )

    assert len(vals_a) == len(vals_b) == len(subjects) == 2
    assert set(subjects) == {"S1", "S2"}


def test_to_lines_dataframe_shape(between_store):
    df = between_store.to_lines_dataframe(["RKneeAngles_x"])

    # 2 conditions x 2 subjects x 3 frames (not resampled, raw line length)
    assert len(df) == 2 * 2 * 3
    assert set(df.columns) == {
        "subject", "condition", "channel", "frame", "value",
    }


def test_to_events_dataframe_shape(between_store):
    df = between_store.to_events_dataframe(["RKneeAngles_x"], ["max"])

    assert len(df) == 2 * 2  # 2 conditions x 2 subjects
    assert set(df.columns) == {
        "subject", "condition", "channel", "event", "value",
    }


@pytest.fixture
def within_store(tmp_path):
    """One condition encoded via channel-name suffix, not folder."""
    write_zoo(
        tmp_path / "S1.zoo",
        {
            "RKnee_a": make_channel([1.0, 2.0, 3.0]),
            "RKnee_b": make_channel([4.0, 5.0, 6.0]),
        },
    )
    spec = ConditionSpec(
        source=ConditionSource.WITHIN,
        suffix_map={"cond_a": "_a", "cond_b": "_b"},
        base_channels=["RKnee"],
    )
    return DataStore(
        fld=str(tmp_path), condition_spec=spec, str_match=[r"S\d"],
    )


def test_within_source_resolves_correct_channel(within_store):
    lines_a = within_store.get_lines("RKnee", "cond_a")
    lines_b = within_store.get_lines("RKnee", "cond_b")

    assert lines_a[0].tolist() == [1.0, 2.0, 3.0]
    assert lines_b[0].tolist() == [4.0, 5.0, 6.0]


def test_get_intra_channel_pairs_two_channels_same_subject(tmp_path):
    write_zoo(
        tmp_path / "S1.zoo",
        {
            "ChannelA": make_channel([1.0], event={"max": [1, 10.0]}),
            "ChannelB": make_channel([1.0], event={"max": [1, 20.0]}),
        },
    )
    store = DataStore(
        fld=str(tmp_path),
        condition_spec=ConditionSpec(
            source=ConditionSource.BETWEEN, conditions=[],
        ),
        str_match=[r"S\d"],
    )

    vals_a, vals_b, subjects = store.get_intra_channel(
        "ChannelA", "ChannelB", "__all__", event_name="max",
    )

    assert vals_a == [10.0]
    assert vals_b == [20.0]
    assert subjects == ["S1"]
