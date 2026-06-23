import uuid
from datetime import datetime, timezone

from app.agents.registry import SUMMARY_AGENT

_sessoes_ativas: dict = {}

def iniciar_sessao(session_id: str) -> None:
    """
    Cria um novo documento de sessão no MongoDB.
    O doc_id (UUID) é gerado aqui e guardado em _sessoes_ativas.
    """
    doc_id = str(uuid.uuid4())
    agora  = _agora()

    col_sessoes.insert_one({
        "_id":           doc_id,
        "session_id":    session_id,
        "iniciada_em":   agora,
        "atualizada_em": agora,
        "resumo":        "",
        "mensagens":     [],
    })

    _sessoes_ativas[session_id] = doc_id


def salvar_mensagem(session_id: str, role: str, content: str) -> None:
    """ Adiciona uma mensagem ao array de mensagens da sessão ativa. """
    doc_id = _sessoes_ativas[session_id]

    col_sessoes.update_one(
        {"_id": doc_id},
        {
            "$push": {"mensagens": {"role": role, "content": content}},
            "$set":  {"atualizada_em": _agora()},
        },
    )


def encerrar_sessao(session_id) -> str:
    """
    Encerra a sessão ativa:
      1. Carrega mensagens do MongoDB
      2. Gera resumo via LLM
      3. Atualiza documento com resumo e atualizada_em
      4. Remove sessão do estado interno
    Retorna o resumo gerado ou string vazia se não houver mensagens.
    """
    doc_id = _sessoes_ativas.get(session_id)

    if not doc_id:
        return ""

    doc = col_sessoes.find_one({"_id": doc_id})

    if not doc or not doc.get("mensagens"):
        _sessoes_ativas.pop(session_id, None)
        return ""

    resumo = _gerar_resumo(doc["mensagens"])

    col_sessoes.update_one(
        {"_id": doc_id},
        {"$set": {"resumo": resumo, "atualizada_em": _agora()}},
    )

    _sessoes_ativas.pop(session_id)

    return resumo
