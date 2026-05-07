import os
import sqlite3

# Path to the SQLite database file (project root)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'spendly.db')


def get_db():
    """Return a sqlite3 connection with row_factory=Row and foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_user_by_email(email):
    """Return the user row matching email (case-insensitive), or None."""
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.strip().lower(),)
        ).fetchone()
    finally:
        conn.close()


def get_user_by_id(user_id):
    """Return the user row matching the given primary key, or None."""
    conn = get_db()
    try:
        return conn.execute(
            "SELECT id, username, email, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()


def get_expense_summary(user_id):
    """
    Return all-time spending totals for a user.

    Returns a dict with keys:
      - total_amount  : float  (0.0 when no expenses exist)
      - expense_count : int    (0 when no expenses exist)
      - categories    : list of sqlite3.Row  (category_name, category_total)
    """
    conn = get_db()
    try:
        totals = conn.execute(
            """
            SELECT
                COALESCE(SUM(amount), 0) AS total_amount,
                COUNT(*)                 AS expense_count
            FROM expenses
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

        categories = conn.execute(
            """
            SELECT
                COALESCE(c.name, 'Uncategorised') AS category_name,
                SUM(e.amount)                      AS category_total
            FROM expenses e
            LEFT JOIN categories c ON c.id = e.category_id
            WHERE e.user_id = ?
            GROUP BY COALESCE(c.name, 'Uncategorised')
            ORDER BY category_total DESC
            """,
            (user_id,),
        ).fetchall()

        return {
            "total_amount":  totals["total_amount"],
            "expense_count": totals["expense_count"],
            "categories":    categories,
        }
    finally:
        conn.close()


def get_all_expenses(user_id):
    """Return all expenses for the given user, most-recent first."""
    conn = get_db()
    try:
        return conn.execute(
            """
            SELECT
                e.id,
                e.amount,
                e.description,
                e.date,
                COALESCE(c.name, 'Uncategorised') AS category_name
            FROM expenses e
            LEFT JOIN categories c ON c.id = e.category_id
            WHERE e.user_id = ?
            ORDER BY e.date DESC, e.created_at DESC
            """,
            (user_id,),
        ).fetchall()
    finally:
        conn.close()


def get_all_categories():
    """Return all category rows ordered by name."""
    conn = get_db()
    try:
        return conn.execute(
            "SELECT id, name FROM categories ORDER BY name ASC"
        ).fetchall()
    finally:
        conn.close()


def get_expense_by_id(expense_id, user_id):
    """Return a single expense row only if it belongs to user_id (IDOR-safe), or None."""
    conn = get_db()
    try:
        return conn.execute(
            """
            SELECT e.id, e.amount, e.category_id, e.description, e.date
            FROM expenses e
            WHERE e.id = ? AND e.user_id = ?
            """,
            (expense_id, user_id),
        ).fetchone()
    finally:
        conn.close()


def add_expense(user_id, amount, category_id, description, date):
    """Insert one expense row for the given user."""
    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO expenses (user_id, amount, category_id, description, date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, amount, category_id, description, date),
        )
        conn.commit()
    finally:
        conn.close()


def update_expense(expense_id, user_id, amount, category_id, description, date):
    """Update an expense row, scoped to the owning user."""
    conn = get_db()
    try:
        conn.execute(
            """
            UPDATE expenses
            SET amount = ?, category_id = ?, description = ?, date = ?
            WHERE id = ? AND user_id = ?
            """,
            (amount, category_id, description, date, expense_id, user_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_expense(expense_id, user_id):
    """Delete an expense row, scoped to the owning user."""
    conn = get_db()
    try:
        conn.execute(
            "DELETE FROM expenses WHERE id = ? AND user_id = ?",
            (expense_id, user_id),
        )
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create all tables using CREATE TABLE IF NOT EXISTS."""
    conn = get_db()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT    NOT NULL UNIQUE,
                email         TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS categories (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT    NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                amount      REAL    NOT NULL CHECK (amount > 0),
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                description TEXT,
                date        TEXT    NOT NULL,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );
        """)
        conn.commit()
    finally:
        conn.close()


def seed_db():
    """Insert sample data for development. Safe to run multiple times (INSERT OR IGNORE)."""
    from werkzeug.security import generate_password_hash

    conn = get_db()
    try:
        # ── Default categories ──────────────────────────────────────────
        categories = [
            'Food', 'Travel', 'Bills', 'Shopping',
            'Health', 'Entertainment', 'Other',
        ]
        conn.executemany(
            "INSERT OR IGNORE INTO categories (name) VALUES (?)",
            [(c,) for c in categories],
        )

        # ── Sample user (password: password123) ─────────────────────────
        conn.execute(
            "INSERT OR IGNORE INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            ('demo', 'demo@spendly.app', generate_password_hash('password123')),
        )

        # ── Sample expenses for the demo user ───────────────────────────
        conn.executemany(
            """INSERT OR IGNORE INTO expenses
               (id, user_id, amount, category_id, description, date)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [
                (1, 1, 450.00,  1, 'Lunch at Subway',       '2026-04-20'),
                (2, 1, 1200.00, 2, 'Ola ride to airport',   '2026-04-21'),
                (3, 1, 3400.00, 3, 'Electricity bill',      '2026-04-22'),
                (4, 1, 899.00,  4, 'New headphones',        '2026-04-23'),
                (5, 1, 250.00,  5, 'Pharmacy',              '2026-04-24'),
            ],
        )

        conn.commit()
        print("✅ Database seeded successfully.")
    finally:
        conn.close()
