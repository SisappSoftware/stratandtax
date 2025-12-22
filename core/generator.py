import os
import uuid
import sqlite3
from datetime import datetime
from docx import Document

# ===============================
# CONFIGURACIÓN
# ===============================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

TEMPLATES_DIR = os.path.join(BASE_DIR, "plantillas")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "db", "app.db"))

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ===============================
# UTILIDADES
# ===============================

def replace_placeholders(doc: Document, data: dict) -> int:
    """
    Reemplaza placeholders ${CLAVE} en el documento.
    Devuelve cuántos reemplazos se hicieron.
    """
    replaced = 0

    def _replace_in_paragraph(paragraph):
        nonlocal replaced
        for key, value in data.items():
            placeholder = f"${{{key}}}"
            if placeholder in paragraph.text:
                paragraph.text = paragraph.text.replace(placeholder, str(value))
                replaced += 1

    for p in doc.paragraphs:
        _replace_in_paragraph(p)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    _replace_in_paragraph(p)

    return replaced


# ===============================
# FUNCIÓN PRINCIPAL
# ===============================

def generate_document(template_type: str, data: dict, output_prefix: str, user_id: int):
    """
    Genera un documento Word a partir de una plantilla
    y guarda el registro en la base de datos.
    """

    # -------- paths --------
    template_dir = os.path.join(TEMPLATES_DIR, template_type)
    template_path = os.path.join(template_dir, "solicitud.docx")

    if not os.path.isfile(template_path):
        raise FileNotFoundError("Plantilla no encontrada")

    # -------- abrir docx --------
    doc = Document(template_path)

    replaced_count = replace_placeholders(doc, data)

    # -------- nombre archivo --------
    uid = uuid.uuid4().hex
    filename = f"{output_prefix}_{uid}.docx"
    output_path = os.path.join(OUTPUT_DIR, filename)

    doc.save(output_path)

    # -------- guardar en DB --------
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO documents (
            user_id,
            template_type,
            filename,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            template_type,
            filename,
            datetime.utcnow().isoformat()
        )
    )

    conn.commit()
    conn.close()

    # -------- respuesta --------
    return {
        "ok": True,
        "filename": filename,
        "download_url": f"/download/{filename}",
        "summary": {
            "replaced_count": replaced_count,
            "keys": list(data.keys())
        }
    }
