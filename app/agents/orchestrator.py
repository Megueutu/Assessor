from langchain.agents import create_agent
from app.core.llms import FAST_LLM

from app.prompt.orchestrator import ORCHESTRATOR_PROMPT_COMPLETED

ORCHESTRATOR_AGENT = create_agent(
    model=FAST_LLM,
    system_prompt=ORCHESTRATOR_PROMPT_COMPLETED,
)