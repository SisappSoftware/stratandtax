from functools import wraps
from flask import request, jsonify
from core.auth import decode_token


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token requerido"}), 401

        token = auth_header.split(" ", 1)[1]

        try:
            user = decode_token(token)
        except Exception:
            return jsonify({"error": "Token inválido"}), 401

        request.user = user
        return fn(*args, **kwargs)

    return wrapper


def require_user(fn):
    @wraps(fn)
    @require_auth
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper


def require_admin(fn):
    @wraps(fn)
    @require_auth
    def wrapper(*args, **kwargs):
        if request.user["role"] not in ("admin", "superadmin"):
            return jsonify({"error": "Permisos insuficientes"}), 403
        return fn(*args, **kwargs)

    return wrapper


def require_superadmin(fn):
    @wraps(fn)
    @require_auth
    def wrapper(*args, **kwargs):
        if request.user["role"] != "superadmin":
            return jsonify({"error": "Solo superadmin"}), 403
        return fn(*args, **kwargs)

    return wrapper
