from langchain.agents import create_agent
from core.llms import FAST_LLM

from prompt import ROUTER_PROMPT_COMPLETED
from core.memory import ROUTER_MEMORY

ROUTER_AGENT = create_agent(
    model=FAST_LLM,
    system_prompt=ROUTER_PROMPT_COMPLETED,
    checkpointer=ROUTER_MEMORY
)
