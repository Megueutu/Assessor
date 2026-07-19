from typing import Optional

from langchain.tools import tool

from app.agents.tools.financial.args import PurchaseWishArgs
from app.agents.tools.financial.helpers import resolve_category_id, resolve_type_id
from app.agents.tools.response import ToolResponse
from app.core.database import get_cursor


@tool("purchase_wish", args_schema=PurchaseWishArgs)
def purchase_wish(
    wish_id: int,
    amount: float,
    source_text: str,
    confirmation: str,
    occurred_at: Optional[str] = None,
    category_name: Optional[str] = None,
    description: Optional[str] = None,
    payment_method: Optional[str] = None,
) -> dict:
    """Registra uma compra e realiza o desejo de forma atômica após confirmação explícita."""
    if confirmation != "CONFIRMO":
        return ToolResponse.error(message="A compra do desejo exige confirmação explícita.")
    try:
        with get_cursor() as (_, cur):
            cur.execute(
                "SELECT id, name, category_id FROM wishes WHERE id = %s AND status = 'ACTIVE' FOR UPDATE",
                (wish_id,),
            )
            wish = cur.fetchone()
            if not wish:
                return ToolResponse.error(message="Desejo inexistente ou não está ativo.")

            type_id = resolve_type_id(cur, None, "EXPENSES")
            category_id = resolve_category_id(cur, None, category_name) if category_name else wish[2]
            cur.execute(
                """INSERT INTO transactions
                   (amount, type, category_id, description, payment_method, occurred_at, source_text)
                   VALUES (%s, %s, %s, %s, %s, COALESCE(%s::timestamptz, NOW()), %s)
                   RETURNING id, occurred_at""",
                (amount, type_id, category_id, description or wish[1], payment_method, occurred_at, source_text),
            )
            transaction = cur.fetchone()
            cur.execute(
                """UPDATE wishes
                   SET status = 'PURCHASED', fulfilled_transaction_id = %s,
                       fulfilled_at = NOW(), updated_at = NOW()
                   WHERE id = %s AND status = 'ACTIVE'
                   RETURNING id, name, status, fulfilled_at""",
                (transaction[0], wish_id),
            )
            fulfilled_wish = cur.fetchone()

        return ToolResponse.ok(
            transaction={"transaction_id": transaction[0], "occurred_at": transaction[1].isoformat(), "amount": amount},
            wish={"wish_id": fulfilled_wish[0], "name": fulfilled_wish[1], "status": fulfilled_wish[2], "fulfilled_at": fulfilled_wish[3].isoformat()},
        )
    except Exception:
        return ToolResponse.error(message="Não foi possível registrar a compra e realizar o desejo.")
