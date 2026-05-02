@tool("add_transaction", args_schema=AddTransactionArgs)
def add_transaction(
    amount: float,
    source_text: str = Field(
        ..., description="Mensagem original do usuário. SEMPRE preencha este campo."
    ),
    occurred_at: Optional[str] = None,
    type_id: Optional[int] = None,
    type_name: Optional[str] = None,
    category_id: Optional[int] = None,
    category_name: Optional[str] = None,
    description: Optional[str] = None,
    payment_method: Optional[str] = None,
) -> dict:
    """Insere uma transação financeira no banco."""

    conn = get_conn()
    cur = conn.cursor()

    try:
        st = source_text or description or ""

        resolved_type_id = _resolve_type_id(cur, type_id, type_name)
        resolved_category_id = _resolve_category_id(cur, category_id, category_name)

        if not resolved_type_id:
            return {
                "status": "error",
                "message": "Tipo inválido (use type_id ou type_name: INCOME/EXPENSES/TRANSFER).",
            }

        if occurred_at:
            cur.execute(
                """
                INSERT INTO transactions
                    (amount, type, category_id, description, payment_method, occurred_at, source_text)
                VALUES
                    (%s, %s, %s, %s, %s, %s::timestamptz, %s)
                RETURNING id, occurred_at;
                """,
                (
                    amount,
                    resolved_type_id,
                    resolved_category_id,
                    description,
                    payment_method,
                    occurred_at,
                    st,
                ),
            )

        else:
            cur.execute(
                """
                INSERT INTO transactions
                    (amount, type, category_id, description, payment_method, occurred_at, source_text)
                VALUES
                    (%s, %s, %s, %s, %s, NOW(), %s)
                RETURNING id, occurred_at;
                """,
                (
                    amount,
                    resolved_type_id,
                    resolved_category_id,
                    description,
                    payment_method,
                    st,
                ),
            )

        new_id, occurred = cur.fetchone()
        conn.commit()
        return {"status": "ok", "id": new_id, "occurred_at": str(occurred)}

    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}

    finally:
        try:
            cur.close()
            conn.close()

        except Exception:
            pass



