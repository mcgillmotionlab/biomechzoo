import plotly.colors as pc



class StyleContext:
    """
    Owns all color/dash assignments and legend deduplication state.
    Shared across the entire figure built so assignments are consistent
    """

    _SUBJECT_COLORS = pc.qualitative.D3
    _CONDITION_COLORS = pc.qualitative.D3
    _CONDITION_DASHES = ["solid", "dash", "dot", "dashdot"]
    # _CONDITION_DASHES = ["solid"]

    def __init__(self, subjects , conditions):
        """
        Parameters
        ----------
        subjects : list[str]
        conditions : list[str]
        """
        conditions = conditions or []
        self._subj_color = {
            s: self._SUBJECT_COLORS[i % len(self._SUBJECT_COLORS)] for i, s in enumerate(subjects)
        }
        self._cond_color = {
            c : self._CONDITION_COLORS[i % len(self._CONDITION_COLORS)] for i, c in enumerate(conditions)
        }
        self._cond_dash = {
            c: self._CONDITION_DASHES[i % len(self._CONDITION_DASHES)] for i, c in enumerate(conditions)
        }
        self._legend_seen: set[str] = set()

    def subject_color(self, subject : str): return self._subj_color.get(subject, "#333")
    def condition_color(self, condition: str) -> str: return self._cond_color.get(condition, "#333")
    def condition_dash(self, condition: str) -> str: return self._cond_dash.get(condition, "solid")

    def should_show_legend(self, namespace, key):
        """Returns True the first time (namespace, key) is seen,then False"""
        token = f"{namespace}::{key}"
        if token in self._legend_seen:
            return False
        self._legend_seen.add(token)
        return True
