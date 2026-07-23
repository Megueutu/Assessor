import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from pydantic import ValidationError

from app.agents.tools.schedule.args import AddEventArgs, CheckAvailabilityArgs
from app.agents.tools.schedule.event.add_event import add_event
from app.agents.tools.schedule.event.cancel_event import cancel_event
from app.agents.tools.schedule.event.check_availability import check_availability
from app.agents.tools.schedule.event.list_events import list_events
from app.agents.tools.schedule.event.update_event import update_event
from tests.unit.tools.helpers import FakeCursor, cursor_context


def event_row(event_id=7, title="Reunião", start=None, end=None, status="ACTIVE"):
    start = start or datetime(2026, 7, 20, 13, 0, tzinfo=timezone.utc)
    end = end or datetime(2026, 7, 20, 14, 0, tzinfo=timezone.utc)
    now = datetime(2026, 7, 19, 12, 0, tzinfo=timezone.utc)
    return (event_id, title, start, end, "Sala 1", "Planejamento", status, now, now, None)


class TestScheduleTools(unittest.TestCase):
    def test_should_create_event_when_period_is_available(self):
        start = datetime(2026, 7, 20, 13, 0, tzinfo=timezone.utc)
        end = datetime(2026, 7, 20, 14, 0, tzinfo=timezone.utc)
        cursor = FakeCursor(fetchone_values=[event_row(start=start, end=end)], fetchall_values=[[]])

        with patch("app.agents.tools.schedule.event.add_event.get_cursor", return_value=cursor_context(cursor)):
            result = add_event.func(
                title="Reunião",
                start_time=start,
                end_time=end,
                location="Sala 1",
                notes="Planejamento",
                source_text="Marque uma reunião amanhã",
            )

        self.assertEqual(result["event"]["event_id"], 7)
        self.assertEqual(len(cursor.executions), 2)

    def test_should_not_create_event_when_period_conflicts(self):
        start = datetime(2026, 7, 20, 13, 30, tzinfo=timezone.utc)
        end = datetime(2026, 7, 20, 14, 30, tzinfo=timezone.utc)
        cursor = FakeCursor(fetchall_values=[[event_row()]])

        with patch("app.agents.tools.schedule.event.add_event.get_cursor", return_value=cursor_context(cursor)):
            result = add_event.func(
                title="Outro evento",
                start_time=start,
                end_time=end,
                source_text="Agende outro evento",
            )

        self.assertEqual(result["status"], "conflict")
        self.assertEqual(len(cursor.executions), 1)

    def test_should_report_availability_without_persisting(self):
        start = datetime(2026, 7, 20, 15, 0, tzinfo=timezone.utc)
        end = datetime(2026, 7, 20, 16, 0, tzinfo=timezone.utc)
        cursor = FakeCursor(fetchall_values=[[]])

        with patch(
            "app.agents.tools.schedule.event.check_availability.get_cursor",
            return_value=cursor_context(cursor),
        ):
            result = check_availability.func(start_time=start, end_time=end)

        self.assertTrue(result["available"])
        self.assertEqual(len(cursor.executions), 1)

    def test_should_apply_event_list_filters(self):
        start = datetime(2026, 7, 20, 0, 0, tzinfo=timezone.utc)
        end = datetime(2026, 7, 21, 0, 0, tzinfo=timezone.utc)
        cursor = FakeCursor(fetchall_values=[[]])

        with patch("app.agents.tools.schedule.event.list_events.get_cursor", return_value=cursor_context(cursor)):
            result = list_events.func(
                search="reunião",
                start_from=start,
                start_until=end,
                status="ACTIVE",
                limit=10,
            )

        query, params = cursor.executions[0]
        self.assertIn("start_time >= %s", query)
        self.assertEqual(params, ["%reunião%"] * 4 + [start, end, "ACTIVE", 10])
        self.assertEqual(result["total"], 0)

    def test_should_reject_conflicting_event_update(self):
        new_start = datetime(2026, 7, 20, 15, 0, tzinfo=timezone.utc)
        new_end = datetime(2026, 7, 20, 16, 0, tzinfo=timezone.utc)
        current = event_row(event_id=7)
        conflict = event_row(event_id=8, title="Dentista", start=new_start, end=new_end)
        cursor = FakeCursor(fetchone_values=[current], fetchall_values=[[conflict]])

        with patch("app.agents.tools.schedule.event.update_event.get_cursor", return_value=cursor_context(cursor)):
            result = update_event.func(event_id=7, start_time=new_start, end_time=new_end)

        self.assertEqual(result["status"], "conflict")
        self.assertEqual(len(cursor.executions), 2)

    def test_should_return_error_when_cancelling_inactive_event(self):
        cursor = FakeCursor(fetchone_values=[None])

        with patch("app.agents.tools.schedule.event.cancel_event.get_cursor", return_value=cursor_context(cursor)):
            result = cancel_event.func(event_id=999)

        self.assertEqual(result["status"], "error")

    def test_should_reject_naive_or_reversed_intervals(self):
        with self.assertRaises(ValidationError):
            AddEventArgs(
                title="Sem fuso",
                start_time=datetime(2026, 7, 20, 13, 0),
                source_text="Agende",
            )
        with self.assertRaises(ValidationError):
            CheckAvailabilityArgs(
                start_time=datetime(2026, 7, 20, 14, 0, tzinfo=timezone.utc),
                end_time=datetime(2026, 7, 20, 13, 0, tzinfo=timezone.utc),
            )


if __name__ == "__main__":
    unittest.main()
