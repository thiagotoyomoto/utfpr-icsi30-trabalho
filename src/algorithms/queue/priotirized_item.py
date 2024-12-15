from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class PrioritizedItem[P, T]:
    priority: P
    item: T = field(compare=False)

    def __iter__(self):
        return self.item.__iter__()