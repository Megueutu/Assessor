from typing import Optional

from langchain.tools import tool

from app.agents.tools.financial.helpers import resolve_category_id
from app.agents.tools.notes.args import NoteStatus, UpdateNoteArgs
from app.agents.tools.response import ToolResponse
from app.core.database import get_cursor


@tool("update_note", args_schema=UpdateNoteArgs)
def update_note(
    note_id: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    category_name: Optional[str] = None,
    status: Optional[NoteStatus] = None,
) -> dict:
    """Atualiza os dados de uma anotação existente."""
    if all(value is None for value in (title, content, category_name, status)):
        return ToolResponse.error(message="Nenhum campo para atualização foi fornecido.")

    try:
        with get_cursor() as (_, cur):
            fields = []
            params = []
            if title is not None:
                fields.append("title = %s")
                params.append(title)
            if content is not None:
                fields.append("content = %s")
                params.append(content)
            if category_name is not None:
                fields.append("category_id = %s")
                params.append(resolve_category_id(cur, None, category_name))
            if status is not None:
                fields.extend([
                    "status = %s",
                    "concluded_at = CASE WHEN %s = 'COMPLETED' THEN COALESCE(concluded_at, NOW()) ELSE NULL END",
                ])
                params.extend([status, status])

            fields.append("updated_at = NOW()")
            params.append(note_id)
            cur.execute(
                f"UPDATE notes SET {', '.join(fields)} WHERE id = %s RETURNING id, title, content, status, updated_at, concluded_at",
                params,
            )
            row = cur.fetchone()

        if not row:
            return ToolResponse.error(message="Nenhuma anotação encontrada com o ID fornecido.")
        return ToolResponse.ok(note={
            "note_id": row[0],
            "title": row[1],
            "content": row[2],
            "status": row[3],
            "updated_at": row[4].isoformat(),
            "concluded_at": row[5].isoformat() if row[5] else None,
        })
    except Exception:
        return ToolResponse.error(message="Não foi possível atualizar a anotação.")
