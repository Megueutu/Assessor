from langchain.agents import create_agent
from app.core.llms import FAST_LLM

from app.prompt.agents.specialist.faq import FAQ_PROMPT
from app.tools.registry import FAQ_TOOLS as TOOLS

FAQ_AGENT = create_agent(
    model=FAST_LLM,
    system_prompt=FAQ_PROMPT(),
    tools=TOOLS,
)