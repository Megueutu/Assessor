
@tool("daily_balance")
def daily_balance(date_local: str) -> dict:
    """Busca no banco de dados o saldo total das transações do dia informado (YYYY-MM-DD)."""

    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT
                SUM(CASE WHEN type = 1 THEN amount ELSE 0 END),
                SUM(CASE WHEN type = 2 THEN amount ELSE 0 END)
            FROM transactions
            WHERE (occurred_at AT TIME ZONE 'UTC' AT TIME ZONE 'America/Sao_Paulo')::date = %s
            AND type IN (1, 2)
        """,
            (date_local,),
        )

        ganhos, gastos = cur.fetchone()
        ganhos = float(ganhos or 0)
        gastos = float(gastos or 0)

        return {
            "status": "ok",
            "data": date_local,
            "total_income": ganhos,
            "total_expenses": gastos,
            "saldo": ganhos - gastos,
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass
            