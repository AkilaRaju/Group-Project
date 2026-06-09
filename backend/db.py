# backend/db.py
"""SQLite helper utilities for the Ticket‑to‑FAQ app.
All functions open a connection, perform the operation, and close the connection.
"""
import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "tickets.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

# ---------- Ticket helpers ----------
def get_all_closed_tickets():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM tickets WHERE status='closed'", conn)
    conn.close()
    return df

# ---------- FAQ draft helpers ----------
def insert_faq_draft(question: str, answer: str, source_ticket_ids, cluster_id: int, confidence_score: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO faq_drafts (question, answer, source_ticket_ids, status, cluster_id, confidence_score) VALUES (?,?,?,?,?,?)",
        (question, answer, ",".join(map(str, source_ticket_ids)), "pending", cluster_id, confidence_score),
    )
    conn.commit()
    conn.close()

def get_faq_drafts_by_status(status: str):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM faq_drafts WHERE status = ?", conn, params=(status,))
    conn.close()
    return df

def update_faq_draft(faq_id: int, question: str = None, answer: str = None, status: str = None):
    conn = get_connection()
    cur = conn.cursor()
    if question is not None:
        cur.execute("UPDATE faq_drafts SET question = ? WHERE faq_id = ?", (question, faq_id))
        cur.execute("UPDATE published_faqs SET question = ? WHERE faq_id = ?", (question, faq_id))
    if answer is not None:
        cur.execute("UPDATE faq_drafts SET answer = ? WHERE faq_id = ?", (answer, faq_id))
        cur.execute("UPDATE published_faqs SET answer = ? WHERE faq_id = ?", (answer, faq_id))
    if status is not None:
        cur.execute("UPDATE faq_drafts SET status = ? WHERE faq_id = ?", (status, faq_id))
        if status in ('rejected', 'pending'):
            cur.execute("DELETE FROM published_faqs WHERE faq_id = ?", (faq_id,))
    conn.commit()
    conn.close()

def publish_faq(faq_id: int):
    conn = get_connection()
    cur = conn.cursor()
    # Copy to published_faqs table (idempotent replace) including confidence_score
    cur.execute(
        "INSERT OR REPLACE INTO published_faqs (faq_id, question, answer, source_ticket_ids, confidence_score)"
        " SELECT faq_id, question, answer, source_ticket_ids, confidence_score FROM faq_drafts WHERE faq_id = ?",
        (faq_id,)
    )
    # Mark as approved in drafts
    cur.execute("UPDATE faq_drafts SET status = 'approved' WHERE faq_id = ?", (faq_id,))
    conn.commit()
    conn.close()

# ---------- Published FAQ helpers ----------
def get_published_faqs():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM published_faqs", conn)
    conn.close()
    return df

# ---------- Customer & Agent flow helpers ----------
def insert_ticket(issue: str, resolution: str = "", status: str = "open", raised_at: str = None):
    import datetime
    if raised_at is None:
        raised_at = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tickets (issue, resolution, status, raised_at, closed_at) VALUES (?, ?, ?, ?, ?)",
        (issue, resolution, status, raised_at, "")
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_open_tickets():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM tickets WHERE status='open'", conn)
    conn.close()
    return df

def close_ticket(ticket_id: int, resolution: str):
    import datetime
    closed_at = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE tickets SET status='closed', resolution=?, closed_at=? WHERE ticket_id=?",
        (resolution, closed_at, ticket_id)
    )
    conn.commit()
    conn.close()
