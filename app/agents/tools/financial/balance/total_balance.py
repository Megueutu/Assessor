from langchain.tools import tool

from app.core.database  import get_cursor
from app.agents.tools.response import ToolResponse


_SQL = """
SELECT
    SUM(CASE WHEN tt.type = 'INCOME' THEN t.amount ELSE 0 END),
    SUM(CASE WHEN tt.type = 'EXPENSES' THEN t.amount ELSE 0 END)
FROM transactions t
JOIN transaction_types tt ON tt.id = t.type
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

    except Exception:
        return ToolResponse.error(message="Não foi possível consultar o saldo total.")
