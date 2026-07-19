from datetime import datetime

from langchain.tools import tool

from app.agents.tools.response import ToolResponse
from app.agents.tools.schedule.args import CheckAvailabilityArgs
from app.agents.tools.schedule.helpers import find_conflicts, serialize_event
from app.core.database import get_cursor


@tool("check_availability", args_schema=CheckAvailabilityArgs)
def check_availability(start_time: datetime, end_time: datetime) -> dict:
    """Verifica se uma janela de tempo está livre na agenda."""
    try:
        with get_cursor() as (_, cur):
            conflicts = find_conflicts(cur, start_time, end_time)
        return ToolResponse.ok(
            available=not conflicts,
            conflicts=[serialize_event(row) for row in conflicts],
        )
    except Exception:
        return ToolResponse.error(message="Não foi possível consultar a disponibilidade.")
