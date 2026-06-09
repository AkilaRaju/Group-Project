# backend/data_loader.py
"""Data loading utilities for the Ticket‑to‑FAQ pipeline.
Loads closed tickets from a CSV file (path defined in .env) into the SQLite database.
"""
import os
import pandas as pd
import sqlite3
from dotenv import load_dotenv

load_dotenv()

# Environment variables
CSV_PATH = os.getenv("TICKETS_CSV_PATH")
DB_PATH = os.getenv("DB_PATH", "tickets.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def load_csv_to_db():
    """Read the tickets CSV and insert rows into the `tickets` table.
    Assumes CSV columns: ticket_id, issue, resolution, status.
    """
    if not CSV_PATH or not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV file not found at {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    # Basic validation
    required = {"ticket_id", "issue", "resolution", "status"}
    if not required.issubset(set(df.columns)):
        raise ValueError(f"CSV must contain columns: {required}")
    conn = get_connection()
    # Delete existing tickets to prevent duplicates on rerun
    cur = conn.cursor()
    cur.execute("DELETE FROM tickets")
    conn.commit()
    
    # Standardise status to lowercase to match sqlite CHECK constraint
    df['status'] = df['status'].astype(str).str.strip().str.lower()
    
    # Generate realistic timestamps for historical tickets
    import datetime, random
    now = datetime.datetime.now()
    raised_dates = []
    closed_dates = []
    for i in range(len(df)):
        # subtract between 2 and 10 days
        days_ago = random.randint(2, 10)
        hours_ago = random.randint(0, 23)
        mins_ago = random.randint(0, 59)
        raised = now - datetime.timedelta(days=days_ago, hours=hours_ago, minutes=mins_ago)
        
        # closed between 15 mins and 5 hours later
        delay_mins = random.randint(15, 300)
        closed = raised + datetime.timedelta(minutes=delay_mins)
        
        raised_dates.append(raised.strftime("%d %b %Y, %I:%M %p"))
        closed_dates.append(closed.strftime("%d %b %Y, %I:%M %p"))
        
    df['raised_at'] = raised_dates
    df['closed_at'] = closed_dates
    
    df.to_sql("tickets", conn, if_exists="append", index=False)
    conn.close()
    print(f"Loaded {len(df)} tickets with timestamps into SQLite database at {DB_PATH}")

if __name__ == "__main__":
    load_csv_to_db()

