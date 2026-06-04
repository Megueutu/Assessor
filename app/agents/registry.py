from app.agents.orchestrator import ORCHESTRATOR_AGENT
from app.agents.schedule  import SCHEDULE_AGENT
from app.agents.financial import FINANCIAL_AGENT
from app.agents.faq   import FAQ_AGENT
from app.agents.notes import NOTES_AGENT

AGENTS = {
    "financial": FINANCIAL_AGENT,
    "schedule":  SCHEDULE_AGENT,
    "faq":       FAQ_AGENT,
    "notes":     NOTES_AGENT,
    "router": ORCHESTRATOR_AGENT,
    "orchestrator": ORCHESTRATOR_AGENT,
}