-- ===============================
-- TABLA DE USUARIOS
-- ===============================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'admin', 'superadmin')),
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

-- ===============================
-- TABLA DE DOCUMENTOS
-- ===============================
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    template_type TEXT NOT NULL,
    filename TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
