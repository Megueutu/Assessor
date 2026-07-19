from typing import Optional

from langchain.tools import tool

from app.agents.tools.notes.args import FindMatchingWishesArgs
from app.agents.tools.response import ToolResponse
from app.core.database import get_cursor


@tool("find_matching_wishes", args_schema=FindMatchingWishesArgs)
def find_matching_wishes(search: str, category_name: Optional[str] = None, limit: int = 5) -> dict:
    """Encontra desejos ativos parecidos com uma compra, sem alterar dados."""
    try:
        with get_cursor() as (_, cur):
            sql = """
                SELECT w.id, w.name, w.description, c.name, w.target_amount, w.priority
                FROM wishes w
                LEFT JOIN categories c ON c.id = w.category_id
                WHERE w.status = 'ACTIVE'
                  AND (w.name ILIKE %s OR w.description ILIKE %s OR w.source_text ILIKE %s)
            """
            text_filter = f"%{search}%"
            params = [text_filter, text_filter, text_filter]
            if category_name:
                sql += " AND LOWER(c.name) = LOWER(%s)"
                params.append(category_name)
            sql += " ORDER BY w.priority DESC NULLS LAST, w.created_at DESC LIMIT %s"
            params.append(limit)
            cur.execute(sql, params)
            rows = cur.fetchall()
        return ToolResponse.ok(candidates=[{
            "wish_id": row[0], "name": row[1], "description": row[2], "category": row[3],
            "target_amount": float(row[4]) if row[4] is not None else None, "priority": row[5],
        } for row in rows], requires_confirmation=bool(rows))
    except Exception:
        return ToolResponse.error(message="Não foi possível procurar desejos relacionados.")
