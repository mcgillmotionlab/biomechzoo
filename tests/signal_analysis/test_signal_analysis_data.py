import numpy as np
from biomechzoo.signal_analysis.signal_analysis_data import signal_analysis_data

def test_signal_analysis_data():

    # Create a simple test dataset
    data = {
        "C7": {
            "line": np.array([0, 1, 0, -1, 0, 1, 0, -1, 0], dtype=float),
            "event": {},
        },
        "zoosystem": {"Video": {"Freq": 100}},
    }

    # Test impact_peak analysis
    data_new = signal_analysis_data(data, channels="C7", etype="impact_peak", ename="impact_peak")
    assert "impact_peak_1" in data_new["C7"]["event"]
    assert isinstance(data_new["C7"]["event"]["impact_peak_1"], list)

    # Test loading_rate analysis
    data_new = signal_analysis_data(data, channels="C7", etype="loading_rate", ename="loading_rate")
    assert "loading_rate_1" in data_new["C7"]["event"]
    assert isinstance(data_new["C7"]["event"]["loading_rate_1"], list)