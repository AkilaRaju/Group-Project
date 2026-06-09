# backend/init_db.py
"""Initialises the SQLite database using the schema .sql files.
Run once after cloning the project.
"""
import sqlite3
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "tickets.db")

SCHEMAS = [
    Path(__file__).parents[1] / "tickets.sql",
    Path(__file__).parents[1] / "faq_drafts.sql",
    Path(__file__).parents[1] / "published_faqs.sql",
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for schema_path in SCHEMAS:
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        with open(schema_path, "r", encoding="utf-8") as f:
            cur.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"Database initialised at {DB_PATH}")

if __name__ == "__main__":
    init_db()
