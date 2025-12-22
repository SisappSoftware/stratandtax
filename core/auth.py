import os
import time
import sqlite3
import bcrypt
import jwt
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", "db/app.db")
JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_TTL_SECONDS = int(os.getenv("JWT_TTL_SECONDS", "86400"))  # 24h


def db() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema() -> None:
    schema_path = os.getenv("DB_SCHEMA_PATH", "db/schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = f.read()
    with db() as conn:
        conn.executescript(schema)


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


def create_user(email: str, password: str, role: str = "user", active: int = 1) -> int:
    email = (email or "").strip().lower()
    if not email or "@" not in email:
        raise ValueError("Email inválido")
    if role not in ("user", "admin", "superadmin"):
        raise ValueError("Role inválido")
    if not password or len(password) < 6:
        raise ValueError("Password muy corta (min 6)")

    pw_hash = hash_password(password)
    with db() as conn:
        cur = conn.execute(
            """
            INSERT INTO users (email, password_hash, role, active, created_at)
            VALUES (?, ?, ?, 1, ?)
            """,
            (
                email,
                pw_hash,
                role,
                datetime.utcnow().isoformat()
            )
        )
        return int(cur.lastrowid)


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    email = (email or "").strip().lower()
    with db() as conn:
        row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    with db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    return dict(row) if row else None


def issue_token(user: Dict[str, Any]) -> str:
    now = int(time.time())
    payload = {
        "sub": str(user["id"]),
        "email": user["email"],
        "role": user["role"],
        "iat": now,
        "exp": now + JWT_TTL_SECONDS,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])


def bootstrap_admin_if_needed() -> None:
    """
    Crea un admin inicial si no existe, usando env vars.
    """
    email = os.getenv("ADMIN_BOOTSTRAP_EMAIL", "").strip().lower()
    password = os.getenv("ADMIN_BOOTSTRAP_PASS", "").strip()
    if not email or not password:
        return

    existing = get_user_by_email(email)
    if existing:
        return

    create_user(email=email, password=password, role="admin", active=1)
