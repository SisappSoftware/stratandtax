import logging
from typing import List, Dict, Optional
from core.db import get_db

logger = logging.getLogger(__name__)


# =========================================================
# GUARDAR PACK GENERADO
# =========================================================
def save_generated_pack(
    user_id: int,
    pack_id: str,
    zip_name: str,
    zip_path: str,
    email_sent: bool,
    email_error: Optional[str]
):
    logger.info(
        "save_generated_pack START user_id=%s pack_id=%s zip_name=%s",
        user_id,
        pack_id,
        zip_name
    )

    try:
        conn = get_db()
        logger.info("DB connection acquired")

        conn.execute(
            """
            INSERT INTO generated_packs (
                user_id,
                pack_id,
                zip_name,
                zip_path,
                email_sent,
                email_error,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (
                user_id,
                pack_id,
                zip_name,
                zip_path,
                int(email_sent),
                email_error
            )
        )

        conn.commit()
        logger.info("save_generated_pack COMMIT OK")

    except Exception:
        logger.exception("save_generated_pack FAILED")
        raise


# =========================================================
# OBTENER PACKS DE UN USUARIO
# =========================================================
def get_user_packs(user_id: int) -> List[Dict]:
    logger.info("get_user_packs START user_id=%s", user_id)

    try:
        conn = get_db()
        cur = conn.execute(
            """
            SELECT
                id,
                pack_id,
                zip_name,
                zip_path,
                email_sent,
                email_error,
                created_at
            FROM generated_packs
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,)
        )

        rows = cur.fetchall()
        logger.info("get_user_packs rows=%s", len(rows))

        return [
            {
                "id": row["id"],
                "pack_id": row["pack_id"],
                "zip_name": row["zip_name"],
                "zip_path": row["zip_path"],
                "email_sent": bool(row["email_sent"]),
                "email_error": row["email_error"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    except Exception:
        logger.exception("get_user_packs FAILED")
        raise


# =========================================================
# OBTENER TODOS LOS PACKS (SUPERADMIN)
# =========================================================
def get_all_packs() -> List[Dict]:
    logger.info("get_all_packs START")

    try:
        conn = get_db()
        cur = conn.execute(
            """
            SELECT
                gp.id,
                gp.user_id,
                u.email as user_email,
                gp.pack_id,
                gp.zip_name,
                gp.zip_path,
                gp.email_sent,
                gp.email_error,
                gp.created_at
            FROM generated_packs gp
            JOIN users u ON u.id = gp.user_id
            ORDER BY gp.created_at DESC
            """
        )

        rows = cur.fetchall()
        logger.info("get_all_packs rows=%s", len(rows))

        return [
            {
                "id": row["id"],
                "user_id": row["user_id"],
                "user_email": row["user_email"],
                "pack_id": row["pack_id"],
                "zip_name": row["zip_name"],
                "zip_path": row["zip_path"],
                "email_sent": bool(row["email_sent"]),
                "email_error": row["email_error"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    except Exception:
        logger.exception("get_all_packs FAILED")
        raise
