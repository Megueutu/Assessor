from datetime import datetime
from typing import Optional

from langchain.tools import tool

from app.agents.tools.response import ToolResponse
from app.agents.tools.schedule.args import AddEventArgs
from app.agents.tools.schedule.helpers import find_conflicts, serialize_event
from app.core.database import get_cursor


_SQL_INSERT = """
INSERT INTO events (title, start_time, end_time, location, notes, source_text)
VALUES (%s, %s, %s, %s, %s, %s)
RETURNING id, title, start_time, end_time, location, notes, status, recorded_at, updated_at, cancelled_at
"""


@tool("add_event", args_schema=AddEventArgs)
def add_event(
    title: str,
    start_time: datetime,
    source_text: str,
    end_time: Optional[datetime] = None,
    location: Optional[str] = None,
    notes: Optional[str] = None,
) -> dict:
    """Cria um evento quando o intervalo solicitado está disponível."""
    try:
        with get_cursor() as (_, cur):
            conflicts = find_conflicts(cur, start_time, end_time)
            if conflicts:
                return ToolResponse.custom(
                    status="conflict",
                    message="O horário solicitado conflita com outro evento.",
                    conflicts=[serialize_event(row) for row in conflicts],
                )
            cur.execute(_SQL_INSERT, (title.strip(), start_time, end_time, location, notes, source_text))
            event = cur.fetchone()
        return ToolResponse.ok(event=serialize_event(event))
    except Exception:
        return ToolResponse.error(message="Não foi possível criar o evento.")
