import numpy as np
import pandas as pd
from typing import Dict, List, Optional

def lineval_wide2arrays(
    df: pd.DataFrame,
    condition_col: str = 'condition',
    conditions: Optional[List[str]] = None
) -> Dict[str, np.ndarray]:
    """
    Convert a wide-format DataFrame into arrays grouped by condition.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame returned by `lineval(format='wide')`.
        Must include columns for condition and timepoints (p0...pN).
    condition_col : str
        Column name containing condition labels. Default 'condition'.
    conditions : list of str, optional
        List of condition labels in desired order.
        If None, will use all unique conditions sorted alphabetically.

    Returns
    -------
    Dict[str, np.ndarray]
        Keys = condition labels
        Values = 2D numpy arrays (n_trials x n_timepoints)
    """

    # Identify timepoint columns
    time_cols = [c for c in df.columns if c.startswith('p')]

    # Determine condition list
    if conditions is None:
        conditions = sorted(df[condition_col].unique())

    cond_arrays = {}

    for cond in conditions:
        group = df[df[condition_col] == cond]
        if group.empty:
            raise ValueError(f"Condition '{cond}' not found in DataFrame")
        cond_arrays[cond] = group[time_cols].to_numpy()

    return cond_arrays
