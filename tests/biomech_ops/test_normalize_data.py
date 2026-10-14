import numpy as np

from biomechzoo.biomech_ops.normalize_data import normalize_data


def test_normalize_data():
    """Check that the default normalizes a 140-frame channel to 101 frames."""
    data = {
        "C7": {
            "line": np.arange(140, dtype=float),
            "event": {"midpoint": [70, 1.5, 0]},
        },
        "zoosystem": {"Video": {"CURRENT_END_FRAME": 140}},
    }

    data_new = normalize_data(data)

    assert data_new["C7"]["line"].shape == (101,)
    assert data_new["C7"]["event"]["midpoint"] == [50, 1.5, 0]
    assert data_new["zoosystem"]["Video"]["CURRENT_END_FRAME"] == 101


def test_normalize_data_custom_length():
    """Check that a custom length can grow a 140-frame channel to 200 frames."""
    data = {
        "C7": {
            "line": np.arange(140, dtype=float),
            "event": {"midpoint": [70, 1.5, 0]},
        },
        "zoosystem": {"Video": {"CURRENT_END_FRAME": 140}},
    }

    data_new = normalize_data(data, nlength=200)

    assert data_new["C7"]["line"].shape == (200,)
    assert data_new["C7"]["event"]["midpoint"] == [100, 1.5, 0]
    assert data_new["zoosystem"]["Video"]["CURRENT_END_FRAME"] == 200
