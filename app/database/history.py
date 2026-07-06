from app.database.collections import Collections

_coll = Collections.SESSIONS

def retrieve_history(session_id: str, search: str = "", limit: int = 3) -> list[dict]:
    """
    Recupera resumos de sessões ANTERIORES (já encerradas) de um usuário.

    Estratégia: olha primeiro os resumos. Se houver termo de busca, filtra
    por ele; senão, traz as sessões mais recentes. As mensagens completas
    NÃO vêm aqui — para isso use recuperar_mensagens(doc_id).

    session_id : identifica o usuário (hoje fixo, depois dinâmico)
    busca      : termo opcional para filtrar resumos relevantes
    limite     : máximo de sessões retornadas (mais recentes primeiro)
    """
    filtro = {"session_id": session_id}

    if search:
        filtro["resumo"] = {"$regex": search, "$options": "i"}

    docs = (
        _coll
        .find(filtro, {"resumo": 1, "iniciada_em": 1})
        .sort("iniciada_em", -1)
        .limit(limit)
    )

    return [
        {"doc_id": d["_id"], "iniciada_em": d["iniciada_em"], "resumo": d["resumo"]}
        for d in docs
    ]


def retrieve_messages(doc_id: str) -> list[dict]:
    """
    Busca o array completo de mensagens de um documento específico, pelo _id.
    Usada no passo 2 — só quando o resumo deu match e você precisa do detalhe
    literal da conversa. No futuro, o doc_id virá do Qdrant.
    """
    doc = _coll.find_one({"_id": doc_id}, {"mensagens": 1})
    return doc["mensagens"] if doc else []