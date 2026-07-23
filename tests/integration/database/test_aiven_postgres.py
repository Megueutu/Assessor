import os
import unittest

from psycopg2 import connect

from tests.integration.helpers import integration_tests_enabled


@unittest.skipUnless(
    integration_tests_enabled(),
    "Testes de integração desabilitados.",
)
class TestAivenPostgres(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database_url = (
            os.getenv("POSTGRES_URI", "").strip()
            or os.getenv("POSTGRES_LOCAL", "").strip()
        )
        if not cls.database_url:
            raise unittest.SkipTest("Configure POSTGRES_URI ou POSTGRES_LOCAL.")

    def test_should_connect_and_expose_required_schema(self):
        required_tables = {
            "categories",
            "transaction_types",
            "transactions",
            "events",
            "notes",
            "note_items",
            "wishes",
        }

        with connect(self.database_url, connect_timeout=10) as connection:
            connection.set_session(readonly=True)
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_database()")
                database_name = cursor.fetchone()[0]
                cursor.execute(
                    """SELECT table_name
                       FROM information_schema.tables
                       WHERE table_schema = 'public'"""
                )
                tables = {row[0] for row in cursor.fetchall()}

        self.assertTrue(database_name)
        self.assertTrue(required_tables.issubset(tables))

    def test_should_execute_read_only_query(self):
        with connect(self.database_url, connect_timeout=10) as connection:
            connection.set_session(readonly=True)
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()[0]

        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
