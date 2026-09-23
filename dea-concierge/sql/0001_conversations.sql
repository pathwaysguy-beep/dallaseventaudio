-- Bundle 62: every concierge conversation is kept, not only finished leads.
-- Run once against the production database:
--   cd ~/dallaseventaudio/dea-concierge
--   npx wrangler d1 execute DB --remote --yes --file=sql/0001_conversations.sql
-- Safe to run twice; every statement is IF NOT EXISTS.

CREATE TABLE IF NOT EXISTS conversations (
  id          TEXT PRIMARY KEY,           -- random id the widget makes on the first message
  day         TEXT NOT NULL,              -- Dallas calendar day of the latest message, YYYY-MM-DD
  started_at  TEXT NOT NULL,              -- ISO time of the first message
  updated_at  TEXT NOT NULL,              -- ISO time of the latest message
  page        TEXT,                       -- path the visitor was on when the chat started
  last_page   TEXT,                       -- path of the latest message
  turns       INTEGER NOT NULL DEFAULT 0, -- visitor messages so far
  ended       INTEGER NOT NULL DEFAULT 0, -- 1 once the model closed the session
  lead        INTEGER NOT NULL DEFAULT 0, -- 1 once a name and contact were captured
  errored     INTEGER NOT NULL DEFAULT 0, -- 1 if any turn got the friendly error reply
  transcript  TEXT NOT NULL               -- JSON array of {role, content}
);
CREATE INDEX IF NOT EXISTS conversations_day ON conversations(day);

-- One row per digest email so a cron that fires twice sends once.
CREATE TABLE IF NOT EXISTS digests (
  day            TEXT PRIMARY KEY,
  sent_at        TEXT NOT NULL,
  conversations  INTEGER NOT NULL,
  summary        TEXT
);
