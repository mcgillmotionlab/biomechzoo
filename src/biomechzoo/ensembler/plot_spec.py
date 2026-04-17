from dataclasses import dataclass, field

from src.renderers import Renderer


@dataclass
class PlotSpec:
    channel: str
    condition: str = None
    row: int = 1
    col: int  = 1
    renderer: Renderer = None
    events:    list[str] = field(default_factory=list)  # ← e.g. ["max", "min"]
    companions: list[str] = field(default_factory=list) # ← other condition
    group_by: str | None = None                         # ← e.g. "sex", "age_group"
    group_map: dict[str, str] | None = None             # ← {"P01": "male", "P02": "female"}
    title: str = ""
    x_label: str = ""
    y_label: str = ""

    def __post_init__(self):
        if not self.title:
            self.title = f"{self.channel}"

    @property
    def all_conditions(self):
        return [self.condition] + self.companions