"""
Content Deduplication & History Database
Tracks processed YouTube videos, sermon quotes, and dispatches in SQLite
to ensure 0% repetition across consecutive days (30-day deduplication window).
"""

import hashlib
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "gospel_history.db"

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                channel TEXT NOT NULL,
                published_at TEXT,
                processed_date TEXT NOT NULL,
                view_velocity TEXT
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                quote_hash TEXT PRIMARY KEY,
                quote_text TEXT NOT NULL,
                speaker TEXT NOT NULL,
                scripture TEXT,
                used_date TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dispatches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dispatch_date TEXT NOT NULL,
                subject TEXT NOT NULL,
                recipient TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );
        """)
        conn.commit()

def hash_text(text: str) -> str:
    cleaned = "".join(ch.lower() for ch in text if ch.isalnum())
    return hashlib.sha256(cleaned.encode("utf-8")).hexdigest()

def is_video_processed(video_id: str) -> bool:
    init_db()
    with get_connection() as conn:
        cur = conn.execute("SELECT 1 FROM videos WHERE video_id = ?", (video_id,))
        return cur.fetchone() is not None

def is_quote_used_recently(quote_text: str, days: int = 30) -> bool:
    init_db()
    q_hash = hash_text(quote_text)
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT 1 FROM quotes WHERE quote_hash = ? AND used_date >= ?",
            (q_hash, cutoff)
        )
        return cur.fetchone() is not None

def record_video(video_id: str, title: str, channel: str, published_at: str = None, view_velocity: str = None):
    init_db()
    today = datetime.now().strftime("%Y-%m-%d")
    with get_connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO videos (video_id, title, channel, published_at, processed_date, view_velocity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (video_id, title, channel, published_at, today, view_velocity))
        conn.commit()

def record_quote(quote_text: str, speaker: str, scripture: str = None):
    init_db()
    q_hash = hash_text(quote_text)
    today = datetime.now().strftime("%Y-%m-%d")
    with get_connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO quotes (quote_hash, quote_text, speaker, scripture, used_date)
            VALUES (?, ?, ?, ?, ?)
        """, (q_hash, quote_text, speaker, scripture, today))
        conn.commit()

def record_dispatch(subject: str, recipient: str, status: str = "SUCCESS"):
    init_db()
    now_iso = datetime.now().isoformat()
    today = datetime.now().strftime("%Y-%m-%d")
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO dispatches (dispatch_date, subject, recipient, status, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (today, subject, recipient, status, now_iso))
        conn.commit()

def get_stats():
    init_db()
    with get_connection() as conn:
        v_count = conn.execute("SELECT COUNT(*) FROM videos").fetchone()[0]
        q_count = conn.execute("SELECT COUNT(*) FROM quotes").fetchone()[0]
        d_count = conn.execute("SELECT COUNT(*) FROM dispatches").fetchone()[0]
        return {
            "archived_videos": v_count,
            "archived_quotes": q_count,
            "total_dispatches": d_count
        }

if __name__ == "__main__":
    init_db()
    stats = get_stats()
    print(f"[DATABASE INITIALIZED] {stats}")
