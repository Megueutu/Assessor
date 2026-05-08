from typing  import Optional
from .loader import PAYMENT_METHOD_ALIASES, CATEGORY_ALIASES

def resolve_type_id(
    cur,
    type_id:   Optional[int],
    type_name: Optional[str]
) -> Optional[int]:
    
    if type_name:
        t = type_name.strip().upper()
        if t in PAYMENT_METHOD_ALIASES:
            t = PAYMENT_METHOD_ALIASES[t]
        cur.execute(
            "SELECT id FROM transaction_types WHERE UPPER(type)=%s LIMIT 1;", (t,)
        )
        row = cur.fetchone()
        return row[0] if row else None
    if type_id:
        return int(type_id)


def resolve_category_id(
    cur,
    category_id:   Optional[int],
    category_name: Optional[str]
) -> Optional[int]:
    
    if category_name:
        c = category_name.strip().upper()

        if c in CATEGORY_ALIASES:
            c = CATEGORY_ALIASES[c]

        cur.execute(
            "SELECT id FROM categories WHERE LOWER(name)=%s LIMIT 1;", (c.lower(),)
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


def get_category_id(cur, category_name: Optional[str]) -> Optional[int]:
    if not category_name:
        return None
    cur.execute(
        "SELECT id FROM categories WHERE LOWER(name) = LOWER(%s) LIMIT 1;",
        (category_name,),
    )
    row = cur.fetchone()
    return row[0] if row else None


def local_date_filter_sql(field: str = "occurred_at") -> str:
    """
    Retorna um trecho SQL para filtragem por dia local em America/Sao_Paulo.
    Ex.: (occurred_at AT TIME ZONE 'America/Sao_Paulo')::date = %s::date
    """
    return f"(({field} AT TIME ZONE 'America/Sao_Paulo')::date = %s::date)"
