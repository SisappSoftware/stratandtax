import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename

from core.permissions import require_superadmin
from core.templates import (
    ensure_templates_dir,
    list_forms,
    get_form_schema,
    save_schema,
    set_active,
    has_docx,
)

bp = Blueprint("admin_templates", __name__, url_prefix="/admin/templates")


def _template_dir(tid: str) -> str:
    return os.path.join("plantillas", tid)


def _docx_path(tid: str) -> str:
    return os.path.join(_template_dir(tid), "solicitud.docx")


@bp.get("")
@require_superadmin
def admin_list_templates():
    """
    Lista todas las plantillas (activas e inactivas)
    """
    return jsonify(list_forms(active_only=False))


@bp.get("/<template_id>")
@require_superadmin
def admin_get_template(template_id):
    """
    Devuelve schema + meta básico.
    """
    schema = get_form_schema(template_id)
    if not schema:
        return jsonify({"error": "Plantilla no encontrada"}), 404

    # devolvemos schema; el listado ya trae active/updated_at
    return jsonify({"id": template_id, "schema": schema})


@bp.get("/<template_id>/docx")
@require_superadmin
def admin_download_docx(template_id):
    """
    Descarga el docx de una plantilla
    """
    path = _docx_path(template_id)
    if not os.path.isfile(path):
        return jsonify({"error": "DOCX no encontrado"}), 404
    return send_file(path, as_attachment=True, download_name=f"{template_id}.docx")


@bp.post("")
@require_superadmin
def admin_create_template():
    """
    Crea una plantilla nueva.
    Espera multipart/form-data:
      - template_id (string)
      - schema_json (string JSON)
      - docx (file .docx)
      - active (optional: "true"/"false")
    """
    ensure_templates_dir()

    template_id = (request.form.get("template_id") or "").strip()
    schema_json = (request.form.get("schema_json") or "").strip()
    active_raw = (request.form.get("active") or "true").strip().lower()
    active = active_raw in ("1", "true", "yes", "y", "on")

    if not template_id:
        return jsonify({"error": "template_id requerido"}), 400

    # seguridad: id solo con letras, números, guion y underscore
    safe_id = secure_filename(template_id).replace("-", "_")
    if not safe_id:
        return jsonify({"error": "template_id inválido"}), 400

    try:
        schema = json.loads(schema_json) if schema_json else None
    except Exception:
        return jsonify({"error": "schema_json inválido (JSON)"}), 400

    if not isinstance(schema, dict) or "fields" not in schema:
        return jsonify({"error": "schema_json debe ser objeto con 'fields'"}), 400

    file = request.files.get("docx")
    if not file or not file.filename.lower().endswith(".docx"):
        return jsonify({"error": "docx (.docx) requerido"}), 400

    os.makedirs(_template_dir(safe_id), exist_ok=True)

    # guardar schema
    save_schema(safe_id, schema)

    # guardar docx
    file.save(_docx_path(safe_id))

    # activar/desactivar
    set_active(safe_id, active)

    return jsonify({"ok": True, "id": safe_id})


@bp.put("/<template_id>")
@require_superadmin
def admin_update_template(template_id):
    """
    Actualiza schema y/o docx y/o active.
    multipart/form-data:
      - schema_json (optional)
      - docx (optional file)
      - active (optional)
    """
    template_id = secure_filename(template_id).replace("-", "_")
    if not template_id:
        return jsonify({"error": "ID inválido"}), 400

    if not os.path.isdir(_template_dir(template_id)):
        return jsonify({"error": "Plantilla no encontrada"}), 404

    schema_json = (request.form.get("schema_json") or "").strip()
    active_raw = request.form.get("active")

    if schema_json:
        try:
            schema = json.loads(schema_json)
        except Exception:
            return jsonify({"error": "schema_json inválido (JSON)"}), 400
        if not isinstance(schema, dict) or "fields" not in schema:
            return jsonify({"error": "schema_json debe ser objeto con 'fields'"}), 400
        save_schema(template_id, schema)

    file = request.files.get("docx")
    if file:
        if not file.filename.lower().endswith(".docx"):
            return jsonify({"error": "docx debe ser .docx"}), 400
        file.save(_docx_path(template_id))

    if active_raw is not None:
        active = str(active_raw).strip().lower() in ("1", "true", "yes", "y", "on")
        set_active(template_id, active)

    return jsonify({"ok": True, "id": template_id, "has_docx": has_docx(template_id)})


@bp.delete("/<template_id>")
@require_superadmin
def admin_delete_template(template_id):
    """
    Soft delete: desactiva la plantilla (no borra archivos).
    """
    template_id = secure_filename(template_id).replace("-", "_")
    if not template_id:
        return jsonify({"error": "ID inválido"}), 400

    if not os.path.isdir(_template_dir(template_id)):
        return jsonify({"error": "Plantilla no encontrada"}), 404

    set_active(template_id, False)
    return jsonify({"ok": True, "id": template_id, "active": False})
