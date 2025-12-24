import logging
from core.db import get_db

logger = logging.getLogger(__name__)


def save_generated_pack(
    user_id: int,
    pack_id: str,
    zip_name: str,
    zip_path: str,
    email_sent: bool,
    email_error: str | None
):
    logger.info(
        "save_generated_pack START user_id=%s pack_id=%s zip_name=%s",
        user_id,
        pack_id,
        zip_name
    )

    logger.info(
        "Pack metadata zip_path=%s email_sent=%s email_error=%s",
        zip_path,
        email_sent,
        email_error
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
                email_error
            )
            VALUES (?, ?, ?, ?, ?, ?)
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

        logger.info("Insert executed, committing")
        conn.commit()
        logger.info("Commit successful")

    except Exception:
        logger.exception("save_generated_pack FAILED")
        raise
