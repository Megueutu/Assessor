from langchain.agents import create_agent
from app.core.llms import SPECIALIST_LLM

from app.prompt.finantial import FINANTIAL_PROMPT_COMPLETED
from app.tools.finantial import TOOLS

FINANTIAL_AGENT = create_agent(
    model=SPECIALIST_LLM,
    system_prompt=FINANTIAL_PROMPT_COMPLETED,
    tools=TOOLS,
)
