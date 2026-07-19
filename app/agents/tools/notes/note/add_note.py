from typing import Optional

from langchain.tools import tool

from app.agents.tools.financial.helpers import resolve_category_id
from app.agents.tools.notes.args import AddNoteArgs
from app.agents.tools.response import ToolResponse
from app.core.database import get_cursor


_SQL_INSERT_NOTE = """
INSERT INTO notes (title, content, source_text, category_id)
VALUES (%s, %s, %s, %s)
RETURNING id, title, content, status, recorded_at
"""

_SQL_INSERT_ITEM = """
INSERT INTO note_items (note_id, content, position)
VALUES (%s, %s, %s)
RETURNING id, content, position, is_completed
"""


@tool("add_note", args_schema=AddNoteArgs)
def add_note(
    source_text: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    category_name: Optional[str] = None,
    items: Optional[list[str]] = None,
) -> dict:
    """Cria uma anotação ou checklist e seus itens."""
    try:
        with get_cursor() as (_, cur):
            category_id = resolve_category_id(cur, None, category_name) if category_name else None
            note_content = (content or source_text).strip()
            cur.execute(_SQL_INSERT_NOTE, (title, note_content, source_text, category_id))
            note = cur.fetchone()

            saved_items = []
            for position, item in enumerate(items or []):
                item_content = item.strip()
                if not item_content:
                    continue
                cur.execute(_SQL_INSERT_ITEM, (note[0], item_content, position))
                row = cur.fetchone()
                saved_items.append({
                    "item_id": row[0],
                    "content": row[1],
                    "position": row[2],
                    "is_completed": row[3],
                })

        return ToolResponse.ok(note={
            "note_id": note[0],
            "title": note[1],
            "content": note[2],
            "status": note[3],
            "recorded_at": note[4].isoformat(),
            "items": saved_items,
        })
    except Exception:
        return ToolResponse.error(message="Não foi possível salvar a anotação.")
