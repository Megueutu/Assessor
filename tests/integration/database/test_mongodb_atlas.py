import os
import unittest

from pymongo import MongoClient

from tests.integration.helpers import integration_tests_enabled


@unittest.skipUnless(
    integration_tests_enabled(),
    "Testes de integração desabilitados.",
)
class TestMongoDBAtlas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database_url = (
            os.getenv("MONGODB_URI", "").strip()
            or os.getenv("MONGODB_LOCAL", "").strip()
        )
        database_name = os.getenv("MONGODB_DB", "").strip()
        if not database_url or not database_name:
            raise unittest.SkipTest(
                "Configure MONGODB_URI ou MONGODB_LOCAL e MONGODB_DB."
            )

        cls.client = MongoClient(
            database_url,
            serverSelectionTimeoutMS=10000,
        )
        cls.client.admin.command("ping")
        cls.database = cls.client[database_name]

    @classmethod
    def tearDownClass(cls):
        cls.client.close()

    def test_should_connect_to_configured_database(self):
        response = self.database.command("ping")

        self.assertEqual(response["ok"], 1.0)

    def test_should_read_collection_metadata(self):
        collection_names = self.database.list_collection_names()

        self.assertIsInstance(collection_names, list)


if __name__ == "__main__":
    unittest.main()
