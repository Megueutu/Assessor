import os
from dotenv import load_dotenv
import psycopg2
from typing import Optional, List
from langchain.tools import tool
from pydantic import BaseModel, Field, field_validator

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
def get_conn(): return psycopg2.connect(DATABASE_URL)









class AddTransactionArgs(BaseModel):
    amount: float = Field(..., description="Valor da transação (use positivo).")
    source_text: Optional[str] = Field(default=None, description="Texto original do usuário.")
    occurred_at: Optional[str] = Field(default=None, description="Timestamp ISO 8601; se ausente, usa NOW() no banco.")
    type_id: Optional[int] = Field(default=None, description="ID em transaction_types (1=INCOME, 2=EXPENSES, 3=TRANSFER).")
    type_name: Optional[str] = Field(default=None, description="Nome do tipo: INCOME | EXPENSES | TRANSFER.")
    category_id: Optional[int] = Field(default=None, description="FK de categories (opcional).")
    category_name: Optional[str] = Field(default=None, description="Nome da categoria: comida, transporte, moradia, saúde, lazer, contas, besteira, estudo, férias, investimento, presente, outros.")
    description: Optional[str] = Field(default=None, description="Descrição (opcional).")
    payment_method: Optional[str] = Field(default=None, description="Forma de pagamento (opcional).")

    @field_validator("amount", mode="before")
    @classmethod
    def coerce_amount(cls, v):
        try:
            return float(v)
        except (TypeError, ValueError):
            raise ValueError(f"amount deve ser numérico, recebido: {v!r}")

TYPE_ALIASES = {
    "INCOME": "INCOME", "ENTRADA": "INCOME", "RECEITA": "INCOME", "SALÁRIO": "INCOME",
    "EXPENSE": "EXPENSES", "SAÍDA": "EXPENSES", "DESPESA": "EXPENSES", "GASTO": "EXPENSES",
    "TRANSFER": "TRANSFER", "TRANSFERÊNCIA": "TRANSFER", "TRASNF": "TRANSFER"
}









class QueryTransactionsArgs(BaseModel):
    source_text: Optional[str] = Field(default=None, description="Texto livre para buscar em source_text ou description.")
    date_from_local: Optional[str] = Field(default=None, description="Data inicial (YYYY-MM-DD) no fuso de São Paulo.")
    date_to_local: Optional[str] = Field(default=None, description="Data final (YYYY-MM-DD) no fuso de São Paulo.")
    type_name: Optional[str] = Field(default=None, description="Tipo: INCOME | EXPENSES | TRANSFER.")
    category_name: Optional[str] = Field(default=None, description="Nome da categoria (ex: COMIDA, TRANSPORTE).")

CATEGORY_ALIASES = {
    "ALMOÇO": "COMIDA", "JANTA": "COMIDA", "RESTAURANTE": "COMIDA", "IFOOD": "COMIDA", "MERCADO": "COMIDA",
    "DOCE": "BESTEIRA", "LANCHE": "BESTEIRA", "CERVEJA": "BESTEIRA", "PIZZA": "BESTEIRA", "SNACK": "BESTEIRA", "PODRÃO": "BESTEIRA",
    "UBER": "TRANSPORTE", "99": "TRANSPORTE", "GASOLINA": "TRANSPORTE", "ÔNIBUS": "TRANSPORTE", "METRÔ": "TRANSPORTE",
    "LUZ": "CONTAS", "ÁGUA": "CONTAS", "INTERNET": "CONTAS", "ALUGUEL": "MORADIA", "CONDOMÍNIO": "MORADIA",
    "CINEMA": "LAZER", "SHOW": "LAZER", "VIAGEM": "FÉRIAS", "HOTEL": "FÉRIAS",
    "FARMÁCIA": "SAÚDE", "MÉDICO": "SAÚDE", "EXAME": "SAÚDE", "ACADEMIA": "SAÚDE",
    "CURSO": "ESTUDO", "LIVRO": "ESTUDO", "ESCOLA": "ESTUDO", "FACULDADE": "ESTUDO",
    "AÇÃO": "INVESTIMENTO", "FUNDO": "INVESTIMENTO", "POUPANÇA": "INVESTIMENTO", "CRYPTO": "INVESTIMENTO",
    "GIFT": "PRESENTE", "ANIVERSÁRIO": "PRESENTE", "LEMBRANÇA": "PRESENTE",
}









