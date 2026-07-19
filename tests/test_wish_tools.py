import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from app.agents.tools.financial.transaction.purchase_wish import purchase_wish
from app.agents.tools.notes.wish.cancel_wish import cancel_wish
from tests.helpers import FakeCursor, cursor_context


class TestWishTools(unittest.TestCase):
    def test_should_reject_purchase_without_explicit_confirmation(self):
        result = purchase_wish.func(
            wish_id=1,
            amount=3500,
            source_text="Comprei o PlayStation",
            confirmation="",
        )

        self.assertEqual(result["status"], "error")

    def test_should_create_transaction_and_fulfill_wish_atomically(self):
        now = datetime.now(timezone.utc)
        cursor = FakeCursor(fetchone_values=[
            (5, "PlayStation", 12),
            (2,),
            (31, now),
            (5, "PlayStation", "PURCHASED", now),
        ])

        with patch("app.agents.tools.financial.transaction.purchase_wish.get_cursor", return_value=cursor_context(cursor)):
            result = purchase_wish.func(
                wish_id=5,
                amount=3500,
                source_text="Sim, confirmo a compra do PlayStation",
                confirmation="CONFIRMO",
            )

        self.assertEqual(result["transaction"]["transaction_id"], 31)
        self.assertEqual(result["wish"]["status"], "PURCHASED")

    def test_should_not_create_transaction_when_wish_is_not_active(self):
        cursor = FakeCursor(fetchone_values=[None])

        with patch("app.agents.tools.financial.transaction.purchase_wish.get_cursor", return_value=cursor_context(cursor)):
            result = purchase_wish.func(
                wish_id=5,
                amount=3500,
                source_text="Confirmo",
                confirmation="CONFIRMO",
            )

        self.assertEqual(len(cursor.executions), 1)
        self.assertEqual(result["status"], "error")

    def test_should_return_error_when_cancelling_inactive_wish(self):
        cursor = FakeCursor(fetchone_values=[None])

        with patch("app.agents.tools.notes.wish.cancel_wish.get_cursor", return_value=cursor_context(cursor)):
            result = cancel_wish.func(wish_id=5)

        self.assertEqual(result["status"], "error")


if __name__ == "__main__":
    unittest.main()
