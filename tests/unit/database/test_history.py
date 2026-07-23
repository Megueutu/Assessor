import unittest
from unittest.mock import patch

from app.core.database import mongo_conn

with patch.object(mongo_conn, "get_collection", return_value=object()):
    from app.database import history


class FakeCursor:
    def __init__(self, documents):
        self.documents = documents

    def sort(self, *_):
        return self

    def limit(self, value):
        return self.documents[:value]


class FakeCollection:
    def __init__(self, documents):
        self.documents = documents
        self.filters = None

    def find(self, filters, projection):
        self.filters = filters
        return FakeCursor(self.documents)


class TestHistory(unittest.TestCase):
    def test_should_escape_search_and_filter_completed_sessions(self):
        collection = FakeCollection([])
        history._coll = collection

        result = history.retrieve_history("user-1", "playstation.*", limit=3)

        self.assertEqual(result, [])
        self.assertEqual(collection.filters["resumo"]["$regex"], "playstation\\.\\*")
        self.assertIn({"status": "COMPLETED"}, collection.filters["$or"])


if __name__ == "__main__":
    unittest.main()
