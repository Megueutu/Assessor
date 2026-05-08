from langchain.tools import tool
from typing import Optional

from app.tools.response import ToolResponse
from app.tools.notes.args import UpdateNoteArgs
from app.core.database import get_cursor

_SQL_UPDATE_HEAD = """
UPDATE notes
SET
"""

_SQL_CONTENT = "content = %s"
_SQL_ITEMS   = "items = %s"
_SQL_STATE   = "concluded = %s, concluded_at = NOW()"

_SQL_UPDATE_TAIL = """
WHERE id = %s
RETURNING *
"""


@tool("update_note", args_schema=UpdateNoteArgs)
def update_note(
    note_id: int,
    content: Optional[str]       = None,
    items:   Optional[list[str]] = None,
    state:   Optional[bool]      = None
) -> dict:
    """Atualiza uma nota existente com base no ID e nos campos fornecidos."""

    if not any([content, items, state is not None]):
        return ToolResponse.error(message="Nenhum campo para atualização fornecido.")
    
    try:
        with get_cursor() as (_, cur):
            sql = _SQL_UPDATE_HEAD
            params = []
            
            if content:
                sql += _SQL_CONTENT + ", "
                params.append(content)
            
            if items is not None:
                sql += _SQL_ITEMS + ", "
                params.append(items)
            
            if state is not None:
                sql += _SQL_STATE + ", "
                params.append(state)
            
            sql = sql.rstrip(", ") + _SQL_UPDATE_TAIL
            params.append(note_id)
            
            cur.execute(sql, tuple(params))
            SQL_RETURN = cur.fetchone()
            
            if not SQL_RETURN:
                return ToolResponse.error(message="Nenhuma nota encontrada com o ID fornecido.")
            
            return ToolResponse.ok(note={
                "note_id":      SQL_RETURN[0],
                "source_text":  SQL_RETURN[1],
                "content":      SQL_RETURN[2],
                "items":        SQL_RETURN[3],
                "concluded":    SQL_RETURN[4],
                "recorded_at":  SQL_RETURN[5].isoformat(),
                "concluded_at": SQL_RETURN[6].isoformat() if SQL_RETURN[6] else None
            })
    
    except Exception as e:
        return ToolResponse.error(message=str(e))