class UpdateTransactionArgs(BaseModel):
    id: Optional[int] = Field(
        default=None,
        description="ID da transação a atualizar. Se ausente, será feita uma busca por (match_text + date_local)."
    )
    match_text: Optional[str] = Field(
        default=None,
        description="Texto para localizar transação quando id não for informado (busca em source_text/description)."
    )
    date_local: Optional[str] = Field(
        default=None,
        description="Data local (YYYY-MM-DD) em America/Sao_Paulo; usado em conjunto com match_text quando id ausente."
    )
    amount: Optional[float] = Field(default=None, description="Novo valor.")
    type_id: Optional[int] = Field(default=None, description="Novo type_id (1/2/3).")
    type_name: Optional[str] = Field(default=None, description="Novo type_name: INCOME | EXPENSES | TRANSFER.")
    category_id: Optional[int] = Field(default=None, description="Nova categoria (id).")
    category_name: Optional[str] = Field(default=None, description="Nova categoria (nome).")
    description: Optional[str] = Field(default=None, description="Nova descrição.")
    payment_method: Optional[str] = Field(default=None, description="Novo meio de pagamento.")
    occurred_at: Optional[str] = Field(default=None, description="Novo timestamp ISO 8601.")









def _resolve_type_id(cur, type_id: Optional[int], type_name: Optional[str]) -> Optional[int]:
    if type_name:
        t = type_name.strip().upper()
        if t in TYPE_ALIASES:
            t = TYPE_ALIASES[t]
        cur.execute("SELECT id FROM transaction_types WHERE UPPER(type)=%s LIMIT 1;", (t,))
        row = cur.fetchone()
        return row[0] if row else None
    if type_id:
        return int(type_id)
    
    

def _resolve_category_id(cur, category_id: Optional[int], category_name: Optional[str]) -> Optional[int]:
    if category_name:
        c = category_name.strip().upper()

        if c in CATEGORY_ALIASES:
            c = CATEGORY_ALIASES[c]

        cur.execute(
            "SELECT id FROM categories WHERE LOWER(name)=%s LIMIT 1;",
            (c.lower(),)
        )
        row = cur.fetchone()
        if row:
            return row[0]

        cur.execute("SELECT id FROM categories WHERE LOWER(name)='outros' LIMIT 1;")
        row = cur.fetchone()
        return row[0] if row else None

    if category_id:
        return int(category_id)

    cur.execute("SELECT id FROM categories WHERE LOWER(name)='outros' LIMIT 1;")
    row = cur.fetchone()
    return row[0] if row else None

def _get_category_id(cur, category_name: Optional[str]) -> Optional[int]:
    if not category_name:
        return None
    cur.execute(
        "SELECT id FROM categories WHERE LOWER(name) = LOWER(%s) LIMIT 1;",
        (category_name,)
    )
    row = cur.fetchone()
    return row[0] if row else None

def _local_date_filter_sql(field: str = "occurred_at") -> str:
    """
    Retorna um trecho SQL para filtragem por dia local em America/Sao_Paulo.
    Ex.: (occurred_at AT TIME ZONE 'America/Sao_Paulo')::date = %s::date
    """
    return f"(({field} AT TIME ZONE 'America/Sao_Paulo')::date = %s::date)"







@tool("add_transaction", args_schema=AddTransactionArgs)
def add_transaction(
    amount: float,
    source_text: str = Field(..., description="Mensagem original do usuário. SEMPRE preencha este campo."),
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
        resolved_category_id = _resolve_category_id(
            cur,
            category_id,
            category_name
        )
        
        if not resolved_type_id:
            return {"status": "error", "message": "Tipo inválido (use type_id ou type_name: INCOME/EXPENSES/TRANSFER)."}

        if occurred_at:
            cur.execute(
                """
                INSERT INTO transactions
                    (amount, type, category_id, description, payment_method, occurred_at, source_text)
                VALUES
                    (%s, %s, %s, %s, %s, %s::timestamptz, %s)
                RETURNING id, occurred_at;
                """,
                (amount, resolved_type_id, resolved_category_id, description, payment_method, occurred_at, st),
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
                (amount, resolved_type_id, resolved_category_id, description, payment_method, st),
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
        id_cat = _resolve_category_id(cur, None, category_name) if category_name else None

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
            sql += " AND (t.source_text ILIKE %(texto)s OR t.description ILIKE %(texto)s)"
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
                "data": str(row[4])
            }
            for row in dados
        ]

        return {"status": "ok", "resultados": resposta}

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        cur.close()
        conn.close()









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
            "saldo_geral": ganhos - gastos
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        cur.close()
        conn.close()









