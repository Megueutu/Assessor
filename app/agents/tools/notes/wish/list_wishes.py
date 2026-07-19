from typing import Optional

from langchain.tools import tool

from app.agents.tools.notes.args import ListWishesArgs, WishStatus
from app.agents.tools.response import ToolResponse
from app.core.database import get_cursor


_SQL_BASE = """
SELECT w.id, w.name, w.description, c.name, w.target_amount, w.priority,
       w.status, w.fulfilled_transaction_id, w.source_text, w.created_at,
       w.updated_at, w.fulfilled_at
FROM wishes w
LEFT JOIN categories c ON c.id = w.category_id
WHERE 1=1
"""


def serialize_wish(row):
    return {
        "wish_id": row[0], "name": row[1], "description": row[2], "category": row[3],
        "target_amount": float(row[4]) if row[4] is not None else None,
        "priority": row[5], "status": row[6], "fulfilled_transaction_id": row[7],
        "source_text": row[8], "created_at": row[9].isoformat(),
        "updated_at": row[10].isoformat(),
        "fulfilled_at": row[11].isoformat() if row[11] else None,
    }


@tool("list_wishes", args_schema=ListWishesArgs)
def list_wishes(
    wish_id: Optional[int] = None,
    search: Optional[str] = None,
    status: Optional[WishStatus] = None,
    category_name: Optional[str] = None,
    limit: int = 20,
) -> dict:
    """Lista desejos com filtros opcionais."""
    try:
        with get_cursor() as (_, cur):
            sql = _SQL_BASE
            params = []
            if wish_id:
                sql += " AND w.id = %s"
                params.append(wish_id)
            if search:
                sql += " AND (w.name ILIKE %s OR w.description ILIKE %s OR w.source_text ILIKE %s)"
                text_filter = f"%{search}%"
                params.extend([text_filter, text_filter, text_filter])
            if status:
                sql += " AND w.status = %s"
                params.append(status)
            if category_name:
                sql += " AND LOWER(c.name) = LOWER(%s)"
                params.append(category_name)
            sql += " ORDER BY w.created_at DESC LIMIT %s"
            params.append(limit)
            cur.execute(sql, params)
            rows = cur.fetchall()
        if wish_id and not rows:
            return ToolResponse.error(message="Nenhum desejo encontrado com o ID fornecido.")
        return ToolResponse.ok(wishes=[serialize_wish(row) for row in rows], total=len(rows))
    except Exception:
        return ToolResponse.error(message="Não foi possível consultar os desejos.")
