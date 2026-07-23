from enum import Enum

class Agent(str, Enum):
    ROUTER = "router"
    ORCHESTRATOR = "orchestrator"
    FINANCIAL = "financial"
    SCHEDULE = "schedule"
    NOTES = "notes"
    FAQ = "faq"
    EDUCATION = "education"
    EXCHANGE = "exchange"
    SUMMARY = "summary"
    GUARDRAIL_IN = "guardrail_in"
    GUARDRAIL_OUT = "guardrail_out"
