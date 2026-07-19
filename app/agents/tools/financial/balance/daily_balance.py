from langchain.tools import tool
    
from app.core.database  import get_cursor
from app.agents.tools.response import ToolResponse


_SQL = """
SELECT
    SUM(CASE WHEN tt.type = 'INCOME' THEN t.amount ELSE 0 END),
    SUM(CASE WHEN tt.type = 'EXPENSES' THEN t.amount ELSE 0 END)
FROM transactions t
JOIN transaction_types tt ON tt.id = t.type
WHERE (t.occurred_at AT TIME ZONE 'America/Sao_Paulo')::date = %s::date
AND tt.type IN ('INCOME', 'EXPENSES')
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

    except Exception:
        return ToolResponse.error(message="Não foi possível consultar o saldo diário.")
