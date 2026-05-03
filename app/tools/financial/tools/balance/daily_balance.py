from langchain_core.tools import tool
    
from app.core.database import get_cursor
from app.tools.response import ToolResponse


_SQL = """
SELECT
    SUM(CASE WHEN type = 1 THEN amount ELSE 0 END),
    SUM(CASE WHEN type = 2 THEN amount ELSE 0 END)
FROM transactions
WHERE (occurred_at AT TIME ZONE 'UTC' AT TIME ZONE 'America/Sao_Paulo')::date = %s
AND type IN (1, 2)
"""


@tool("daily_balance")
def daily_balance(date_local: str) -> dict:
    """Busca no banco de dados o saldo total das transações do dia informado (YYYY-MM-DD)."""

    try:
        with get_cursor() as (_, cur):
            cur.execute(_SQL, (date_local,))
            gain, expenses = cur.fetchone()

        gain = float(gain or 0)
        expenses = float(expenses or 0)

        return ToolResponse.ok(
            sql_return={
                "data": date_local,
                "total_income": gain,
                "total_expenses": expenses,
                "saldo": gain - expenses,
            }
        )

    except Exception as e:
        return ToolResponse.error(message=str(e))