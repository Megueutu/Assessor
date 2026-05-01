from langchain.agents import create_agent
from app.core.llms import FAST_LLM

from app.prompt.router import ROUTER_PROMPT_COMPLETED
from app.core.memory import ROUTER_MEMORY

ROUTER_AGENT = create_agent(
    model=FAST_LLM,
    system_prompt=ROUTER_PROMPT_COMPLETED,
    checkpointer=ROUTER_MEMORY
)
