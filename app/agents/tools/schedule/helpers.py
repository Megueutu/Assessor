from datetime import datetime, timedelta


_SQL_CONFLICTS = """
SELECT id, title, start_time, end_time, location, notes, status, recorded_at, updated_at, cancelled_at
FROM events
WHERE status = 'ACTIVE'
  AND (%s IS NULL OR id <> %s)
  AND start_time < %s
  AND COALESCE(end_time, start_time + INTERVAL '1 minute') > %s
ORDER BY start_time
LIMIT 10
"""


def effective_end(start_time: datetime, end_time: datetime | None) -> datetime:
    return end_time or start_time + timedelta(minutes=1)


def find_conflicts(cur, start_time: datetime, end_time: datetime | None, exclude_event_id: int | None = None):
    cur.execute(
        _SQL_CONFLICTS,
        (exclude_event_id, exclude_event_id, effective_end(start_time, end_time), start_time),
    )
    return cur.fetchall()


def serialize_event(row) -> dict:
    return {
        "event_id": row[0],
        "title": row[1],
        "start_time": row[2].isoformat(),
        "end_time": row[3].isoformat() if row[3] else None,
        "location": row[4],
        "notes": row[5],
        "status": row[6],
        "recorded_at": row[7].isoformat(),
        "updated_at": row[8].isoformat(),
        "cancelled_at": row[9].isoformat() if row[9] else None,
    }
