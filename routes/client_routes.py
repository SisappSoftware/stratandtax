from flask import Blueprint, jsonify, request
from core.permissions import require_auth
from core.templates import list_forms, get_form_schema
import sqlite3
import os

bp = Blueprint("client", __name__, url_prefix="/client")

DB_PATH = os.getenv("DB_PATH", "db/app.db")


@bp.get("/forms")
@require_auth
def client_forms():
    """
    Lista los formularios disponibles para el cliente
    """
    return jsonify(list_forms())


@bp.get("/forms/<form_id>")
@require_auth
def client_form_schema(form_id):
    """
    Devuelve el schema.json de un formulario
    """
    schema = get_form_schema(form_id)
    if not schema:
        return jsonify({"error": "Formulario no encontrado"}), 404
    return jsonify(schema)


@bp.get("/documents")
@require_auth
def client_documents():
    """
    Devuelve el historial de documentos del usuario logueado
    """
    user_id = request.user["id"]

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT
            id,
            template_type,
            filename,
            created_at
        FROM documents
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id,)
    ).fetchall()

    conn.close()

    return jsonify([dict(r) for r in rows])

@bp.post("/generate")
@require_auth
def client_generate():
    """
    Genera un documento para el usuario logueado
    """
    payload = request.get_json() or {}

    template_type = payload.get("template_type")
    data = payload.get("data")
    output_prefix = payload.get("output_prefix", template_type)

    if not template_type or not isinstance(data, dict):
        return jsonify({"error": "Datos inválidos"}), 400

    # Importamos la lógica existente
    from core.generator import generate_document

    try:
        result = generate_document(
            template_type=template_type,
            data=data,
            output_prefix=output_prefix,
            user_id=request.user["id"]  # 👈 CLAVE
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
