import numpy as np

from biomechzoo.signal_analysis import compute_impact


def test_impact_peak_accepts_detection_parameters(monkeypatch):
    expected_peaks = np.array([10, 20, 30])
    expected_heights = np.array([1.0, 2.0, 4.0])
    received = {}

    def peak_impacts(data, freq, **kwargs):
        received.update(data=data, freq=freq, **kwargs)
        return expected_peaks, {"peak_heights": expected_heights}

    monkeypatch.setattr(compute_impact, "peak_impacts", peak_impacts)

    signal = np.zeros(40)
    peaks, heights = compute_impact.impact_peak(
        signal,
        100,
        distance_ratio=0.8,
        relative_peak_height=0.5,
        autocorrelation_peak_distance=25,
        autocorrelation_duration_sec=2.5,
        autocorrelation_peak_height=0.1,
        peak_height=0.2,
    )

    assert peaks == [20, 30]
    assert heights == [2.0, 4.0]
    assert received == {
        "data": signal,
        "freq": 100,
        "distance_ratio": 0.8,
        "autocorrelation_peak_distance": 25,
        "autocorrelation_duration_sec": 2.5,
        "autocorrelation_peak_height": 0.1,
        "peak_height": 0.2,
    }


def test_peak_impacts_accepts_peak_detection_parameters(monkeypatch):
    monkeypatch.setattr(compute_impact, "compute_distance", lambda *args, **kwargs: 12)
    received = {}

    def find_peaks(data, **kwargs):
        received.update(kwargs)
        return np.array([15]), {"peak_heights": np.array([1.0])}

    monkeypatch.setattr(compute_impact.signal, "find_peaks", find_peaks)
    data = np.zeros(30)

    peaks, properties = compute_impact.peak_impacts(
        data,
        100,
        distance_ratio=0.8,
        autocorrelation_peak_distance=25,
        autocorrelation_duration_sec=2.5,
        autocorrelation_peak_height=0.1,
        peak_height=0.2,
    )

    assert peaks.tolist() == [15]
    assert properties["peak_heights"].tolist() == [1.0]
    assert received == {"distance": 12, "height": 0.2}


def test_loading_rate_uses_configured_pre_peak_window(monkeypatch):
    monkeypatch.setattr(
        compute_impact,
        "peak_impacts",
        lambda *args, **kwargs: (np.array([22]), {"peak_heights": np.array([2.0])}),
    )
    differences = np.zeros(40)
    differences[3] = 10
    differences[17] = 5
    signal = np.r_[0, np.cumsum(differences)]

    peak_indices, rates = compute_impact.loading_rate(signal, 100, pre_peak_window=5)

    assert peak_indices == [17]
    assert rates == [5]


def test_compute_distance_accepts_autocorrelation_parameters(monkeypatch):
    autocorrelation_parameters = {}

    def compute_autocorrelation(data, freq, duration_sec):
        autocorrelation_parameters.update(freq=freq, duration_sec=duration_sec)
        return np.zeros(150)

    monkeypatch.setattr(compute_impact, "compute_autocorrelation", compute_autocorrelation)
    find_peaks_parameters = {}

    def find_peaks(data, **kwargs):
        find_peaks_parameters.update(kwargs)
        return np.array([50, 100]), {}

    monkeypatch.setattr(compute_impact.signal, "find_peaks", find_peaks)

    distance = compute_impact.compute_distance(
        np.zeros(100),
        distance_ratio=0.8,
        freq=100,
        autocorrelation_peak_distance=25,
        autocorrelation_duration_sec=2.5,
        autocorrelation_peak_height=0.1,
    )

    assert distance == 40
    assert autocorrelation_parameters == {"freq": 100, "duration_sec": 2.5}
    assert find_peaks_parameters == {"distance": 25, "height": 0.1}
