from langchain.agents import create_agent
from core.llms import FAST_LLM

from prompt import ORCHESTRATOR_PROMPT_COMPLETED

ORCHESTRATOR_AGENT = create_agent(
    model=FAST_LLM,
    system_prompt=ORCHESTRATOR_PROMPT_COMPLETED,
)