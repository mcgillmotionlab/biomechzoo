from dataclasses import dataclass, field
from typing import List, Optional

from biomechzoo.ensembler.renderers import Renderer


@dataclass
class PlotSpec:
    channel: str
    condition: Optional[str] = None
    row: int = 1
    col: int  = 1
    renderer: Optional[Renderer] = None
    events: list[str] = field(default_factory=list)  # ← e.g. ["max", "min"]
    companions: list[str] = field(default_factory=list)  # ← other condition
    # ← second-channel for intra-file comparison
    companion_channel: str | None = None
    group_by: str | None = None  # ← e.g. "sex", "age_group"
    # ← {"P01": "male", "P02": "female"}
    group_map: dict[str, str] | None = None
    title: str = ""
    x_label: str = ""
    y_label: str = ""

    def __post_init__(self) -> None:
        """Default ``title`` to the channel name when not provided."""
        if not self.title:
            self.title = f"{self.channel}"

    @property
    def all_conditions(self) -> List[Optional[str]]:
        """list of str or None: ``condition`` followed by ``companions``."""
        return [self.condition] + self.companions