@tool("daily_balance")
def daily_balance(date_local: str) -> dict:
    """Busca no banco de dados o saldo total das transações do dia informado (YYYY-MM-DD)."""

    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                SUM(CASE WHEN type = 1 THEN amount ELSE 0 END),
                SUM(CASE WHEN type = 2 THEN amount ELSE 0 END)
            FROM transactions
            WHERE (occurred_at AT TIME ZONE 'UTC' AT TIME ZONE 'America/Sao_Paulo')::date = %s
            AND type IN (1, 2)
        """, (date_local,))

        ganhos, gastos = cur.fetchone()
        ganhos = float(ganhos or 0)
        gastos = float(gastos or 0)

        return {
            "status": "ok",
            "data": date_local,
            "total_income": ganhos,
            "total_expenses": gastos,
            "saldo": ganhos - gastos
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass









@tool("update_transaction", args_schema=UpdateTransactionArgs)
def update_transaction(
    id: Optional[int] = None,
    match_text: Optional[str] = None,
    date_local: Optional[str] = None,
    amount: Optional[float] = None,
    type_id: Optional[int] = None,
    type_name: Optional[str] = None,
    category_id: Optional[int] = None,
    category_name: Optional[str] = None,
    description: Optional[str] = None,
    payment_method: Optional[str] = None,
    occurred_at: Optional[str] = None,
) -> dict:
    """
    Atualiza uma transação existente.
    Estratégias:
      - Se 'id' for informado: atualiza diretamente por ID.
      - Caso contrário: localiza a transação mais recente que combine (match_text em source_text/description)
        E (date_local em America/Sao_Paulo), então atualiza.
    Retorna: status, rows_affected, id, e o registro atualizado.
    """
    if not any([amount, type_id, type_name, category_id, category_name, description, payment_method, occurred_at]):
        return {"status": "error", "message": "Nada para atualizar: forneça pelo menos um campo (amount, type, category, description, payment_method, occurred_at)."}

    conn = get_conn()
    cur = conn.cursor()
    try:
        # Resolve target_id
        target_id = id
        if target_id is None:
            if not match_text or not date_local:
                return {"status": "error", "message": "Sem 'id': informe match_text E date_local para localizar o registro."}

            # Buscar o mais recente no dia local informado que combine o texto
            cur.execute(
                f"""
                SELECT t.id
                FROM transactions t
                WHERE (t.source_text ILIKE %s OR t.description ILIKE %s)
                  AND {_local_date_filter_sql("t.occurred_at")}
                ORDER BY t.occurred_at DESC
                LIMIT 1;
                """,
                (f"%{match_text}%", f"%{match_text}%", date_local)
            )
            row = cur.fetchone()
            if not row:
                return {"status": "error", "message": "Nenhuma transação encontrada para os filtros fornecidos."}
            target_id = row[0]

        # Resolver type_id / category_id a partir de nomes, se fornecidos
        resolved_type_id = _resolve_type_id(cur, type_id, type_name) if (type_id or type_name) else None
        resolved_category_id = category_id
        if category_name and not category_id:
            resolved_category_id = _get_category_id(cur, category_name)

        # Montar SET dinâmico
        sets = []
        params: List[object] = []
        if amount is not None:
            sets.append("amount = %s")
            params.append(amount)
        if resolved_type_id is not None:
            sets.append("type = %s")
            params.append(resolved_type_id)
        if resolved_category_id is not None:
            sets.append("category_id = %s")
            params.append(resolved_category_id)
        if description is not None:
            sets.append("description = %s")
            params.append(description)
        if payment_method is not None:
            sets.append("payment_method = %s")
            params.append(payment_method)
        if occurred_at is not None:
            sets.append("occurred_at = %s::timestamptz")
            params.append(occurred_at)

        if not sets:
            return {"status": "error", "message": "Nenhum campo válido para atualizar."}

        params.append(target_id)

        cur.execute(
            f"UPDATE transactions SET {', '.join(sets)} WHERE id = %s;",
            params
        )
        rows_affected = cur.rowcount
        conn.commit()

        # Retornar o registro atualizado
        cur.execute(
            """
            SELECT
              t.id, t.occurred_at, t.amount, tt.type AS type_name,
              c.name AS category_name, t.description, t.payment_method, t.source_text
            FROM transactions t
            JOIN transaction_types tt ON tt.id = t.type
            LEFT JOIN categories c ON c.id = t.category_id
            WHERE t.id = %s;
            """,
            (target_id,)
        )
        r = cur.fetchone()
        updated = None
        if r:
            updated = {
                "id": r[0],
                "occurred_at": str(r[1]),
                "amount": float(r[2]),
                "type": r[3],
                "category": r[4],
                "description": r[5],
                "payment_method": r[6],
                "source_text": r[7],
            }

        return {
            "status": "ok",
            "rows_affected": rows_affected,
            "id": target_id,
            "updated": updated
        }

    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass









TOOLS = [add_transaction, query_transactions, total_balance, daily_balance]