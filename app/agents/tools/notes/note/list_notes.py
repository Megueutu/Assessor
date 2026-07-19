from typing import Optional

from langchain.tools import tool

from app.agents.tools.notes.args import ListNotesArgs, NoteStatus
from app.agents.tools.response import ToolResponse
from app.core.database import get_cursor


_SQL_BASE = """
SELECT n.id, n.title, n.source_text, n.content, c.name, n.status,
       n.recorded_at, n.updated_at, n.concluded_at
FROM notes n
LEFT JOIN categories c ON c.id = n.category_id
WHERE 1=1
"""

_SQL_ITEMS = """
SELECT id, content, position, is_completed, completed_at
FROM note_items
WHERE note_id = %s
ORDER BY position, id
"""


def _serialize_note(row, items):
    return {
        "note_id": row[0],
        "title": row[1],
        "source_text": row[2],
        "content": row[3],
        "category": row[4],
        "status": row[5],
        "recorded_at": row[6].isoformat(),
        "updated_at": row[7].isoformat(),
        "concluded_at": row[8].isoformat() if row[8] else None,
        "items": [
            {
                "item_id": item[0],
                "content": item[1],
                "position": item[2],
                "is_completed": item[3],
                "completed_at": item[4].isoformat() if item[4] else None,
            }
            for item in items
        ],
    }


@tool("list_notes", args_schema=ListNotesArgs)
def list_notes(
    note_id: Optional[int] = None,
    content: Optional[str] = None,
    items: Optional[list[str]] = None,
    status: Optional[NoteStatus] = None,
    category_name: Optional[str] = None,
    limit: int = 20,
) -> dict:
    """Lista anotações e checklists usando filtros opcionais."""
    try:
        with get_cursor() as (_, cur):
            sql = _SQL_BASE
            params = []

            if note_id:
                sql += " AND n.id = %s"
                params.append(note_id)
            if content:
                sql += " AND (n.title ILIKE %s OR n.source_text ILIKE %s OR n.content ILIKE %s)"
                text_filter = f"%{content}%"
                params.extend([text_filter, text_filter, text_filter])
            if status:
                sql += " AND n.status = %s"
                params.append(status)
            if category_name:
                sql += " AND LOWER(c.name) = LOWER(%s)"
                params.append(category_name)
            for item in items or []:
                sql += " AND EXISTS (SELECT 1 FROM note_items ni WHERE ni.note_id = n.id AND ni.content ILIKE %s)"
                params.append(f"%{item}%")

            sql += " ORDER BY n.recorded_at DESC LIMIT %s"
            params.append(limit)
            cur.execute(sql, params)
            rows = cur.fetchall()

            notes = []
            for row in rows:
                cur.execute(_SQL_ITEMS, (row[0],))
                notes.append(_serialize_note(row, cur.fetchall()))

        if note_id and not notes:
            return ToolResponse.error(message="Nenhuma anotação encontrada com o ID fornecido.")
        return ToolResponse.ok(notes=notes, total=len(notes))
    except Exception:
        return ToolResponse.error(message="Não foi possível consultar as anotações.")
