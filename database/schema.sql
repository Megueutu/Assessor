CREATE TABLE IF NOT EXISTS categories (
  id           SERIAL PRIMARY KEY,
  name         VARCHAR(64) NOT NULL,
  description  TEXT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_categories_name
  ON categories (LOWER(name));

CREATE TABLE IF NOT EXISTS transaction_types (
  id      SERIAL PRIMARY KEY,
  type    TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_transaction_types_type
  ON transaction_types (UPPER(type));

CREATE TABLE IF NOT EXISTS transactions (
  id             BIGSERIAL PRIMARY KEY,
  amount         NUMERIC(14,2) NOT NULL CONSTRAINT transactions_amount_positive CHECK (amount > 0),
  type           INT NOT NULL DEFAULT 2 REFERENCES transaction_types(id),
  category_id    INT REFERENCES categories(id) ON DELETE SET NULL,
  description    TEXT,
  payment_method VARCHAR(32),
  occurred_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  source_text    TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_transactions_occurred_at
  ON transactions (occurred_at DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_category_time
  ON transactions (category_id, occurred_at DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_type_time
  ON transactions (type, occurred_at DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_localday
  ON transactions (((occurred_at AT TIME ZONE 'America/Sao_Paulo')::date));

CREATE TABLE IF NOT EXISTS events (
  id           BIGSERIAL PRIMARY KEY,
  title        TEXT NOT NULL,
  start_time   TIMESTAMPTZ NOT NULL,
  end_time     TIMESTAMPTZ,
  location     TEXT,
  notes        TEXT,
  status       VARCHAR(16) NOT NULL DEFAULT 'ACTIVE'
               CONSTRAINT events_status_valid CHECK (status IN ('ACTIVE', 'CANCELLED')),
  recorded_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  cancelled_at TIMESTAMPTZ,
  source_text  TEXT NOT NULL,
  CONSTRAINT events_time_valid CHECK (end_time IS NULL OR end_time > start_time),
  CONSTRAINT events_cancellation_valid CHECK (
    (status = 'CANCELLED' AND cancelled_at IS NOT NULL)
    OR (status = 'ACTIVE' AND cancelled_at IS NULL)
  )
);

CREATE INDEX IF NOT EXISTS idx_events_start_time
  ON events (start_time DESC);

CREATE INDEX IF NOT EXISTS idx_events_status_start_time
  ON events (status, start_time);

CREATE TABLE IF NOT EXISTS notes (
  id           BIGSERIAL PRIMARY KEY,
  title        TEXT,
  content      TEXT NOT NULL,
  source_text  TEXT NOT NULL,
  category_id  INT REFERENCES categories(id) ON DELETE SET NULL,
  status       VARCHAR(16) NOT NULL DEFAULT 'ACTIVE'
               CONSTRAINT notes_status_valid CHECK (status IN ('ACTIVE', 'COMPLETED', 'ARCHIVED')),
  recorded_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  concluded_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_notes_status_time
  ON notes (status, recorded_at DESC);

CREATE INDEX IF NOT EXISTS idx_notes_category_time
  ON notes (category_id, recorded_at DESC);

CREATE TABLE IF NOT EXISTS note_items (
  id           BIGSERIAL PRIMARY KEY,
  note_id      BIGINT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  content      TEXT NOT NULL,
  position     INT NOT NULL DEFAULT 0 CHECK (position >= 0),
  is_completed BOOLEAN NOT NULL DEFAULT FALSE,
  completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_note_items_note_position
  ON note_items (note_id, position, id);

CREATE TABLE IF NOT EXISTS wishes (
  id                       BIGSERIAL PRIMARY KEY,
  name                     TEXT NOT NULL,
  description              TEXT,
  category_id              INT REFERENCES categories(id) ON DELETE SET NULL,
  target_amount            NUMERIC(14,2) CHECK (target_amount IS NULL OR target_amount > 0),
  priority                 SMALLINT CHECK (priority IS NULL OR priority BETWEEN 1 AND 5),
  status                   VARCHAR(16) NOT NULL DEFAULT 'ACTIVE'
                           CHECK (status IN ('ACTIVE', 'PURCHASED', 'CANCELLED', 'ARCHIVED')),
  fulfilled_transaction_id BIGINT UNIQUE REFERENCES transactions(id),
  source_text              TEXT NOT NULL,
  created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  fulfilled_at             TIMESTAMPTZ,
  CHECK (
    (status = 'PURCHASED' AND fulfilled_transaction_id IS NOT NULL AND fulfilled_at IS NOT NULL)
    OR
    (status <> 'PURCHASED' AND fulfilled_transaction_id IS NULL AND fulfilled_at IS NULL)
  )
);

CREATE INDEX IF NOT EXISTS idx_wishes_status_time
  ON wishes (status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_wishes_category_status
  ON wishes (category_id, status);
