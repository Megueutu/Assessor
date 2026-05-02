from langchain.agents import create_agent
from app.core.llms import SPECIALIST_LLM

from app.prompt.agents.schedule import SCHEDULE_PROMPT

SCHEDULE_AGENT = create_agent(
    model=SPECIALIST_LLM,
    system_prompt=SCHEDULE_PROMPT,
)