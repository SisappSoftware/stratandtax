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

CREATE TABLE IF NOT EXISTS generated_packs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  pack_id TEXT NOT NULL,
  zip_filename TEXT NOT NULL,
  created_at TEXT NOT NULL,
  email_to TEXT,
  email_sent INTEGER NOT NULL DEFAULT 0,
  email_error TEXT,
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS site_content (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS generated_packs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    pack_id TEXT NOT NULL,
    zip_name TEXT NOT NULL,
    zip_path TEXT NOT NULL,
    email_sent INTEGER NOT NULL DEFAULT 0,
    email_error TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
