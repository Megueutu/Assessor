from langchain.agents import create_agent
from app.core.llms import FAST_LLM

from app.prompt.agents.orchestrator import ORCHESTRATOR_PROMPT

ORCHESTRATOR_AGENT = create_agent(
    model=FAST_LLM,
    system_prompt=ORCHESTRATOR_PROMPT,
)