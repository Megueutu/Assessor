import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.agents.tools.education import education_retriever as retriever


class TestEducationRetriever(unittest.TestCase):
    def setUp(self):
        retriever._INDEX = None
        retriever._INDEX_SIGNATURE = ()

    def test_should_return_controlled_error_when_corpus_is_empty(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(retriever.config, "EDUCATION_DOCUMENTS_PATH", directory),
        ):
            result = retriever.education_retriever.func(query="What is compound interest?")

        self.assertEqual(result["status"], "error")
        self.assertIn("Nenhum material", result["message"])

    def test_should_rebuild_index_when_document_is_added(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "budget.md").write_text("# Budget\nMonthly planning.", encoding="utf-8")

            with (
                patch.object(retriever.config, "EDUCATION_DOCUMENTS_PATH", directory),
                patch.object(retriever, "_build_index", side_effect=[object(), object()]) as build_index,
            ):
                first_index = retriever._get_index()
                (root / "credit.md").write_text("# Credit\nBorrowing costs.", encoding="utf-8")
                second_index = retriever._get_index()

        self.assertIsNot(first_index, second_index)
        self.assertEqual(build_index.call_count, 2)


if __name__ == "__main__":
    unittest.main()
