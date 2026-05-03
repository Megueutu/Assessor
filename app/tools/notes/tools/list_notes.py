

from langchain_core.tools import tool
from typing import Optional

from app.tools.response import ToolResponse
from app.tools.notes.args import ListNotesArgs
from app.core.database import get_cursor


_SQL_BY_ID = """
    SELECT id, source_text, content, items, concluded, recorded_at, concluded_at
    FROM notes
    WHERE id = %s
"""

_SQL_BASE         = "SELECT id, source_text, content, items, concluded, recorded_at, concluded_at FROM notes WHERE 1=1"
_SQL_FILTER_TEXT  = " AND (source_text ILIKE %s OR content ILIKE %s)"
_SQL_FILTER_STATE = " AND concluded = %s"
_SQL_FILTER_ITEMS = " AND %s = ANY(items)"
_SQL_ORDER        = " ORDER BY recorded_at DESC LIMIT %s"


@tool("list_notes", args_schema=ListNotesArgs)
def list_notes(
    note_id: Optional[int]       = None,
    content: Optional[str]       = None,
    itens:   Optional[list[str]] = None,
    state:   Optional[bool]      = None,
    limit:   Optional[int]       = 20
) -> dict:
    """Lista notas do usuário com base em filtros. Caso não haja filtros, lista todas as notas."""

    try:
        with get_cursor() as (_, cur):
            if note_id:
                cur.execute(_SQL_BY_ID, (note_id,))
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
            
            

            sql = _SQL_BASE
            params = []
            
            if content:
                sql += _SQL_FILTER_TEXT
                params.extend([f"%{content}%", f"%{content}%"])
            
            if state is not None:
                sql += _SQL_FILTER_STATE
                params.append(state)
                
            if itens:
                sql += _SQL_FILTER_ITEMS
                for item in itens:
                    sql += _SQL_FILTER_ITEMS
                    params.append(item)
                
            sql += _SQL_ORDER
            params.append(limit)
            
            cur.execute(sql, params)
            SQL_RETURN = cur.fetchall()
            if not SQL_RETURN:
                return ToolResponse.ok(message="Nenhuma nota encontrada.")
            
            return ToolResponse.ok(notes=[
                {
                    "note_id":      row[0],
                    "source_text":  row[1],
                    "content":      row[2],
                    "items":        row[3],
                    "concluded":    row[4],
                    "recorded_at":  row[5].isoformat(),
                    "concluded_at": row[6].isoformat() if row[6] else None
                }
                for row in SQL_RETURN
            ])

    except Exception as e:
        return ToolResponse.error(message=f"Erro ao listar notas no banco de dados: {e}")