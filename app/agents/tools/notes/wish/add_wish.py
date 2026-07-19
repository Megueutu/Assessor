from typing import Optional

from langchain.tools import tool

from app.agents.tools.financial.helpers import resolve_category_id
from app.agents.tools.notes.args import AddWishArgs
from app.agents.tools.response import ToolResponse
from app.core.database import get_cursor


@tool("add_wish", args_schema=AddWishArgs)
def add_wish(
    name: str,
    source_text: str,
    description: Optional[str] = None,
    category_name: Optional[str] = None,
    target_amount: Optional[float] = None,
    priority: Optional[int] = None,
) -> dict:
    """Adiciona um desejo de compra à lista de desejos."""
    try:
        with get_cursor() as (_, cur):
            category_id = resolve_category_id(cur, None, category_name) if category_name else None
            cur.execute(
                """INSERT INTO wishes
                   (name, description, category_id, target_amount, priority, source_text)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   RETURNING id, name, description, target_amount, priority, status, created_at""",
                (name.strip(), description, category_id, target_amount, priority, source_text),
            )
            row = cur.fetchone()
        return ToolResponse.ok(wish={
            "wish_id": row[0], "name": row[1], "description": row[2],
            "target_amount": float(row[3]) if row[3] is not None else None,
            "priority": row[4], "status": row[5], "created_at": row[6].isoformat(),
        })
    except Exception:
        return ToolResponse.error(message="Não foi possível adicionar o desejo.")
