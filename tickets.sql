-- tickets.sql
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id INTEGER PRIMARY KEY,
    issue TEXT NOT NULL,
    resolution TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('open','closed')),
    raised_at TEXT,
    closed_at TEXT
);
