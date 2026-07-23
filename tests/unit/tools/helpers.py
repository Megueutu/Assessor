from contextlib import contextmanager


class FakeCursor:
    def __init__(self, fetchone_values=None, fetchall_values=None):
        self.fetchone_values = list(fetchone_values or [])
        self.fetchall_values = list(fetchall_values or [])
        self.executions = []
        self.rowcount = 0

    def execute(self, sql, params=None):
        self.executions.append((sql, params))

    def fetchone(self):
        return self.fetchone_values.pop(0) if self.fetchone_values else None

    def fetchall(self):
        return self.fetchall_values.pop(0) if self.fetchall_values else []


def cursor_context(cursor):
    @contextmanager
    def _context():
        yield object(), cursor

    return _context()
