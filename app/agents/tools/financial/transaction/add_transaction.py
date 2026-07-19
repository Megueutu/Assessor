from langchain.tools import tool
from typing import Optional

from app.core.database  import get_cursor
from app.agents.tools.response import ToolResponse
from app.agents.tools.financial.args    import AddTransactionArgs
from app.agents.tools.financial.helpers import resolve_category_id, resolve_type_id


_SQL_INSERT = """
    INSERT INTO transactions
        (amount, type, category_id, description, payment_method, occurred_at, source_text)
    VALUES
        (%s, %s, %s, %s, %s, COALESCE(%s::timestamptz, NOW()), %s)
    RETURNING id, occurred_at
"""


@tool("add_transaction", args_schema=AddTransactionArgs)
def add_transaction(
    amount:         float,
    source_text:    str,
    occurred_at:    Optional[str] = None,
    type_id:        Optional[int] = None,
    type_name:      Optional[str] = None,
    category_id:    Optional[int] = None,
    category_name:  Optional[str] = None,
    description:    Optional[str] = None,
    payment_method: Optional[str] = None,
) -> dict:
    """Insere uma transação financeira no banco."""

    try:
        with get_cursor() as (_, cur):
            resolved_type_id     = resolve_type_id(cur, type_id, type_name)
            resolved_category_id = resolve_category_id(cur, category_id, category_name)

            if not resolved_type_id:
                return ToolResponse.error("Tipo inválido. Use INCOME, EXPENSES ou TRANSFER.")

            cur.execute(_SQL_INSERT, (
                amount,
                resolved_type_id,
                resolved_category_id,
                description,
                payment_method,
                occurred_at,
                source_text,
            ))

            id, occurred_at = cur.fetchone()

        return ToolResponse.ok(
            id=id,
            occurred_at=occurred_at.isoformat()
        )

    except Exception:
        return ToolResponse.error(message="Não foi possível registrar a transação.")
