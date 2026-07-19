from datetime import datetime
from typing import Optional

from langchain.tools import tool

from app.agents.tools.response import ToolResponse
from app.agents.tools.schedule.args import EventStatus, ListEventsArgs
from app.agents.tools.schedule.helpers import serialize_event
from app.core.database import get_cursor


_SQL_BASE = """
SELECT id, title, start_time, end_time, location, notes, status, recorded_at, updated_at, cancelled_at
FROM events
WHERE 1=1
"""


@tool("list_events", args_schema=ListEventsArgs)
def list_events(
    event_id: Optional[int] = None,
    search: Optional[str] = None,
    start_from: Optional[datetime] = None,
    start_until: Optional[datetime] = None,
    status: Optional[EventStatus] = "ACTIVE",
    limit: int = 20,
) -> dict:
    """Lista eventos usando filtros opcionais."""
    try:
        sql = _SQL_BASE
        params = []
        if event_id is not None:
            sql += " AND id = %s"
            params.append(event_id)
        if search:
            sql += " AND (title ILIKE %s OR location ILIKE %s OR notes ILIKE %s OR source_text ILIKE %s)"
            text_filter = f"%{search}%"
            params.extend([text_filter] * 4)
        if start_from is not None:
            sql += " AND start_time >= %s"
            params.append(start_from)
        if start_until is not None:
            sql += " AND start_time < %s"
            params.append(start_until)
        if status is not None:
            sql += " AND status = %s"
            params.append(status)
        sql += " ORDER BY start_time ASC LIMIT %s"
        params.append(limit)

        with get_cursor() as (_, cur):
            cur.execute(sql, params)
            events = [serialize_event(row) for row in cur.fetchall()]

        if event_id is not None and not events:
            return ToolResponse.error(message="Nenhum evento encontrado com o ID fornecido.")
        return ToolResponse.ok(events=events, total=len(events))
    except Exception:
        return ToolResponse.error(message="Não foi possível consultar os eventos.")
