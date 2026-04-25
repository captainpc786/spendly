# Step 1 — Database Setup

## Checklist

### `database/db.py`
- [x] Import `sqlite3` and `os`
- [x] Define `DB_PATH` constant pointing to `spendly.db` in the project root
- [x] Implement `get_db()` — returns `sqlite3.Connection` with `row_factory=sqlite3.Row` and `PRAGMA foreign_keys = ON`
- [x] Implement `init_db()` — creates `users`, `categories`, `expenses` tables with `CREATE TABLE IF NOT EXISTS`
- [x] Implement `seed_db()` — inserts default categories, a demo user, and sample expenses using `INSERT OR IGNORE`

### Schema
- [x] `users` table — `id`, `username`, `email`, `password_hash`, `created_at`
- [x] `categories` table — `id`, `name` (seeded: Food, Travel, Bills, Shopping, Health, Entertainment, Other)
- [x] `expenses` table — `id`, `user_id` (FK → users), `amount`, `category_id` (FK → categories), `description`, `date`, `created_at`
- [x] Foreign key: `expenses.user_id` → `users.id` ON DELETE CASCADE
- [x] Foreign key: `expenses.category_id` → `categories.id` ON DELETE SET NULL
- [x] Check constraint: `expenses.amount > 0`

### `app.py`
- [x] Import `init_db` from `database.db`
- [x] Set `app.secret_key` (required for session management in Step 3)
- [x] Call `init_db()` inside `with app.app_context()` at startup

### Project hygiene
- [x] `spendly.db` added to `.gitignore`
- [x] `database/__init__.py` exists (empty, marks package)

## Notes

- Demo credentials: **username:** `demo` · **password:** `password123`
- `seed_db()` uses `INSERT OR IGNORE` — safe to run multiple times
- `seed_db()` is intentionally **not** called at startup; run it manually during development:
  ```powershell
  python -c "from database.db import seed_db; seed_db()"
  ```
- `spendly.db` is auto-created in the project root the first time `python app.py` is run
