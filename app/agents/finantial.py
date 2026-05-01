from langchain.agents import create_agent
from core.llms import SPECIALIST_LLM

from prompt import FINANTIAL_PROMPT_COMPLETED
from tools.finantial import TOOLS

FINANTIAL_AGENT = create_agent(
    model=SPECIALIST_LLM,
    system_prompt=FINANTIAL_PROMPT_COMPLETED,
    tools=TOOLS,
)
