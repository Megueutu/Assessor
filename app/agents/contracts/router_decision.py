from pydantic import BaseModel
from typing import Literal

from app.core.constants.flow import Flow

class RouterDecision(BaseModel):
    flow: Flow
    intent: dict[str, bool]
    answer: str | None = None