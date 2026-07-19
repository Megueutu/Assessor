BEGIN;

CREATE UNIQUE INDEX IF NOT EXISTS uq_categories_name ON categories (LOWER(name));
CREATE UNIQUE INDEX IF NOT EXISTS uq_transaction_types_type ON transaction_types (UPPER(type));

ALTER TABLE transactions
  ALTER COLUMN occurred_at SET DEFAULT NOW();

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'transactions_amount_positive') THEN
    ALTER TABLE transactions
      ADD CONSTRAINT transactions_amount_positive CHECK (amount > 0);
  END IF;
END $$;

ALTER TABLE notes ADD COLUMN IF NOT EXISTS title TEXT;
ALTER TABLE notes ADD COLUMN IF NOT EXISTS category_id INT REFERENCES categories(id) ON DELETE SET NULL;
ALTER TABLE notes ADD COLUMN IF NOT EXISTS status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE';
ALTER TABLE notes ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'notes' AND column_name = 'concluded'
  ) THEN
    UPDATE notes
    SET status = CASE WHEN concluded THEN 'COMPLETED' ELSE 'ACTIVE' END,
        updated_at = COALESCE(concluded_at, recorded_at, NOW())
    WHERE status = 'ACTIVE';
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'notes_status_valid') THEN
    ALTER TABLE notes
      ADD CONSTRAINT notes_status_valid CHECK (status IN ('ACTIVE', 'COMPLETED', 'ARCHIVED'));
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS note_items (
  id BIGSERIAL PRIMARY KEY,
  note_id BIGINT NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  position INT NOT NULL DEFAULT 0 CHECK (position >= 0),
  is_completed BOOLEAN NOT NULL DEFAULT FALSE,
  completed_at TIMESTAMPTZ
);

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'notes' AND column_name = 'items'
  ) THEN
    INSERT INTO note_items (note_id, content, position)
    SELECT n.id, item.content, item.ordinality - 1
    FROM notes n
    CROSS JOIN LATERAL UNNEST(COALESCE(n.items, ARRAY[]::TEXT[])) WITH ORDINALITY AS item(content, ordinality)
    WHERE NOT EXISTS (SELECT 1 FROM note_items ni WHERE ni.note_id = n.id);
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS wishes (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  category_id INT REFERENCES categories(id) ON DELETE SET NULL,
  target_amount NUMERIC(14,2) CHECK (target_amount IS NULL OR target_amount > 0),
  priority SMALLINT CHECK (priority IS NULL OR priority BETWEEN 1 AND 5),
  status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE'
    CHECK (status IN ('ACTIVE', 'PURCHASED', 'CANCELLED', 'ARCHIVED')),
  fulfilled_transaction_id BIGINT UNIQUE REFERENCES transactions(id),
  source_text TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  fulfilled_at TIMESTAMPTZ,
  CHECK (
    (status = 'PURCHASED' AND fulfilled_transaction_id IS NOT NULL AND fulfilled_at IS NOT NULL)
    OR (status <> 'PURCHASED' AND fulfilled_transaction_id IS NULL AND fulfilled_at IS NULL)
  )
);

CREATE INDEX IF NOT EXISTS idx_notes_status_time ON notes (status, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_notes_category_time ON notes (category_id, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_note_items_note_position ON note_items (note_id, position, id);
CREATE INDEX IF NOT EXISTS idx_wishes_status_time ON wishes (status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_wishes_category_status ON wishes (category_id, status);

INSERT INTO categories (name)
VALUES ('eletrônicos')
ON CONFLICT DO NOTHING;

COMMIT;
