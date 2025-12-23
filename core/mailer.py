import smtplib
import os
from email.message import EmailMessage


print("DEBUG SMTP_USER:", os.getenv("SMTP_USER"))
print("DEBUG SMTP_PASS:", os.getenv("SMTP_PASS"))
print("DEBUG SMTP_HOST:", os.getenv("SMTP_HOST"))
print("DEBUG SMTP_PORT:", os.getenv("SMTP_PORT"))

def send_zip_email(to_email: str, zip_path: str):
    """
    Envía un ZIP por email.
    No lanza excepción: devuelve dict con status.
    """

    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")

    if not SMTP_USER or not SMTP_PASS:
        return {"sent": False, "error": "SMTP no configurado"}

    msg = EmailMessage()
    msg["Subject"] = "Documentación generada"
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg.set_content(
        "Hola,\n\nAdjuntamos el paquete de documentos generado automáticamente.\n\nSaludos."
    )

    try:
        with open(zip_path, "rb") as f:
            zip_data = f.read()

        msg.add_attachment(
            zip_data,
            maintype="application",
            subtype="zip",
            filename=os.path.basename(zip_path)
        )

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        return {"sent": True, "error": None}

    except Exception as e:
        return {"sent": False, "error": str(e)}
