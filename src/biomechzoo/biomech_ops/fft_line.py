import numpy as np
import matplotlib.pyplot as plt


def fft_analysis(x, fs, thresh=10):
    """
    FFT analysis with cutoff frequency suggestion.

    Parameters
    ----------
    x : array-like
        Signal.
    fs : float
        Sampling frequency (Hz).
    thresh : float, optional
        Threshold as percentage of maximum amplitude.
        Default is 10 (%).

    Returns
    -------
    freq : ndarray
        Frequency vector (Hz).
    amp : ndarray
        Single-sided amplitude spectrum.
    mean_freq : float
        Amplitude-weighted mean frequency.
    max_freq : float
        Dominant frequency (excluding DC component).
    cutoff_freq : float
        Suggested cutoff frequency based on threshold.
    """

    x = np.asarray(x).squeeze()

    # Remove DC offset
    x = x - np.mean(x)

    N = len(x)

    # FFT
    fft_vals = np.fft.rfft(x)
    freq = np.fft.rfftfreq(N, d=1 / fs)

    # Single-sided amplitude spectrum
    amp = 2.0 * np.abs(fft_vals) / N

    # Normalize spectrum
    amp_norm = amp / np.max(amp)

    # Weighted mean frequency
    mean_freq = np.sum(freq * amp_norm) / np.sum(amp_norm)

    # Dominant frequency (ignore DC component)
    max_idx = np.argmax(amp_norm[1:]) + 1
    max_freq = freq[max_idx]

    # Suggested cutoff frequency
    threshold = thresh / 100.0
    idx = np.where(amp_norm > threshold)[0]

    if len(idx):
        cutoff_freq = freq[idx[-1]]
    else:
        cutoff_freq = np.nan

    return freq, amp, mean_freq, max_freq, cutoff_freq


def plot_fft(freq, amp, cutoff_freq=None, thresh=10, max_display_freq=50):
    """
    Plot normalized FFT spectrum and suggested cutoff frequency.
    """

    amp_norm = amp / np.max(amp)

    plt.figure(figsize=(8, 4))
    plt.plot(freq, amp_norm, linewidth=1.5)

    if cutoff_freq is not None and not np.isnan(cutoff_freq):
        idx = np.argmin(np.abs(freq - cutoff_freq))
        plt.plot(cutoff_freq, amp_norm[idx], "r*", markersize=12)
        plt.axvline(cutoff_freq, linestyle="--")
        plt.text(
            cutoff_freq,
            amp_norm[idx],
            "  Cutoff = {:.2f} Hz".format(cutoff_freq),
            verticalalignment="bottom",
        )

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Normalized Amplitude")
    plt.title(
        "Single-Sided Amplitude Spectrum ({}% Threshold)".format(thresh)
    )
    plt.xlim([0, 300])
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":

    # ------- TESTING --------
    import os
    from biomechzoo.utils.zload import zload
    from biomechzoo.utils.find_repo_root import find_repo_root

    project_root = find_repo_root()

    fl = os.path.join(project_root, "data", "other", "acc_breast_jogging.zoo",)

    data = zload(fl)

    acc = np.asarray(
        data["highg_a_breast_vert"]["line"]
    )

    fs = data["zoosystem"]["Video"]["Freq"]

    freq, amp, mean_freq, max_freq, cutoff_freq = fft_analysis(
        acc,
        fs,
        thresh=10,
    )

    print(
        "Mean frequency: {:.2f} Hz".format(mean_freq)
    )
    print(
        "Dominant frequency: {:.2f} Hz".format(max_freq)
    )
    print(
        "Suggested cutoff frequency: {:.2f} Hz".format(
            cutoff_freq
        )
    )

    plot_fft(
        freq,
        amp,
        cutoff_freq=cutoff_freq,
        thresh=10,
    )