from langchain_core.tools import tool
from typing import Optional

from app.core.database import get_cursor
from app.tools.financial.args import QueryTransactionsArgs
from app.tools.financial.helpers import resolve_category_id, resolve_type_id
from app.tools.response import ToolResponse


_SQL_BASE = """
    SELECT t.amount, tt.type, c.name, t.description, t.occurred_at
    FROM transactions t
    JOIN transaction_types tt ON t.type = tt.id
    LEFT JOIN categories c ON t.category_id = c.id
    WHERE 1=1
"""
_SQL_FILTER_TYPE     = " AND t.type = %(id_tipo)s"
_SQL_FILTER_CATEGORY = " AND t.category_id = %(id_cat)s"
_SQL_FILTER_TEXT     = " AND (t.source_text ILIKE %(texto)s OR t.description ILIKE %(texto)s)"
_SQL_FILTER_FROM     = " AND (t.occurred_at AT TIME ZONE 'UTC' AT TIME ZONE 'America/Sao_Paulo') >= %(inicio)s"
_SQL_FILTER_TO       = " AND (t.occurred_at AT TIME ZONE 'UTC' AT TIME ZONE 'America/Sao_Paulo') <= %(fim)s::date + interval '1 day' - interval '1 second'"
_SQL_ORDER           = " ORDER BY t.occurred_at DESC LIMIT 20"


@tool("query_transactions", args_schema=QueryTransactionsArgs)
def query_transactions(
    source_text:     Optional[str] = None,
    date_from_local: Optional[str] = None,
    date_to_local:   Optional[str] = None,
    type_name:       Optional[str] = None,
    category_name:   Optional[str] = None,
) -> dict:
    """Consulta transações com filtros por texto, tipo e datas locais (America/Sao_Paulo)."""

    try:
        with get_cursor() as (_, cur):
            resolved_type_id     = resolve_type_id(cur, None, type_name) if type_name else None
            resolved_category_id = resolve_category_id(cur, None, category_name) if category_name else None

            sql     = _SQL_BASE
            filters = {}

            if resolved_type_id:
                sql += _SQL_FILTER_TYPE
                filters["id_tipo"] = resolved_type_id

            if resolved_category_id:
                sql += _SQL_FILTER_CATEGORY
                filters["id_cat"] = resolved_category_id

            if source_text:
                sql += _SQL_FILTER_TEXT
                filters["texto"] = f"%{source_text}%"

            if date_from_local:
                sql += _SQL_FILTER_FROM
                filters["inicio"] = date_from_local

            if date_to_local:
                sql += _SQL_FILTER_TO
                filters["fim"] = date_to_local

            sql += _SQL_ORDER
            cur.execute(sql, filters)
            rows = cur.fetchall()

        return ToolResponse.ok(
            resultados=[
                {
                    "value":       float(row[0]),
                    "type":        row[1],
                    "category":    row[2],
                    "description": row[3],
                    "date":        row[4].isoformat(),
                }
                for row in rows
            ]
        )

    except Exception as e:
        return ToolResponse.error(message=str(e))