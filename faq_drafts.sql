-- faq_drafts.sql
CREATE TABLE IF NOT EXISTS faq_drafts (
    faq_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    source_ticket_ids TEXT NOT NULL, -- comma‑separated list of ticket IDs
    status TEXT NOT NULL CHECK(status IN ('pending','approved','rejected')),
    cluster_id INTEGER,
    confidence_score INTEGER DEFAULT 0
);
