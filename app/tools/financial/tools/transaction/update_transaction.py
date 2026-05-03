from langchain.tools import tool
from typing import Optional

from app.core.database import get_cursor
from app.tools.financial.args import UpdateTransactionArgs
from app.tools.financial.helpers import local_date_filter_sql, resolve_type_id, get_category_id
from app.tools.response import ToolResponse


_SQL_FIND_BY_TEXT_AND_DATE = f"""
    SELECT id FROM transactions t
    WHERE (t.source_text ILIKE %s OR t.description ILIKE %s)
    AND {local_date_filter_sql("t.occurred_at")}
    ORDER BY t.occurred_at DESC
    LIMIT 1
"""

_SQL_SELECT_UPDATED = """
    SELECT
        t.id, t.occurred_at, t.amount, tt.type,
        c.name, t.description, t.payment_method, t.source_text
    FROM transactions t
    JOIN transaction_types tt ON tt.id = t.type
    LEFT JOIN categories c ON c.id = t.category_id
    WHERE t.id = %s
"""

_UPDATABLE_FIELDS = {
    "amount":         "amount = %s",
    "resolved_type":  "type = %s",
    "resolved_cat":   "category_id = %s",
    "description":    "description = %s",
    "payment_method": "payment_method = %s",
    "occurred_at":    "occurred_at = %s::timestamptz",
}


@tool("update_transaction", args_schema=UpdateTransactionArgs)
def update_transaction(
    id:             Optional[int]   = None,
    match_text:     Optional[str]   = None,
    date_local:     Optional[str]   = None,
    amount:         Optional[float] = None,
    type_id:        Optional[int]   = None,
    type_name:      Optional[str]   = None,
    category_id:    Optional[int]   = None,
    category_name:  Optional[str]   = None,
    description:    Optional[str]   = None,
    payment_method: Optional[str]   = None,
    occurred_at:    Optional[str]   = None,
) -> dict:
    """Atualiza uma transação existente por ID ou por texto + data."""

    try:
        with get_cursor() as (_, cur):
            target_id = id
            if target_id is None:
                if not match_text or not date_local:
                    return ToolResponse.error("Sem 'id': informe match_text E date_local para localizar o registro.")

                cur.execute(_SQL_FIND_BY_TEXT_AND_DATE, (f"%{match_text}%", f"%{match_text}%", date_local))
                row = cur.fetchone()
                if not row:
                    return ToolResponse.error("Nenhuma transação encontrada para os filtros fornecidos.")
                target_id = row[0]

            resolved_type = resolve_type_id(cur, type_id, type_name) if (type_id or type_name) else None
            resolved_cat  = get_category_id(cur, category_name) if (category_name and not category_id) else category_id

            updates = {
                "amount":         amount,
                "resolved_type":  resolved_type,
                "resolved_cat":   resolved_cat,
                "description":    description,
                "payment_method": payment_method,
                "occurred_at":    occurred_at,
            }

            sets   = [_UPDATABLE_FIELDS[k] for k, v in updates.items() if v is not None]
            params = [v for v in updates.values() if v is not None]

            if not sets:
                return ToolResponse.error("Nada para atualizar: forneça pelo menos um campo.")

            cur.execute(
                f"UPDATE transactions SET {', '.join(sets)} WHERE id = %s",
                (*params, target_id)
            )
            rows_affected = cur.rowcount

            cur.execute(_SQL_SELECT_UPDATED, (target_id,))
            r = cur.fetchone()

        return ToolResponse.ok(
            rows_affected=rows_affected,
            updated={
                "id":             r[0],
                "occurred_at":    r[1].isoformat(),
                "amount":         float(r[2]),
                "type":           r[3],
                "category":       r[4],
                "description":    r[5],
                "payment_method": r[6],
                "source_text":    r[7],
            } if r else None
        )

    except Exception as e:
        return ToolResponse.error(message=str(e))