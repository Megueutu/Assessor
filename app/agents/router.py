from langchain.agents import create_agent
from app.core.llms    import FAST_LLM

from app.prompt.agents.router import ROUTER_PROMPT

ROUTER_AGENT = create_agent(
    model=FAST_LLM,
    system_prompt=ROUTER_PROMPT(),
)
