from langchain.agents import create_agent
from app.core.llms import SPECIALIST_LLM

from app.prompt.agents.notes import NOTES_PROMPT
from app.tools.registry import NOTES_TOOLS as TOOLS

NOTES_AGENT = create_agent(
    model=SPECIALIST_LLM,
    system_prompt=NOTES_PROMPT,
    tools=TOOLS,
)
