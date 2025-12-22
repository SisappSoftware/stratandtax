import os
import json
from datetime import datetime

TEMPLATES_DIR = "plantillas"


def _template_dir(template_id: str) -> str:
    return os.path.join(TEMPLATES_DIR, template_id)


def _meta_path(template_id: str) -> str:
    return os.path.join(_template_dir(template_id), "meta.json")


def _schema_path(template_id: str) -> str:
    return os.path.join(_template_dir(template_id), "schema.json")


def _docx_path(template_id: str) -> str:
    return os.path.join(_template_dir(template_id), "solicitud.docx")


def ensure_templates_dir() -> None:
    os.makedirs(TEMPLATES_DIR, exist_ok=True)


def read_meta(template_id: str) -> dict:
    mp = _meta_path(template_id)
    if not os.path.isfile(mp):
        # por compatibilidad: si no hay meta, asumimos active=true
        return {"active": True, "created_at": None, "updated_at": None}
    try:
        with open(mp, "r", encoding="utf-8") as f:
            return json.load(f) or {"active": True}
    except Exception:
        return {"active": True}


def write_meta(template_id: str, active: bool) -> dict:
    ensure_templates_dir()
    meta = read_meta(template_id)
    now = datetime.utcnow().isoformat()
    if not meta.get("created_at"):
        meta["created_at"] = now
    meta["updated_at"] = now
    meta["active"] = bool(active)

    os.makedirs(_template_dir(template_id), exist_ok=True)
    with open(_meta_path(template_id), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return meta


def list_forms(active_only: bool = True) -> list:
    """
    Lista plantillas para clientes.
    - active_only=True: devuelve solo activas (para /client/forms)
    """
    ensure_templates_dir()
    forms = []

    for folder in os.listdir(TEMPLATES_DIR):
        form_path = os.path.join(TEMPLATES_DIR, folder)
        if not os.path.isdir(form_path):
            continue

        schema_p = os.path.join(form_path, "schema.json")
        docx_p = os.path.join(form_path, "solicitud.docx")

        if not (os.path.isfile(schema_p) and os.path.isfile(docx_p)):
            continue

        meta = read_meta(folder)
        if active_only and not meta.get("active", True):
            continue

        try:
            with open(schema_p, "r", encoding="utf-8") as f:
                schema = json.load(f)
        except Exception:
            continue

        forms.append({
            "id": folder,
            "label": schema.get("label", folder),
            "description": schema.get("description", ""),
            "active": bool(meta.get("active", True)),
            "updated_at": meta.get("updated_at"),
        })

    # orden: activos arriba, luego por label
    forms.sort(key=lambda x: (not x.get("active", True), (x.get("label") or "").lower()))
    return forms


def get_form_schema(form_id: str) -> dict | None:
    sp = _schema_path(form_id)
    if not os.path.isfile(sp):
        return None
    try:
        with open(sp, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_schema(form_id: str, schema: dict) -> None:
    os.makedirs(_template_dir(form_id), exist_ok=True)
    with open(_schema_path(form_id), "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)


def has_docx(form_id: str) -> bool:
    return os.path.isfile(_docx_path(form_id))


def set_active(form_id: str, active: bool) -> dict:
    return write_meta(form_id, active=active)
