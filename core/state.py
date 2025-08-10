from enum import Enum
from dataclasses import dataclass
from typing import Optional


class AgentState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    EXECUTING = "executing"
    CONFIRMING = "confirming"
    SLEEPING = "sleeping"


@dataclass
class StateContext:
    current: AgentState = AgentState.IDLE
    last_error: Optional[str] = None

    def set(self, new_state: AgentState) -> None:
        self.current = new_state
        self.last_error = None
