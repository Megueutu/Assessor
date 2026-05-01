from langchain.agents import create_agent
from app.core.llms import FAST_LLM

from app.prompt.faq import FAQ_PROMPT_COMPLETED
from app.tools.faq import TOOLS

FAQ_AGENT = create_agent(
    model=FAST_LLM,
    system_prompt=FAQ_PROMPT_COMPLETED,
    tools=TOOLS,
)