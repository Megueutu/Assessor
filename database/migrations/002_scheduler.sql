BEGIN;

ALTER TABLE events ADD COLUMN IF NOT EXISTS status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE';
ALTER TABLE events ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
ALTER TABLE events ADD COLUMN IF NOT EXISTS cancelled_at TIMESTAMPTZ;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'events_status_valid') THEN
    ALTER TABLE events
      ADD CONSTRAINT events_status_valid CHECK (status IN ('ACTIVE', 'CANCELLED'));
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'events_time_valid') THEN
    ALTER TABLE events
      ADD CONSTRAINT events_time_valid CHECK (end_time IS NULL OR end_time > start_time);
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'events_cancellation_valid') THEN
    ALTER TABLE events
      ADD CONSTRAINT events_cancellation_valid CHECK (
        (status = 'CANCELLED' AND cancelled_at IS NOT NULL)
        OR (status = 'ACTIVE' AND cancelled_at IS NULL)
      );
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_events_status_start_time ON events (status, start_time);

COMMIT;
