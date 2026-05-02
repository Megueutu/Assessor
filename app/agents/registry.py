from .schedule import SCHEDULE_AGENT
from .financial import FINANCIAL_AGENT
from .faq import FAQ_AGENT

SPECIALIST_AGENTS = {
    "financeiro": FINANCIAL_AGENT,
    "agenda": SCHEDULE_AGENT,
    "faq": FAQ_AGENT,
}