CREATE TABLE IF NOT EXISTS users (
    id               INTEGER PRIMARY KEY,
    first_name       TEXT,
    username         TEXT,
    default_currency TEXT    DEFAULT 'EUR',
    created_at       TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS categories (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL UNIQUE,
    icon       TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS store_mappings (
    pattern     TEXT    NOT NULL UNIQUE,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    source      TEXT    DEFAULT 'manual',
    created_at  TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS expenses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    amount      REAL    NOT NULL,
    currency    TEXT    NOT NULL DEFAULT 'EUR',
    description TEXT    NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    store       TEXT,
    created_at  TEXT    DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_expenses_user_date ON expenses(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_expenses_category  ON expenses(category_id);
CREATE INDEX IF NOT EXISTS idx_store_mappings_pattern ON store_mappings(pattern);
