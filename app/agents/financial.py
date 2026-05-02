from langchain.agents import create_agent
from app.core.llms import SPECIALIST_LLM

from app.prompt.agents.financial import FINANCIAL_PROMPT
from app.tools.registry import FINANCIAL_TOOLS as TOOLS

FINANCIAL_AGENT = create_agent(
    model=SPECIALIST_LLM,
    system_prompt=FINANCIAL_PROMPT,
    tools=TOOLS,
)
