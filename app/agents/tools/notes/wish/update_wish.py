from typing import Optional

from langchain.tools import tool

from app.agents.tools.financial.helpers import resolve_category_id
from app.agents.tools.notes.args import UpdateWishArgs
from app.agents.tools.response import ToolResponse
from app.core.database import get_cursor


@tool("update_wish", args_schema=UpdateWishArgs)
def update_wish(
    wish_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    category_name: Optional[str] = None,
    target_amount: Optional[float] = None,
    priority: Optional[int] = None,
) -> dict:
    """Atualiza um desejo ativo."""
    if all(value is None for value in (name, description, category_name, target_amount, priority)):
        return ToolResponse.error(message="Nenhum campo para atualização foi fornecido.")
    try:
        with get_cursor() as (_, cur):
            fields = []
            params = []
            for column, value in (("name", name), ("description", description), ("target_amount", target_amount), ("priority", priority)):
                if value is not None:
                    fields.append(f"{column} = %s")
                    params.append(value)
            if category_name is not None:
                fields.append("category_id = %s")
                params.append(resolve_category_id(cur, None, category_name))
            fields.append("updated_at = NOW()")
            params.append(wish_id)
            cur.execute(
                f"UPDATE wishes SET {', '.join(fields)} WHERE id = %s AND status = 'ACTIVE' RETURNING id, name, status, updated_at",
                params,
            )
            row = cur.fetchone()
        if not row:
            return ToolResponse.error(message="Desejo inexistente ou não está ativo.")
        return ToolResponse.ok(wish={"wish_id": row[0], "name": row[1], "status": row[2], "updated_at": row[3].isoformat()})
    except Exception:
        return ToolResponse.error(message="Não foi possível atualizar o desejo.")
