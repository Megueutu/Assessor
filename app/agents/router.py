from langchain_core.messages import SystemMessage, HumanMessage
from app.core.llms import FAST_LLM

from app.prompt.agents.router import ROUTER_PROMPT
from app.agents.contracts.router_decision import RouterDecision


ROUTER_MODEL = FAST_LLM.with_structured_output(RouterDecision)

def ROUTER_DECISION(messages) -> dict:
    return ROUTER_MODEL.invoke([
        SystemMessage(content=ROUTER_PROMPT()),
        *messages
])