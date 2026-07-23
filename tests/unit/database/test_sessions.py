import unittest
from unittest.mock import patch

from app.core.database import mongo_conn

with patch.object(mongo_conn, "get_collection", return_value=object()):
    from app.database import sessions


class FakeCollection:
    def __init__(self, documents=None):
        self.documents = {doc["_id"]: dict(doc) for doc in (documents or [])}
        self.indexes = []

    def create_index(self, fields, name):
        self.indexes.append((fields, name))

    def find_one(self, filters, sort=None):
        for document in self.documents.values():
            if all(document.get(key) == value for key, value in filters.items()):
                return dict(document)
        return None

    def insert_one(self, document):
        self.documents[document["_id"]] = dict(document)

    def update_one(self, filters, update):
        document = self.documents[filters["_id"]]
        if "$push" in update:
            for field, value in update["$push"].items():
                document.setdefault(field, []).append(value)
        if "$set" in update:
            document.update(update["$set"])


class TestSessions(unittest.TestCase):
    def setUp(self):
        self.collection = FakeCollection()
        sessions._coll = self.collection
        sessions._active_sessions.clear()
        sessions._indexes_created = False

    def test_should_resume_active_session(self):
        self.collection.documents["existing"] = {
            "_id": "existing",
            "session_id": "user-1",
            "status": "ACTIVE",
            "mensagens": [],
        }

        session_uuid = sessions.start("user-1")

        self.assertEqual(session_uuid, "existing")

    def test_should_complete_session_with_summary(self):
        session_uuid = sessions.start("user-1")
        sessions.save("user-1", "human", "Quero comprar um PlayStation")

        with patch.object(sessions, "_summarize", return_value="Usuário quer um PlayStation."):
            summary = sessions.terminate("user-1")

        self.assertEqual(summary, "Usuário quer um PlayStation.")
        self.assertEqual(self.collection.documents[session_uuid]["status"], "COMPLETED")

    def test_should_keep_session_active_when_summary_fails(self):
        session_uuid = sessions.start("user-1")
        sessions.save("user-1", "human", "Mensagem")

        with patch.object(sessions, "_summarize", side_effect=RuntimeError("model unavailable")):
            with self.assertRaises(RuntimeError):
                sessions.terminate("user-1")

        self.assertEqual(self.collection.documents[session_uuid]["status"], "ACTIVE")


if __name__ == "__main__":
    unittest.main()
