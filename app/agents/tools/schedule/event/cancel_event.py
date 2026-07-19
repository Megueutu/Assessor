from langchain.tools import tool

from app.agents.tools.response import ToolResponse
from app.agents.tools.schedule.args import CancelEventArgs
from app.agents.tools.schedule.helpers import serialize_event
from app.core.database import get_cursor


@tool("cancel_event", args_schema=CancelEventArgs)
def cancel_event(event_id: int) -> dict:
    """Cancela um evento ativo sem removê-lo do histórico."""
    try:
        with get_cursor() as (_, cur):
            cur.execute(
                """UPDATE events
                   SET status = 'CANCELLED', updated_at = NOW(), cancelled_at = NOW()
                   WHERE id = %s AND status = 'ACTIVE'
                   RETURNING id, title, start_time, end_time, location, notes, status,
                             recorded_at, updated_at, cancelled_at""",
                (event_id,),
            )
            event = cur.fetchone()
        if not event:
            return ToolResponse.error(message="Evento inexistente ou não está ativo.")
        return ToolResponse.ok(event=serialize_event(event))
    except Exception:
        return ToolResponse.error(message="Não foi possível cancelar o evento.")
