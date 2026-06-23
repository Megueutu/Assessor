from langchain_core.messages import SystemMessage
from langchain.agents import create_agent
from app.core.llms import FAST_LLM

from app.core.llms import SPECIALIST_LLM
from app.agents.tools.registry import NOTES_TOOLS
from app.agents.tools.registry import FINANCIAL_TOOLS
from app.agents.tools.registry import FAQ_TOOLS

from app.agents.prompt.coordinator.orchestrator import ORCHESTRATOR_PROMPT
from app.agents.prompt.specialist.notes import NOTES_PROMPT
from app.agents.prompt.specialist.schedule import SCHEDULE_PROMPT
from app.agents.prompt.specialist.financial import FINANCIAL_PROMPT
from app.agents.prompt.specialist.faq import FAQ_PROMPT
from app.agents.prompt.coordinator.router import ROUTER_PROMPT
from app.agents.prompt.utils.summary import SUMMARY_PROMPT

from app.agents.contracts.router_decision import RouterDecision


ORCHESTRATOR_AGENT = create_agent(
    model=FAST_LLM,
    system_prompt=ORCHESTRATOR_PROMPT(),
)

NOTES_AGENT = create_agent(
    model=SPECIALIST_LLM,
    system_prompt=NOTES_PROMPT(),
    tools=NOTES_TOOLS,
)

SCHEDULE_AGENT = create_agent(
    model=SPECIALIST_LLM,
    system_prompt=SCHEDULE_PROMPT(),
)

FINANCIAL_AGENT = create_agent(
    model=SPECIALIST_LLM,
    system_prompt=FINANCIAL_PROMPT(),
    tools=FINANCIAL_TOOLS,
)

FAQ_AGENT = create_agent(
    model=FAST_LLM,
    system_prompt=FAQ_PROMPT(),
    tools=FAQ_TOOLS,
)

SUMMARY_AGENT = create_agent(
    model=FAST_LLM,
    system_prompt=SUMMARY_PROMPT()
)

ROUTER_MODEL = FAST_LLM.with_structured_output(RouterDecision)


def ROUTER_DECISION(messages) -> dict:
    return ROUTER_MODEL.invoke([
        SystemMessage(content=ROUTER_PROMPT()),
        *messages
])


def SUMMARY_CHAT(messages: list[dict]) -> str:
    convo = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
    return SUMMARY_AGENT.invoke({"conversa": convo}).content.strip()


AGENTS = {
    "financial": FINANCIAL_AGENT,
    "schedule":  SCHEDULE_AGENT,
    "faq":       FAQ_AGENT,
    "notes":     NOTES_AGENT,
    "orchestrator": ORCHESTRATOR_AGENT,
    "summary": SUMMARY_AGENT
}


DEFS = {
    "router": ROUTER_DECISION,
    "summary": SUMMARY_CHAT
}