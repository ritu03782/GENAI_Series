
import json
import sqlite3
from datetime import datetime

DB_PATH = "blog_history.db"


def connect():
    """Create a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    """Create the blogs table if it does not exist."""
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS blogs (
                thread_id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                audience TEXT,
                stage TEXT,
                review_payload TEXT,
                final_blog TEXT,
                history TEXT,
                updated_at TEXT NOT NULL
            )
            """
        )


def save_blog(session):
    """Insert a blog or update its existing record."""
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO blogs (
                thread_id,
                topic,
                audience,
                stage,
                review_payload,
                final_blog,
                history,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(thread_id) DO UPDATE SET
                topic = excluded.topic,
                audience = excluded.audience,
                stage = excluded.stage,
                review_payload = excluded.review_payload,
                final_blog = excluded.final_blog,
                history = excluded.history,
                updated_at = excluded.updated_at
            """,
            (
                session["thread_id"],
                session.get("topic", "Untitled blog"),
                session.get("audience", ""),
                session.get("stage", "setup"),
                json.dumps(session.get("review_payload")),
                session.get("final_blog", ""),
                json.dumps(session.get("history", [])),
                datetime.now().isoformat(timespec="seconds"),
            ),
        )


def list_blogs():
    """Return saved blogs, newest first."""
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT thread_id, topic, stage, updated_at
            FROM blogs
            ORDER BY updated_at DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def load_blog(thread_id):
    """Load one blog and restore its JSON fields."""
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM blogs WHERE thread_id = ?",
            (thread_id,),
        ).fetchone()

    if row is None:
        return None

    blog = dict(row)

    blog["review_payload"] = json.loads(
        blog["review_payload"] or "null"
    )
    blog["history"] = json.loads(
        blog["history"] or "[]"
    )

    return blog


def delete_blog(thread_id):
    """Delete a saved blog."""
    with connect() as conn:
        conn.execute(
            "DELETE FROM blogs WHERE thread_id = ?",
            (thread_id,),
        )

