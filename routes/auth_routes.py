from flask import Blueprint, request, jsonify
from core.auth import get_user_by_email, verify_password, issue_token, get_user_by_id, decode_token

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("username") or payload.get("email") or "").strip().lower()
    password = (payload.get("password") or "").strip()

    user = get_user_by_email(email)
    if not user or not user.get("active"):
        return jsonify({"error": "Credenciales inválidas"}), 401

    if not verify_password(password, user["password_hash"]):
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = issue_token(user)
    return jsonify({"token": token, "role": user["role"], "email": user["email"]})


@bp.get("/me")
def me():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "No autorizado"}), 401
    token = auth.split(" ", 1)[1].strip()

    try:
        claims = decode_token(token)
        user = get_user_by_id(int(claims["sub"]))
        if not user or not user.get("active"):
            return jsonify({"error": "No autorizado"}), 401
        return jsonify({"id": user["id"], "email": user["email"], "role": user["role"]})
    except Exception:
        return jsonify({"error": "No autorizado"}), 401
