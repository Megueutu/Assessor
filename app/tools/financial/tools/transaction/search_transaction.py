
@tool("query_transactions", args_schema=QueryTransactionsArgs)
def query_transactions(
    source_text: Optional[str] = None,
    date_from_local: Optional[str] = None,
    date_to_local: Optional[str] = None,
    type_name: Optional[str] = None,
    category_name: Optional[str] = None,
) -> dict:
    """Consulta transações com filtros por texto, tipo e datas locais (America/Sao_Paulo)."""

    conn = get_conn()
    cur = conn.cursor()

    try:
        id_tipo = _resolve_type_id(cur, None, type_name) if type_name else None
        id_cat = (
            _resolve_category_id(cur, None, category_name) if category_name else None
        )

        sql = """
            SELECT t.amount, tt.type, c.name, t.description, t.occurred_at
            FROM transactions t
            JOIN transaction_types tt ON t.type = tt.id
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE 1=1
        """
        filtros = {}

        if id_tipo:
            sql += " AND t.type = %(id_tipo)s"
            filtros["id_tipo"] = id_tipo

        if id_cat:
            sql += " AND t.category_id = %(id_cat)s"
            filtros["id_cat"] = id_cat

        if source_text:
            sql += (
                " AND (t.source_text ILIKE %(texto)s OR t.description ILIKE %(texto)s)"
            )
            filtros["texto"] = f"%{source_text}%"

        if date_from_local:
            sql += " AND (t.occurred_at AT TIME ZONE 'UTC' AT TIME ZONE 'America/Sao_Paulo') >= %(inicio)s"
            filtros["inicio"] = date_from_local

        if date_to_local:
            sql += " AND (t.occurred_at AT TIME ZONE 'UTC' AT TIME ZONE 'America/Sao_Paulo') <= %(fim)s::date + interval '1 day' - interval '1 second'"
            filtros["fim"] = date_to_local

        sql += " ORDER BY t.occurred_at DESC LIMIT 20"

        cur.execute(sql, filtros)
        dados = cur.fetchall()

        resposta = [
            {
                "valor": float(row[0]),
                "tipo": row[1],
                "categoria": row[2],
                "descricao": row[3],
                "data": str(row[4]),
            }
            for row in dados
        ]

        return {"status": "ok", "resultados": resposta}

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        cur.close()
        conn.close()

