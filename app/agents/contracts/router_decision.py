from pydantic import BaseModel
from typing import Literal

class RouterDecision(BaseModel):
    flow: Literal[
        "direct",
        "business",
        "faq"
        ]
    
    agents: list[Literal[
        "financial",
        "schedule",
        "notes",
        "faq"
    ]] = []

    answer: str | None = None