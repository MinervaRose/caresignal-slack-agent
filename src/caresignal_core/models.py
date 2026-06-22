from dataclasses import dataclass
from typing import Literal

Priority = Literal["high", "medium", "low"]
Action = Literal["Resolved", "Assign follow-up", "Needs context"]


@dataclass(frozen=True)
class CareSignal:
    kind: str
    priority: Priority
    user: str
    thread_id: str
    evidence: str
    why_it_matters: str
    next_kind_action: str
    suggested_action: Action = "Assign follow-up"
    rts_query: str | None = None
