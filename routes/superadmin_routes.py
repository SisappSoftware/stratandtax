from flask import Blueprint, jsonify, request
from core.permissions import require_superadmin
import sqlite3
import os

bp = Blueprint("superadmin", __name__, url_prefix="/admin")

DB_PATH = os.getenv("DB_PATH", "db/app.db")


@bp.get("/users")
@require_superadmin
def list_users():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, email, role, active, created_at FROM users ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@bp.post("/users")
@require_superadmin
def create_user_admin():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not email or not password:
        return jsonify({"error": "Datos inválidos"}), 400

    from core.auth import create_user
    try:
        uid = create_user(email, password, role=role)
        return jsonify({"ok": True, "user_id": uid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.get("/documents")
@require_superadmin
def list_documents():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT d.id, u.email, d.template_type, d.filename, d.created_at
        FROM documents d
        JOIN users u ON u.id = d.user_id
        ORDER BY d.created_at DESC
        """
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])
