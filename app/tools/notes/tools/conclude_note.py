from langchain_core.tools import tool
from typing import Optional

from app.tools.response import ToolResponse
from app.tools.notes.args import ConcludeNoteArgs
from app.core.database import get_cursor

_SQL = """
UPDATE notes
SET concluded = %s, concluded_at = NOW()
WHERE id = %s
"""

@tool("conclude_note", args_schema=ConcludeNoteArgs)
def conclude_note(note_id: int, items: Optional[list]) -> dict:
    """Marca uma nota como concluída e atualiza os itens, se fornecidos."""

    try:
        with get_cursor() as (_, cur):
            cur.execute(_SQL, (True, note_id))
            cur.fetchone()

        return ToolResponse.ok(message=f"Nota {note_id} marcada como concluída.")

    except Exception as e:
        return ToolResponse.error(message=f"Erro ao concluir nota no banco de dados: {e}")