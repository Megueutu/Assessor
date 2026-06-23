from uuid import uuid8
from datetime import datetime, timezone

from app.agents.registry import SUMMARY_CHAT
from app.core.config import config
from app.core.database import mongo_conn


_coll = mongo_conn.get_collection("sessions")
_active_sessions = {}


def _now() -> datetime: return datetime.now(timezone.utc)

def start(session_id: str) -> None:
    uuid = str(uuid8)
    now = _now()

    _coll.insert_one({
        "_id":           uuid,
        "session_id":    session_id,
        "iniciada_em":   now,
        "atualizada_em": now,
        "resumo":        "",
        "mensagens":     [],
    })

    _active_sessions[session_id] = uuid


def save(session_id: str, role: str, content: str) -> None:
    """ Adiciona uma mensagem ao array de mensagens da sessão ativa. """
    doc_id = _active_sessions[session_id]

    _coll.update_one(
        {"_id": doc_id},
        {
            "$push": {"mensagens": {"role": role, "content": content}},
            "$set":  {"atualizada_em": _now()},
        },
    )


def terminate(session_id) -> str:
    doc_id = _active_sessions.get(session_id)

    if not doc_id:
        return ""

    doc = _coll.find_one({"_id": doc_id})

    if not doc or not doc.get("mensagens"):
        _active_sessions.pop(session_id, None)
        return ""

    resumo = SUMMARY_CHAT(doc["mensagens"])

    _coll.update_one(
        {"_id": doc_id},
        {"$set": {"resumo": resumo, "atualizada_em": _now()}},
    )

    _active_sessions.pop(session_id)

    return resumo
