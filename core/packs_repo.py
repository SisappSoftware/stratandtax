import sqlite3
from datetime import datetime
from core.db import get_db


def save_generated_pack(
    user_id: int,
    pack_id: str,
    zip_name: str,
    zip_path: str,
    email_sent: bool,
    email_error: str | None
):
    conn = get_db()
    conn.execute(
        """
        INSERT INTO generated_packs
        (user_id, pack_id, zip_name, zip_path, email_sent, email_error, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            pack_id,
            zip_name,
            zip_path,
            int(email_sent),
            email_error,
            datetime.utcnow().isoformat()
        )
    )
    conn.commit()


def get_user_packs(user_id: int):
    conn = get_db()
    cur = conn.execute(
        """
        SELECT id, pack_id, zip_name, email_sent, email_error, created_at
        FROM generated_packs
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id,)
    )
    return [dict(row) for row in cur.fetchall()]
