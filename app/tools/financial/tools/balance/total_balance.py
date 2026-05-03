from langchain_core.tools import tool

from app.core.database import get_cursor
from app.tools.response import ToolResponse


_SQL = """
SELECT
    SUM(CASE WHEN type = 1 THEN amount ELSE 0 END),
    SUM(CASE WHEN type = 2 THEN amount ELSE 0 END)
FROM transactions
"""


@tool("total_balance")
def total_balance() -> dict:
    """Busca no banco de dados o saldo total de todas as transações."""

    try:
        with get_cursor() as (_, cur):
            cur.execute(_SQL)
            gain, expenses = cur.fetchone()

        gain = float(gain or 0)
        expenses = float(expenses or 0)

        return ToolResponse.ok(
            sql_return={
                "total_income": gain,
                "total_expenses": expenses,
                "saldo_geral": gain - expenses,
            }
        )

    except Exception as e:
        return ToolResponse.error(message=str(e))
