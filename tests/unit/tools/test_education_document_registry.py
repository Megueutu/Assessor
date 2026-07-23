import tempfile
import unittest
from pathlib import Path

from app.agents.tools.education.document_registry import discover_documents, load_documents


class TestEducationDocumentRegistry(unittest.TestCase):
    def test_should_discover_supported_documents_recursively(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / "credit"
            nested.mkdir()
            (root / "budget.md").write_text("# Budget", encoding="utf-8")
            (nested / "interest.PDF").touch()
            (nested / "ignored.txt").touch()

            documents = discover_documents(root)

        self.assertEqual(
            [path.name for path in documents],
            ["budget.md", "interest.PDF"],
        )

    def test_should_load_markdown_with_normalized_source_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / "budget"
            nested.mkdir()
            path = nested / "emergency_fund.md"
            path.write_text("# Emergency fund\nKeep liquid reserves.", encoding="utf-8")

            documents = load_documents(root)

        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].metadata["source"], "budget/emergency_fund.md")
        self.assertEqual(documents[0].metadata["file_name"], "emergency_fund.md")
        self.assertEqual(documents[0].metadata["document_type"], "md")
        self.assertIsNone(documents[0].metadata["page_number"])

    def test_should_return_empty_list_when_directory_does_not_exist(self):
        documents = discover_documents("/tmp/assessor-missing-education-documents")

        self.assertEqual(documents, [])


if __name__ == "__main__":
    unittest.main()
