from app.agents.schedule  import SCHEDULE_AGENT
from app.agents.financial import FINANCIAL_AGENT
from app.agents.faq   import FAQ_AGENT
from app.agents.notes import NOTES_AGENT

SPECIALIST_AGENTS = {
    "financial": FINANCIAL_AGENT,
    "schedule":  SCHEDULE_AGENT,
    "faq":       FAQ_AGENT,
    "notes":     NOTES_AGENT,
}