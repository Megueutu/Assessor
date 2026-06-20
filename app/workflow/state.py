import operator
from typing import Annotated

from langgraph.graph import MessagesState

class GraphState(MessagesState):
    called: Annotated[list[str], operator.add]
    intent: Annotated[dict[str, bool], operator.or_]
    specialist_outputs: Annotated[list[str], operator.add]
    flow: str
    map_pii: dict
