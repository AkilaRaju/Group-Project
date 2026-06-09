-- published_faqs.sql
CREATE TABLE IF NOT EXISTS published_faqs (
    faq_id INTEGER PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    source_ticket_ids TEXT NOT NULL,
    confidence_score INTEGER DEFAULT 0
);
