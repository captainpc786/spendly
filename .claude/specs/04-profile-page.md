# Spec: Profile Page

## Overview
This feature converts the `/profile` stub into a fully functional user dashboard for Spendly.
After login, users will land on their personal profile page, which greets them by name and shows
a high-level summary of their spending: total spent this month, number of expenses, and a
breakdown by category. This is the first logged-in-only route in the app and establishes the
access-control pattern (redirect to `/login` if no session) that all subsequent expense routes
will reuse.

## Depends on
- Step 01 — Database Setup (`users`, `expenses`, and `categories` tables must exist)
- Step 02 — User Registration (a user account must exist to view the profile)
- Step 03 — Login and Logout (`session["user_id"]` must be set by the login flow)

## Routes
- `GET /profile` — render the profile/dashboard page — **logged-in only** (redirect to `/login` if
  `session["user_id"]` is absent)

## Database changes
No new tables or columns required. All data is already present in:
- `users` — `id`, `username`, `email`, `created_at`
- `expenses` — `id`, `user_id`, `amount`, `category_id`, `description`, `date`
- `categories` — `id`, `name`

Two new helper queries will be added to `database/db.py`:
1. `get_user_by_id(user_id)` — fetch a single user row by primary key
2. `get_expense_summary(user_id)` — return total spend and per-category totals for the current
   calendar month (aggregated via SQL `GROUP BY`)

## Templates
- **Create:** `templates/profile.html` — extends `base.html`; displays:
  - Greeting header: "Hello, {username}!"
  - Summary card: total spent this month (formatted as ₹X,XXX.XX)
  - Summary card: number of expenses this month
  - Category breakdown table or card grid (category name → total amount)
  - Empty state message when the user has no expenses yet
  - A prominent "Add Expense" button linking to `/expenses/add`

## Files to change
- `app.py` — implement `profile()` route: guard with session check, fetch user + summary from DB,
  pass data to template
- `database/db.py` — add `get_user_by_id(user_id)` and `get_expense_summary(user_id)` helpers

## Files to create
- `templates/profile.html` — the profile/dashboard template (extends `base.html`)
- `static/css/profile.css` — profile page-specific styles (imported via `base.html` block or
  inline `<link>` in `profile.html`)

## New dependencies
No new dependencies. All required libraries (`flask`, `sqlite3`, `werkzeug`) are already installed.

## Rules for implementation
- No SQLAlchemy or ORMs — use raw `sqlite3` via `get_db()`
- Parameterised queries only — never use f-strings or string concatenation in SQL
- Passwords are never read or displayed on this page
- Use CSS variables — never hardcode hex values (use `--accent`, `--paper-card`, etc.)
- All templates extend `base.html` via `{% extends "base.html" %}`
- Use `url_for()` for every internal link — never hardcode paths
- The route must redirect to `url_for("login")` with a flash "Please log in to view your profile."
  if `session["user_id"]` is not set
- `get_user_by_id` and `get_expense_summary` belong in `database/db.py`, not inline in the route
- Currency must display in Indian Rupees (₹) formatted to 2 decimal places
- Month filter in `get_expense_summary` must use SQL `strftime('%Y-%m', date)` against the
  current month — do not filter in Python
- The "Add Expense" link must be visible even when there are no expenses (empty state)

## Definition of done
- [ ] Visiting `GET /profile` without being logged in redirects to `/login` with a flash message
- [ ] Visiting `GET /profile` while logged in renders `profile.html` without errors
- [ ] The page greets the user by their `username` (e.g. "Hello, demo!")
- [ ] The total amount spent this month is displayed and formatted as ₹X,XXX.XX
- [ ] The number of expenses this month is displayed correctly
- [ ] Each category with at least one expense this month appears in the breakdown
- [ ] When the user has no expenses, an empty-state message is shown instead of the table
- [ ] The "Add Expense" button is present and links to `/expenses/add`
- [ ] The `/profile` route no longer returns the raw stub string "Profile page — coming in Step 4"
- [ ] All styles use CSS variables from `style.css` — no hardcoded colours
