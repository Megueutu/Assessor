from uuid import uuid4
from datetime import datetime, timezone

from app.database.collections import Collections

_coll = Collections.SESSIONS
_active_sessions = {}
_indexes_created = False

def _now() -> datetime: return datetime.now(timezone.utc)


def _ensure_indexes() -> None:
    global _indexes_created
    if _indexes_created:
        return
    _coll.create_index(
        [("session_id", 1), ("status", 1), ("atualizada_em", -1)],
        name="idx_sessions_user_status_updated",
    )
    _indexes_created = True


def _summarize(messages: list[dict]) -> str:
    from app.agents.registry import SUMMARY_CHAT
    return SUMMARY_CHAT(messages)


def start(session_id: str) -> str:
    _ensure_indexes()
    active_uuid = _active_sessions.get(session_id)
    if active_uuid:
        return active_uuid

    active = _coll.find_one(
        {"session_id": session_id, "status": "ACTIVE"},
        sort=[("atualizada_em", -1)],
    )
    if active:
        _active_sessions[session_id] = active["_id"]
        return active["_id"]

    uuid = str(uuid4())
    now = _now()

    _coll.insert_one({
        "_id":           uuid,
        "session_id":    session_id,
        "iniciada_em":   now,
        "atualizada_em": now,
        "resumo":        "",
        "mensagens":     [],
        "status":        "ACTIVE",
        "encerrada_em":  None,
    })

    _active_sessions[session_id] = uuid
    return uuid


def save(session_id: str, role: str, content: str) -> None:
    uuid = _active_sessions.get(session_id) or start(session_id)

    _coll.update_one(
        {"_id": uuid},
        {
            "$push": {"mensagens": {"role": role, "content": content}},
            "$set":  {"atualizada_em": _now()},
        },
    )


def terminate(session_id) -> str:
    uuid = _active_sessions.get(session_id)

    if not uuid: return ""
    doc = _coll.find_one({"_id": uuid})

    if not doc:
        _active_sessions.pop(session_id, None)
        return ""

    now = _now()
    if not doc.get("mensagens"):
        _coll.update_one(
            {"_id": uuid},
            {"$set": {"status": "COMPLETED", "encerrada_em": now, "atualizada_em": now}},
        )
        _active_sessions.pop(session_id, None)
        return ""

    summary = _summarize(doc["mensagens"])

    _coll.update_one(
        {"_id": uuid},
        {"$set": {
            "resumo": summary,
            "status": "COMPLETED",
            "encerrada_em": now,
            "atualizada_em": now,
        }},
    )

    _active_sessions.pop(session_id)

    return summary
