from langchain.tools import tool
from typing import Optional

from app.tools.response import ToolResponse
from app.tools.notes.args import ConcludeNoteArgs
from app.core.database import get_cursor

_SQL = """
UPDATE notes
SET concluded = %s, concluded_at = NOW()
WHERE id = %s
RETURNING *
"""

@tool("conclude_note", args_schema=ConcludeNoteArgs)
def conclude_note(note_id: int) -> dict:
    """Marca uma nota como concluída."""

    try:
        with get_cursor() as (_, cur):
            cur.execute(_SQL, (True, note_id))
            _SQL_RETURN = cur.fetchone()

        return ToolResponse.ok(message=f"Nota {note_id} marcada como concluída.", note=_SQL_RETURN)

    except Exception as e:
        return ToolResponse.error(message=f"Erro ao concluir nota no banco de dados: {e}")