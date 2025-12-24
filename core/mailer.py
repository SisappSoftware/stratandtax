import os
import smtplib
import logging
from email.message import EmailMessage

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

DISABLE_EMAIL = os.getenv("DISABLE_EMAIL") == "true"


def send_zip_email(to_email: str, zip_path: str, zip_filename: str):
    logger.info(
        "send_zip_email START to_email=%s zip_path=%s zip_filename=%s",
        to_email,
        zip_path,
        zip_filename
    )

    logger.info(
        "SMTP config host=%s port=%s user=%s disable_email=%s",
        SMTP_HOST,
        SMTP_PORT,
        SMTP_USER,
        DISABLE_EMAIL
    )

    if DISABLE_EMAIL:
        logger.warning("Email disabled via DISABLE_EMAIL")
        return {"sent": False, "error": "Email disabled"}

    try:
        if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS]):
            logger.error("SMTP not fully configured")
            return {"sent": False, "error": "SMTP not configured"}

        if not os.path.exists(zip_path):
            logger.error("ZIP not found at %s", zip_path)
            return {"sent": False, "error": "ZIP not found"}

        msg = EmailMessage()
        msg["Subject"] = "Documentación generada"
        msg["From"] = SMTP_USER
        msg["To"] = to_email
        msg.set_content("Se adjunta el paquete de documentos generado.")

        with open(zip_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="zip",
                filename=zip_filename
            )

        with smtplib.SMTP(SMTP_HOST, int(SMTP_PORT), timeout=30) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        logger.info("Email sent successfully")
        return {"sent": True, "error": None}

    except Exception:
        logger.exception("send_zip_email FAILED")
        return {"sent": False, "error": "exception"}
