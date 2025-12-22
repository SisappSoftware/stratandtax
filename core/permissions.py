from functools import wraps
from flask import request, jsonify
from core.auth import decode_token, get_user_by_id


def require_auth(fn):
    """
    Middleware para proteger endpoints con JWT
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")

        if not auth.startswith("Bearer "):
            return jsonify({"error": "No autorizado"}), 401

        token = auth.split(" ", 1)[1]

        try:
            claims = decode_token(token)
            user = get_user_by_id(int(claims["sub"]))

            if not user or not user.get("active"):
                return jsonify({"error": "No autorizado"}), 401

            # Inyectamos el usuario en la request
            request.user = user

            return fn(*args, **kwargs)

        except Exception:
            return jsonify({"error": "Token inválido"}), 401

    return wrapper

def require_superadmin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "No autorizado"}), 401

        token = auth.split(" ", 1)[1]

        try:
            claims = decode_token(token)
            user = get_user_by_id(int(claims["sub"]))

            if not user or user["role"] != "superadmin":
                return jsonify({"error": "Permisos insuficientes"}), 403

            request.user = user
            return fn(*args, **kwargs)
        except Exception:
            return jsonify({"error": "Token inválido"}), 401

    return wrapper