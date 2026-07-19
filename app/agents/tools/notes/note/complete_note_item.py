from langchain.tools import tool

from app.agents.tools.notes.args import CompleteNoteItemArgs
from app.agents.tools.response import ToolResponse
from app.core.database import get_cursor


@tool("complete_note_item", args_schema=CompleteNoteItemArgs)
def complete_note_item(item_id: int) -> dict:
    """Marca um item de checklist como concluído."""
    try:
        with get_cursor() as (_, cur):
            cur.execute(
                """UPDATE note_items
                   SET is_completed = TRUE, completed_at = COALESCE(completed_at, NOW())
                   WHERE id = %s
                   RETURNING id, note_id, content, is_completed, completed_at""",
                (item_id,),
            )
            row = cur.fetchone()
        if not row:
            return ToolResponse.error(message="Nenhum item encontrado com o ID fornecido.")
        return ToolResponse.ok(item={
            "item_id": row[0],
            "note_id": row[1],
            "content": row[2],
            "is_completed": row[3],
            "completed_at": row[4].isoformat(),
        })
    except Exception:
        return ToolResponse.error(message="Não foi possível concluir o item.")
