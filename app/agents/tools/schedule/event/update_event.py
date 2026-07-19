from datetime import datetime
from typing import Optional

from langchain.tools import tool

from app.agents.tools.response import ToolResponse
from app.agents.tools.schedule.args import UpdateEventArgs
from app.agents.tools.schedule.helpers import find_conflicts, serialize_event
from app.core.database import get_cursor


_SQL_SELECT = """
SELECT id, title, start_time, end_time, location, notes, status, recorded_at, updated_at, cancelled_at
FROM events
WHERE id = %s AND status = 'ACTIVE'
"""


@tool("update_event", args_schema=UpdateEventArgs)
def update_event(
    event_id: int,
    title: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    location: Optional[str] = None,
    notes: Optional[str] = None,
) -> dict:
    """Atualiza um evento ativo e impede conflito no novo horário."""
    try:
        with get_cursor() as (_, cur):
            cur.execute(_SQL_SELECT, (event_id,))
            current = cur.fetchone()
            if not current:
                return ToolResponse.error(message="Evento inexistente ou não está ativo.")

            resulting_start = start_time or current[2]
            resulting_end = end_time if end_time is not None else current[3]
            if resulting_end is not None and resulting_end <= resulting_start:
                return ToolResponse.error(message="O fim do evento deve ser posterior ao início.")

            if start_time is not None or end_time is not None:
                conflicts = find_conflicts(cur, resulting_start, resulting_end, exclude_event_id=event_id)
                if conflicts:
                    return ToolResponse.custom(
                        status="conflict",
                        message="O novo horário conflita com outro evento.",
                        conflicts=[serialize_event(row) for row in conflicts],
                    )

            fields = []
            params = []
            for column, value in (
                ("title", title.strip() if title else None),
                ("start_time", start_time),
                ("end_time", end_time),
                ("location", location),
                ("notes", notes),
            ):
                if value is not None:
                    fields.append(f"{column} = %s")
                    params.append(value)
            fields.append("updated_at = NOW()")
            params.append(event_id)
            cur.execute(
                f"UPDATE events SET {', '.join(fields)} WHERE id = %s AND status = 'ACTIVE' "
                "RETURNING id, title, start_time, end_time, location, notes, status, recorded_at, updated_at, cancelled_at",
                params,
            )
            event = cur.fetchone()
        return ToolResponse.ok(event=serialize_event(event))
    except Exception:
        return ToolResponse.error(message="Não foi possível atualizar o evento.")
