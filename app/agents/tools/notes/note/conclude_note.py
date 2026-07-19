from langchain.tools import tool

from app.agents.tools.notes.args import ConcludeNoteArgs
from app.agents.tools.response import ToolResponse
from app.core.database import get_cursor


_SQL = """
UPDATE notes
SET status = 'COMPLETED', concluded_at = COALESCE(concluded_at, NOW()), updated_at = NOW()
WHERE id = %s AND status <> 'ARCHIVED'
RETURNING id, title, status, concluded_at
"""


@tool("conclude_note", args_schema=ConcludeNoteArgs)
def conclude_note(note_id: int) -> dict:
    """Marca uma anotação como concluída."""
    try:
        with get_cursor() as (_, cur):
            cur.execute(_SQL, (note_id,))
            row = cur.fetchone()
        if not row:
            return ToolResponse.error(message="Anotação inexistente ou arquivada.")
        return ToolResponse.ok(note={
            "note_id": row[0],
            "title": row[1],
            "status": row[2],
            "concluded_at": row[3].isoformat(),
        })
    except Exception:
        return ToolResponse.error(message="Não foi possível concluir a anotação.")
