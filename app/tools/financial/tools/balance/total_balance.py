
@tool("total_balance")
def total_balance() -> dict:
    """Busca no banco de dados o saldo total de todas as transações."""

    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                SUM(CASE WHEN type = 1 THEN amount ELSE 0 END),
                SUM(CASE WHEN type = 2 THEN amount ELSE 0 END)
            FROM transactions
        """)

        ganhos, gastos = cur.fetchone()
        ganhos = float(ganhos or 0)
        gastos = float(gastos or 0)

        return {
            "status": "ok",
            "total_income": ganhos,
            "total_expenses": gastos,
            "saldo_geral": ganhos - gastos,
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        cur.close()
        conn.close()
