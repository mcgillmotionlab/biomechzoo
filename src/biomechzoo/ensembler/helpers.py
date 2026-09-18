import re
import warnings
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, NamedTuple, Optional, Tuple

import numpy as np
from scipy.stats import iqr

_NO_CONDITIONS = "__all__"


def match_condition(
        path: str, conditions: Optional[List[str]],
) -> Optional[str]:
    """
    Find which condition name appears (case-insensitively) in a path.

    Parameters
    ----------
    path : str
        File path to search.
    conditions : list of str or None
        Candidate condition names. If falsy, no condition matching is
        applied.

    Returns
    -------
    condition : str or None
        ``_NO_CONDITIONS`` ('__all__') if ``conditions`` is falsy, the
        matching condition name if one is found in ``path``, or None
        if no condition matches.
    """
    if not conditions:
        return _NO_CONDITIONS

    for cond in conditions:
        if cond.lower() in path.lower():
            return cond
    return None


def extract_subject_id(
        f: str, subj_list: Optional[List[str]],
        str_pattern: Optional[List[str]],
) -> Optional[str]:
    """
    Extract the subject ID from a zoo file path, matching either a
    regular expression or a known list of subject IDs.

    Parameters
    ----------
    f : str
        File path to the zoo file.
    subj_list : list of str
        List of subject IDs.
    str_pattern : list of str
        String pattern to match the subject IDs.

    Returns
    -------
    s : str or None
        Subject ID if found, otherwise None.
    """
    if str_pattern:
        for pattern in str_pattern:
            match = re.search(pattern, f)
            if match:
                return match.group(0)
    if subj_list:
        matched = [subj for subj in subj_list if subj in f]
        return matched[0] if matched else None

    return None


class ZooEvent(NamedTuple):
    x: float   # frame / time / % gait cycle
    y: float   # amplitude value


def extract_events(ch_data: Dict, event_name: str) -> Optional[ZooEvent]:
    """
    Extract the named event's (frame, value) scalars from a zoo channel.

    Parameters
    ----------
    ch_data : dict
        Zoo channel dictionary (with an 'event' key).
    event_name : str
        Name of the event to extract.

    Returns
    -------
    event : ZooEvent or None
        The event's (x, y) values, or None if not found, malformed,
        or flagged with the sentinel value 999.
    """
    try:
        x = ch_data["event"][event_name][0]
        y = ch_data["event"][event_name][1]
        if y == 999:
            return None
        return ZooEvent(x=x, y=y)
    except (KeyError, TypeError, ValueError):
        return None


def compute_ensemble(
        arrays: List[np.ndarray],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute time normalized mean and standard deviation for a list
    of arrays.

    Parameters
    ----------
    arrays : list of ndarray
        Time-normalized arrays (must all be the same length).

    Returns
    -------
    mean : ndarray
        Pointwise mean across ``arrays``.
    upper : ndarray
        ``mean + std``.
    lower : ndarray
        ``mean - std``.
    """

    stack = np.vstack(arrays)
    mean = np.nanmean(stack, axis=0)
    std = np.nanstd(stack, axis=0)
    upper = mean + std
    lower = mean - std

    return mean, upper, lower


class ConditionSource(Enum):
    """Enum defining condition sources."""
    BETWEEN = "folder" # Condition encoded in folder/filepath
    WITHIN = "channel" # Conditions encoded in channel name suffix/prefix


@dataclass
class ConditionSpec:
    """Describes how the conditions are encoded in the data"""
    source: ConditionSource
    conditions: list[str]       = field(default_factory=list)
    channel_map: dict[str, dict[str, str]] | None = None
    base_channels : list[str]    = field(default_factory=list)
    suffix_map : dict[str, str] | None = None

    def __post_init__(self) -> None:
        """Auto-build ``channel_map``/``conditions`` for WITHIN sources."""
        if self.source == ConditionSource.WITHIN:

            #auto built channel_map from suffix pattern if not provided
            if self.channel_map is None:
                if not self.suffix_map or not self.base_channels:
                    raise ValueError(
                        "ConditionSpec with WITHIN source require "
                        "either a channel_map or both suffix_map "
                        "and base_channels."
                    )
                self.channel_map = {
                    cond: {
                        base : f"{base}{suffix}"
                        for base in self.base_channels
                    }
                    for cond, suffix in self.suffix_map.items()
                }
            if not self.conditions:
                self.conditions = list(self.channel_map.keys())


def _compute_bandwidth(values: list[float]) -> float:
    """
    Silverman's rule of thumb — bandwidth scaled to data spread.

    More robust than Scott's rule when outliers are present.

    Parameters
    ----------
    values : list of float
        Sample values to compute a kernel-density bandwidth for.

    Returns
    -------
    bandwidth : float
        Estimated bandwidth.
    """
    arr = np.asarray(values)
    n=len(arr)
    std = np.std(arr, ddof=1)
    spread = min(std, iqr(arr) / 1.34)
    return 0.9 * spread * n ** (-1 / 5)


def align_by_subject(
        vals_a: list[float], subjects_a: list[str],
        vals_b: list[float], subjects_b: list[str],
) -> tuple[list[float], list[float], list[str]]:
    """
    Pair values from two conditions by matching subject IDs.

    When a subject has a different number of trials in each condition,
    only the first ``min(n_a, n_b)`` trials are paired (a warning is
    raised).

    Parameters
    ----------
    vals_a : list of float
        Values for condition A.
    subjects_a : list of str
        Subject ID for each entry in ``vals_a``.
    vals_b : list of float
        Values for condition B.
    subjects_b : list of str
        Subject ID for each entry in ``vals_b``.

    Returns
    -------
    aligned_a : list of float
        Paired values from condition A.
    aligned_b : list of float
        Paired values from condition B.
    aligned_s : list of str
        Subject ID for each paired entry.
    """
    idx_a: dict[str, list[int]] = defaultdict(list)
    idx_b: dict[str, list[int]] = defaultdict(list)

    for i, s in enumerate(subjects_a):
        idx_a[s].append(i)
    for i, s in enumerate(subjects_b):
        idx_b[s].append(i)

    # map_b = dict(zip(subjects_b, vals_b))
    aligned_a, aligned_b, aligned_s = [], [], []
    common_subject = [s for s in idx_a if s in idx_b]

    for subj in common_subject:
        trials_a = idx_a[subj]
        trials_b = idx_b[subj]

        n_a, n_b = len(trials_a), len(trials_b)
        if n_a != n_b:
            warnings.warn(
                f"Subject {subj!r} has {n_a} trials in condition A "
                f"and {n_b} in condition B. "
                f"Using first {min(n_a, n_b)} trials only."
            )

        for ia, ib in zip(trials_a, trials_b):
            aligned_a.append(vals_a[ia])
            aligned_b.append(vals_b[ib])
            aligned_s.append(subj)

    return aligned_a, aligned_b, aligned_s


def resolve_shade(color: str) -> str:
    """
    Convert a hex color to a translucent rgba string for shading.

    Parameters
    ----------
    color : str
        Hex color string (e.g. '#1f77b4').

    Returns
    -------
    shade_color : str
        ``rgba(...)`` string with opacity 0.2.
    """
    h = color.lstrip('#')
    rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    # shade color with opacity
    opacity = 0.2
    shade_color = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {opacity})"
    return shade_color