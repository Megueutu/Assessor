from langchain.tools import tool

from app.agents.tools.notes.args import CancelWishArgs
from app.agents.tools.response import ToolResponse
from app.core.database import get_cursor


@tool("cancel_wish", args_schema=CancelWishArgs)
def cancel_wish(wish_id: int) -> dict:
    """Cancela um desejo ativo sem removê-lo do histórico."""
    try:
        with get_cursor() as (_, cur):
            cur.execute(
                """UPDATE wishes SET status = 'CANCELLED', updated_at = NOW()
                   WHERE id = %s AND status = 'ACTIVE'
                   RETURNING id, name, status, updated_at""",
                (wish_id,),
            )
            row = cur.fetchone()
        if not row:
            return ToolResponse.error(message="Desejo inexistente ou não está ativo.")
        return ToolResponse.ok(wish={"wish_id": row[0], "name": row[1], "status": row[2], "updated_at": row[3].isoformat()})
    except Exception:
        return ToolResponse.error(message="Não foi possível cancelar o desejo.")
