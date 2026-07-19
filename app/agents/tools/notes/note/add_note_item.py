from langchain.tools import tool

from app.agents.tools.notes.args import AddNoteItemArgs
from app.agents.tools.response import ToolResponse
from app.core.database import get_cursor


@tool("add_note_item", args_schema=AddNoteItemArgs)
def add_note_item(note_id: int, content: str) -> dict:
    """Adiciona um item a um checklist existente."""
    try:
        with get_cursor() as (_, cur):
            cur.execute("SELECT 1 FROM notes WHERE id = %s AND status = 'ACTIVE'", (note_id,))
            if not cur.fetchone():
                return ToolResponse.error(message="Anotação inexistente ou não está ativa.")
            cur.execute(
                """INSERT INTO note_items (note_id, content, position)
                   VALUES (%s, %s, (SELECT COALESCE(MAX(position), -1) + 1 FROM note_items WHERE note_id = %s))
                   RETURNING id, content, position, is_completed""",
                (note_id, content.strip(), note_id),
            )
            row = cur.fetchone()
        return ToolResponse.ok(item={"item_id": row[0], "content": row[1], "position": row[2], "is_completed": row[3]})
    except Exception:
        return ToolResponse.error(message="Não foi possível adicionar o item.")
