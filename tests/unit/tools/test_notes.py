import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from app.agents.tools.notes.note.add_note import add_note
from app.agents.tools.notes.note.conclude_note import conclude_note
from app.agents.tools.notes.note.list_notes import list_notes
from tests.unit.tools.helpers import FakeCursor, cursor_context


class TestNotesTools(unittest.TestCase):
    def test_should_create_note_and_items_in_same_transaction(self):
        now = datetime.now(timezone.utc)
        cursor = FakeCursor(fetchone_values=[
            (7, "Compras", "Comprar itens", "ACTIVE", now),
            (10, "arroz", 0, False),
            (11, "feijão", 1, False),
        ])

        with patch("app.agents.tools.notes.note.add_note.get_cursor", return_value=cursor_context(cursor)):
            result = add_note.func(
                source_text="Comprar arroz e feijão",
                title="Compras",
                content="Comprar itens",
                items=["arroz", "feijão"],
            )

        self.assertEqual(result["note"]["note_id"], 7)
        self.assertEqual(len(result["note"]["items"]), 2)

    def test_should_return_error_when_note_does_not_exist(self):
        cursor = FakeCursor(fetchone_values=[None])

        with patch("app.agents.tools.notes.note.conclude_note.get_cursor", return_value=cursor_context(cursor)):
            result = conclude_note.func(note_id=999)

        self.assertEqual(result["status"], "error")

    def test_should_add_one_item_filter_per_requested_item(self):
        cursor = FakeCursor(fetchall_values=[[]])

        with patch("app.agents.tools.notes.note.list_notes.get_cursor", return_value=cursor_context(cursor)):
            result = list_notes.func(items=["arroz", "feijão"], limit=20)

        query, params = cursor.executions[0]
        self.assertEqual(query.count("EXISTS (SELECT 1 FROM note_items"), 2)
        self.assertEqual(params, ["%arroz%", "%feijão%", 20])
        self.assertEqual(result["total"], 0)


if __name__ == "__main__":
    unittest.main()
