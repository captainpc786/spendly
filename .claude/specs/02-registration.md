# Spec: Registration

## Overview
This step implements the user registration flow for Spendly. A visitor fills in
a username, email address, and password on the `/register` page. The server
validates the input, checks for duplicate usernames and emails, hashes the
password with werkzeug, inserts the new row into the `users` table, and then
redirects the user to the login page with a success flash message. This is the
gateway feature that lets real users create their own accounts before Step 3
(Login / Logout) and Step 4 (Profile) can be built on top of it.

## Depends on
- **Step 01 — Database Setup**: the `users` table must exist (`init_db()` must
  have been run) and `get_db()` must be importable from `database.db`.

## Routes

| Method | Path | Description | Access |
|--------|------|-------------|--------|
| `GET` | `/register` | Render the blank registration form | Public |
| `POST` | `/register` | Validate input and create the user account | Public |

## Database changes
No new tables or columns required. The existing `users` table already has all
needed fields:

```
users (id, username, email, password_hash, created_at)
```

`created_at` defaults to `datetime('now')` so it does not need to be supplied
by the application layer.

## Templates

### Create
- `templates/register.html` — Registration form extending `base.html`.
  Contains fields for `username`, `email`, `password`, and `confirm_password`.
  Displays flashed error/success messages from the session.

### Modify
- `templates/base.html` — No structural changes needed; confirm that
  `get_flashed_messages` block is already present (or add it if missing).

## Files to change

| File | What changes |
|------|-------------|
| `app.py` | Convert the `register()` stub into a real `GET/POST` view that handles validation, hashing, DB insert, and redirect. Import `request`, `redirect`, `url_for`, `flash`, `session` from Flask, and `get_db` from `database.db`. |

## Files to create

| File | Purpose |
|------|---------|
| `templates/register.html` | Registration form page |

## New dependencies
No new dependencies. `werkzeug` (already installed via Flask) provides
`generate_password_hash`.

## Rules for implementation
- No SQLAlchemy or ORMs — use raw `sqlite3` via `get_db()` only.
- Parameterised queries only — never interpolate user input into SQL strings.
- Passwords hashed with `werkzeug.security.generate_password_hash` — never
  store plaintext.
- Use CSS variables — never hardcode hex colour values in templates or CSS.
- All templates must extend `base.html` using `{% extends "base.html" %}`.
- Use `app.secret_key` (set in `app.py`) so Flask sessions and flash messages
  work correctly.
- Validate server-side (do not rely solely on HTML5 `required` attributes):
  - `username`: 3–30 characters, alphanumeric + underscores only.
  - `email`: must contain `@` and `.` (basic check is fine).
  - `password`: minimum 8 characters.
  - `confirm_password`: must match `password`.
  - Both `username` and `email` must be unique; show a specific error if either
    is already taken.
- On any validation failure, re-render the form with the error flashed and the
  previously entered `username` and `email` pre-filled (never pre-fill the
  password fields).
- On success, redirect to `url_for('login')` with a success flash message.

## Definition of done
- [ ] `GET /register` renders the registration form without errors.
- [ ] Submitting the form with all valid, unique data creates a new row in the
      `users` table and redirects to `/login`.
- [ ] A success flash message ("Account created! Please log in.") is visible on
      the login page after a successful registration.
- [ ] Submitting with a `username` already in the database shows an error
      "Username already taken" and does not create a duplicate row.
- [ ] Submitting with an `email` already in the database shows an error
      "Email already registered" and does not create a duplicate row.
- [ ] Submitting with mismatched passwords shows "Passwords do not match".
- [ ] Submitting with a password shorter than 8 characters shows "Password must
      be at least 8 characters".
- [ ] The `password_hash` column in `spendly.db` never contains a plaintext
      password (verify with DB Browser or `sqlite3` CLI).
- [ ] The `confirm_password` value is never stored anywhere.
- [ ] All pages pass HTML validation (no unclosed tags, valid nesting).
