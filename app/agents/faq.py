from langchain.agents import create_agent
from core.llms import FAST_LLM

from prompt import FAQ_PROMPT_COMPLETED
from tools.faq import TOOLS

FAQ_AGENT = create_agent(
    model=FAST_LLM,
    system_prompt=FAQ_PROMPT_COMPLETED,
    tools=TOOLS,
)