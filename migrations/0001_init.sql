-- Requires: CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS personas (
  id            TEXT PRIMARY KEY,
  name          TEXT NOT NULL,
  archetype     TEXT,
  traits        JSONB DEFAULT '{}'::jsonb,
  weight        DOUBLE PRECISION DEFAULT 1.0,
  created_at    TIMESTAMPTZ DEFAULT now(),
  updated_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS studies (
  id            TEXT PRIMARY KEY,
  title         TEXT NOT NULL,
  objective     TEXT,
  config        JSONB DEFAULT '{}'::jsonb,
  created_at    TIMESTAMPTZ DEFAULT now(),
  updated_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sessions (
  id            TEXT PRIMARY KEY,
  study_id      TEXT NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
  status        TEXT NOT NULL,
  meta          JSONB DEFAULT '{}'::jsonb,
  started_at    TIMESTAMPTZ,
  finished_at   TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS messages (
  id            TEXT PRIMARY KEY,
  session_id    TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  role          TEXT NOT NULL,
  persona_id    TEXT REFERENCES personas(id),
  content       TEXT NOT NULL,
  meta          JSONB DEFAULT '{}'::jsonb,
  created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS insights (
  id            TEXT PRIMARY KEY,
  study_id      TEXT NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
  title         TEXT NOT NULL,
  summary_md    TEXT NOT NULL,
  tags          TEXT[] DEFAULT '{}',
  score         DOUBLE PRECISION,
  meta          JSONB DEFAULT '{}'::jsonb,
  created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS message_embeddings (
  id            TEXT PRIMARY KEY,
  study_id      TEXT NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
  embedding     VECTOR(1536),
  meta          JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_msg_embed_ann
  ON message_embeddings USING ivfflat (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS persona_rollups (
  study_id      TEXT NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
  persona_id    TEXT NOT NULL REFERENCES personas(id) ON DELETE CASCADE,
  metric        TEXT NOT NULL,
  value         DOUBLE PRECISION NOT NULL,
  PRIMARY KEY (study_id, persona_id, metric)
);
