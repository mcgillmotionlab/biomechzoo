import numpy as np
from scipy.signal import find_peaks, butter, filtfilt

def imu_mcgrath(ch_line, fsamp, min_stance_t, is_filtered=False):
    """
    This function detects the steps based on the method of McGrath et al. (2012) https://doi.org/10.1007/s12283-012-0093-8
    in short, the first minimum after a local maximum is the heel strike. The local maxima are the mid-swing.
    Data should be filtered
    """

    if is_filtered:
        yd = ch_line
    else:
        # Butterworth filter
        order = 5
        Fc = 5
        Wn = Fc / (fsamp / 2)
        [b, a] = butter(order, Wn, btype='low')
        yd = filtfilt(b, a, ch_line)


    # Identify midswing peaks
    t1 = round(fsamp / 2)
    potential_midswing_ind, _ = find_peaks(yd, distance=t1)
    potential_midswing_mag = yd[potential_midswing_ind]

    # Thresholds for midswing
    th2 = 0.8 * np.mean(yd[yd > np.mean(yd)])
    mask = potential_midswing_mag >= th2
    potential_midswing_ind = potential_midswing_ind[mask]
    potential_midswing_mag = potential_midswing_mag[mask]

    th1 = 0.3 * potential_midswing_mag

    # Find minima
    minima_ind, _ = find_peaks(-yd)
    minima_mag = -yd[minima_ind]

    # Validate midswing peaks
    valid_inds = []
    for i in range(len(potential_midswing_ind) - 1, -1, -1):
        peak_idx = potential_midswing_ind[i]
        preceding_min = minima_ind[minima_ind < peak_idx]
        if preceding_min.size > 0:
            closest_min_idx = preceding_min[-1]
            pos = np.where(minima_ind == closest_min_idx)[0][0]
            if (potential_midswing_mag[i] - minima_mag[pos]) >= th1[i]:
                valid_inds.append(peak_idx)
    potential_midswing_ind = np.array(valid_inds)

    # Additional thresholds
    th3 = 0.8 * abs(np.mean(yd[yd < np.mean(yd)]))
    th4 = 0.8 * np.mean(yd[yd < np.mean(yd)])
    th5 = np.mean(yd)
    th6 = 2 * th3

    maxima_ind, _ = find_peaks(yd)
    maxima_mag = yd[maxima_ind]

    IC, TC = [], []
    t2 = round(1.5 * fsamp)

    # Loop through confirmed midswing peaks
    for step_idx in range(len(potential_midswing_ind) - 1, -1, -1):
        peak_idx = potential_midswing_ind[step_idx]

        # IC candidates (minima after midswing)
        end_idx = min(peak_idx + t2, len(yd))
        ic_candidates, _ = find_peaks(-yd[peak_idx:end_idx])
        ic_candidates = ic_candidates + peak_idx
        ic_mags = yd[ic_candidates]

        # Filter IC by threshold
        ic_candidates = ic_candidates[ic_mags < th5]
        ic_mags = ic_mags[ic_mags < th5]

        # Validate IC with preceding maxima
        for ic_idx in ic_candidates:
            preceding_max = maxima_ind[maxima_ind < ic_idx]
            if preceding_max.size > 0:
                closest_max_idx = preceding_max[-1]
                if yd[closest_max_idx] >= yd[ic_idx] + th3:
                    IC.append(ic_idx)
                    break

        # TC candidates (minima before midswing)
        start_idx = max(peak_idx - t2, 0)
        tc_candidates, _ = find_peaks(-yd[start_idx:peak_idx])
        tc_candidates = tc_candidates + start_idx
        tc_mags = yd[tc_candidates]

        # Filter TC by threshold
        tc_candidates = tc_candidates[tc_mags < th4]
        tc_mags = tc_mags[tc_mags < th4]

        # Validate TC with following maxima
        for tc_idx in tc_candidates:
            following_max = maxima_ind[maxima_ind > tc_idx]
            if following_max.size > 0:
                closest_max_idx = following_max[0]
                if yd[closest_max_idx] >= yd[tc_idx] + th6:
                    TC.append(tc_idx)
                    break

    # Crash handling
    IC, TC = crash_catch(int(min_stance_t * fsamp / 1000), IC, TC)

    return IC, TC

def crash_catch(min_stance_samples, IC, TC):
    # Ensure IC and TC arrays are same length and valid
    IC = np.array(IC)
    TC = np.array(TC)
    if len(IC) != len(TC):
        min_len = min(len(IC), len(TC))
        IC = IC[:min_len]
        TC = TC[:min_len]
    return IC, TC