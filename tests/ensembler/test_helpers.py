import warnings

import numpy as np
import pytest

from biomechzoo.ensembler.helpers import (
    ConditionSource,
    ConditionSpec,
    ZooEvent,
    _compute_bandwidth,
    align_by_subject,
    compute_ensemble,
    extract_events,
    extract_subject_id,
    match_condition,
    resolve_shade,
)


# -- match_condition --

def test_match_condition_finds_match_case_insensitive():
    result = match_condition("data/STRAIGHT/HC001A.zoo", ["Straight", "Turn"])

    assert result == "Straight"


def test_match_condition_no_conditions_returns_all_sentinel():
    assert match_condition("data/Straight/HC001A.zoo", None) == "__all__"
    assert match_condition("data/Straight/HC001A.zoo", []) == "__all__"


def test_match_condition_no_match_returns_none():
    result = match_condition("data/Other/HC001A.zoo", ["Straight", "Turn"])

    assert result is None


# -- extract_subject_id --

def test_extract_subject_id_via_regex_pattern():
    result = extract_subject_id(
        "HC001A15.zoo", subj_list=None, str_pattern=[r"HC\d{3}[A-Z]"],
    )

    assert result == "HC001A"


def test_extract_subject_id_via_subject_list():
    result = extract_subject_id(
        "HC001A15.zoo", subj_list=["HC001A", "HC002B"], str_pattern=None,
    )

    assert result == "HC001A"


def test_extract_subject_id_no_match_returns_none():
    result = extract_subject_id(
        "unknown.zoo", subj_list=["HC001A"], str_pattern=None,
    )

    assert result is None


# -- extract_events --

def test_extract_events_returns_zoo_event():
    ch_data = {"event": {"max": [10, 1.5]}}

    assert extract_events(ch_data, "max") == ZooEvent(x=10, y=1.5)


def test_extract_events_sentinel_999_returns_none():
    ch_data = {"event": {"max": [10, 999]}}

    assert extract_events(ch_data, "max") is None


def test_extract_events_missing_key_returns_none():
    assert extract_events({}, "max") is None
    assert extract_events({"event": {}}, "max") is None


# -- compute_ensemble --

def test_compute_ensemble_mean_upper_lower():
    arrays = [np.array([1.0, 2.0, 3.0]), np.array([3.0, 4.0, 5.0])]

    mean, upper, lower = compute_ensemble(arrays)

    # per-column mean of {1,3}, {2,4}, {3,5} = 2, 3, 4; std = 1 for each
    np.testing.assert_allclose(mean, [2.0, 3.0, 4.0])
    np.testing.assert_allclose(upper, [3.0, 4.0, 5.0])
    np.testing.assert_allclose(lower, [1.0, 2.0, 3.0])


# -- ConditionSpec --

def test_condition_spec_between_source_unchanged():
    spec = ConditionSpec(source=ConditionSource.BETWEEN, conditions=["A", "B"])

    assert spec.conditions == ["A", "B"]
    assert spec.channel_map is None


def test_condition_spec_within_auto_builds_channel_map():
    spec = ConditionSpec(
        source=ConditionSource.WITHIN,
        suffix_map={"cond_a": "_a", "cond_b": "_b"},
        base_channels=["ch1", "ch2"],
    )

    assert spec.channel_map == {
        "cond_a": {"ch1": "ch1_a", "ch2": "ch2_a"},
        "cond_b": {"ch1": "ch1_b", "ch2": "ch2_b"},
    }
    assert spec.conditions == ["cond_a", "cond_b"]


def test_condition_spec_within_requires_suffix_map_and_base_channels():
    with pytest.raises(ValueError, match="channel_map"):
        ConditionSpec(source=ConditionSource.WITHIN)


# -- _compute_bandwidth --

def test_compute_bandwidth_positive_for_spread_data():
    bw = _compute_bandwidth([1.0, 2.0, 3.0, 4.0, 5.0])

    assert bw > 0


def test_compute_bandwidth_zero_for_constant_data():
    bw = _compute_bandwidth([2.0, 2.0, 2.0, 2.0])

    assert bw == 0


# -- align_by_subject --

def test_align_by_subject_pairs_matching_subjects():
    aligned_a, aligned_b, aligned_s = align_by_subject(
        [1.0, 2.0], ["S1", "S2"], [1.5, 2.5], ["S1", "S2"],
    )

    assert aligned_a == [1.0, 2.0]
    assert aligned_b == [1.5, 2.5]
    assert aligned_s == ["S1", "S2"]


def test_align_by_subject_drops_unmatched_subjects():
    aligned_a, aligned_b, aligned_s = align_by_subject(
        [1.0, 2.0], ["S1", "S2"], [1.5], ["S1"],
    )

    assert aligned_a == [1.0]
    assert aligned_b == [1.5]
    assert aligned_s == ["S1"]


def test_align_by_subject_warns_on_mismatched_trial_counts():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        align_by_subject(
            [1.0, 2.0], ["S1", "S1"], [1.5], ["S1"],
        )

    assert len(caught) == 1
    assert "S1" in str(caught[0].message)


# -- resolve_shade --

def test_resolve_shade_converts_hex_to_rgba():
    result = resolve_shade("#1f77b4")

    assert result == "rgba(31, 119, 180, 0.2)"
