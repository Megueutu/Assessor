from .router import ROUTER_AGENT
from .schedule import SCHEDULE_AGENT
from .finantial import FINANTIAL_AGENT
from .orchestrator import ORCHESTRATOR_AGENT
from .faq import FAQ_AGENT

DOER = {
    "financeiro": FINANTIAL_AGENT,
    "agenda": SCHEDULE_AGENT,
    "faq": FAQ_AGENT,
}