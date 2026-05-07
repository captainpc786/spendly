# Spec: Backend Routes for Profile Page

## Overview
This step expands the profile/dashboard page into a fully interactive expense management
hub. The `/profile` route already renders a monthly summary; this spec adds the four remaining
expense-management routes — **List**, **Add**, **Edit**, and **Delete** — that are currently
returning stub strings in `app.py`.

After this step a logged-in user can:
1. View all their expenses in a paginated/sorted list on the profile page.
2. Add a new expense via a form.
3. Edit an existing expense.
4. Delete an expense with a single click (no separate confirmation page).

All four routes are **logged-in only**: any unauthenticated request redirects to `/login`.

---

## Depends on
- Step 01 — Database Setup (`users`, `expenses`, `categories` tables must exist)
- Step 02 — User Registration (a seeded user must exist for manual testing)
- Step 03 — Login and Logout (`session["user_id"]` must be set by the login flow)
- Step 04 — Profile Page (`GET /profile` renders `profile.html`; `get_user_by_id` and
  `get_expense_summary` helpers already exist in `database/db.py`)

---

## Routes

| Method | Path                        | Access        | Notes                              |
|--------|-----------------------------|---------------|------------------------------------|
| GET    | `/profile`                  | Logged-in     | Already live; extended with expense list |
| GET    | `/expenses/add`             | Logged-in     | Render the add-expense form        |
| POST   | `/expenses/add`             | Logged-in     | Validate & insert; redirect to `/profile` |
| GET    | `/expenses/<int:id>/edit`   | Logged-in     | Render form pre-filled with expense data |
| POST   | `/expenses/<int:id>/edit`   | Logged-in     | Validate & update; redirect to `/profile` |
| GET    | `/expenses/<int:id>/delete` | Logged-in     | Delete row; redirect to `/profile` |

---

## Database changes
No new tables or columns. Two new helper functions will be added to `database/db.py`:

### `get_all_expenses(user_id)` → `list[sqlite3.Row]`
Returns all expenses for the given user, most-recent first.

```sql
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
```

### `get_all_categories()` → `list[sqlite3.Row]`
Returns all rows from the `categories` table (used to populate `<select>` dropdowns).

```sql
SELECT id, name FROM categories ORDER BY name ASC
```

### `get_expense_by_id(expense_id, user_id)` → `sqlite3.Row | None`
Returns a single expense row **only if it belongs to the requesting user**
(prevents IDOR — Insecure Direct Object Reference).

```sql
SELECT e.id, e.amount, e.category_id, e.description, e.date
FROM expenses e
WHERE e.id = ? AND e.user_id = ?
```

### `add_expense(user_id, amount, category_id, description, date)` → `None`
Inserts one expense row.

```sql
INSERT INTO expenses (user_id, amount, category_id, description, date)
VALUES (?, ?, ?, ?, ?)
```

### `update_expense(expense_id, user_id, amount, category_id, description, date)` → `None`
Updates a single expense, scoped to the owning user.

```sql
UPDATE expenses
SET amount = ?, category_id = ?, description = ?, date = ?
WHERE id = ? AND user_id = ?
```

### `delete_expense(expense_id, user_id)` → `None`
Deletes a single expense, scoped to the owning user.

```sql
DELETE FROM expenses WHERE id = ? AND user_id = ?
```

---

## Templates

### Modify: `templates/profile.html`
Add an **expense list section** below the existing summary cards:
- Table columns: Date | Category | Description | Amount | Actions (Edit / Delete)
- Each row's Edit button links to `url_for("edit_expense", id=expense.id)`
- Each row's Delete link is a small `<form method="POST">` posting to
  `url_for("delete_expense", id=expense.id)` (GET-based delete is unsafe; see Rules)
- An empty-state message is shown when `expenses` is an empty list
- The existing "Add Expense" button remains prominent at the top of the section

### Create: `templates/expenses/add.html`
Form fields:
- `amount` — number input, step=`0.01`, min=`0.01`, required
- `category_id` — `<select>` populated from `categories`; first option is blank placeholder
- `description` — text input, maxlength=`255`, optional
- `date` — date input, required, defaults to today (`value="{{ today }}"`)
- Submit button: "Add Expense" (`.btn-submit`)
- Cancel link back to `/profile`

### Create: `templates/expenses/edit.html`
Identical structure to `add.html` but:
- All fields pre-filled from the existing expense row
- Submit button text: "Save Changes"
- Page title and heading reflect "Edit Expense"

---

## Files to change
- `app.py` — convert the three stub routes into real GET+POST handlers; pass `expenses`
  and `categories` into `profile()` render call
- `database/db.py` — add the six helper functions listed above

## Files to create
- `templates/expenses/add.html` — add-expense form (extends `base.html`)
- `templates/expenses/edit.html` — edit-expense form (extends `base.html`)
- `static/css/expenses.css` — expense list table + form styles

---

## New dependencies
None. All required libraries are already installed.

---

## Rules for implementation

### Security
- All routes must check `session.get("user_id")` first; redirect to `url_for("login")` if absent
- `get_expense_by_id` **must** filter by both `id` AND `user_id` — never fetch by `id` alone
- Delete and update helpers must also scope queries to `user_id`
- Delete must be triggered by `POST`, not `GET` — use a small `<form method="POST">` in the
  template; a `GET /expenses/<id>/delete` stub is only acceptable as a temporary redirect
- No f-strings in SQL — parameterised queries only

### Validation (server-side, in the route)
- `amount`: must be convertible to `float` and `> 0`; show flash error and re-render form on failure
- `date`: must be a non-empty string matching `YYYY-MM-DD`; validate with `datetime.strptime`
- `category_id`: optional — convert to `int` if provided, else pass `None`
- `description`: optional — strip whitespace, store `None` if empty

### Flash messages
| Event | Category | Message |
|-------|----------|---------|
| Expense added | `success` | `"Expense added."` |
| Expense updated | `success` | `"Expense updated."` |
| Expense deleted | `success` | `"Expense deleted."` |
| Expense not found / wrong owner | `error` | `"Expense not found."` |
| Invalid amount | `error` | `"Amount must be a positive number."` |
| Invalid date | `error` | `"Please enter a valid date (YYYY-MM-DD)."` |

### CSS
- Use CSS variables only — never hardcode hex values
- Table uses `--border` for borders, `--paper-card` for background
- Amount column right-aligned and formatted as `₹X,XXX.XX`
- Action buttons use `.btn-ghost` (small variant); Delete styled with `--danger`
- Expense form uses existing `.auth-card`, `.form-group`, `.form-input` classes

### Template
- All templates extend `base.html` via `{% extends "base.html" %}`
- Use `url_for()` for every internal link — never hardcode paths
- Date default in add form: pass `today = datetime.date.today().isoformat()` from the route
- Currency formatting: use a Jinja2 custom filter `format_inr` registered in `app.py`

---

## Definition of done
- [ ] `GET /profile` shows the full expense list below the summary cards (most-recent first)
- [ ] `GET /profile` with no expenses shows the empty-state message in the list section
- [ ] `GET /expenses/add` renders the form without errors when logged in
- [ ] `GET /expenses/add` without a session redirects to `/login` with a flash message
- [ ] `POST /expenses/add` with valid data inserts a row and redirects to `/profile` with a success flash
- [ ] `POST /expenses/add` with a non-numeric amount re-renders the form with an error flash
- [ ] `POST /expenses/add` with a missing date re-renders the form with an error flash
- [ ] `GET /expenses/<id>/edit` renders the form pre-filled with the correct expense data
- [ ] `GET /expenses/<id>/edit` with a foreign `id` (not owned by session user) redirects to `/profile` with an error flash
- [ ] `POST /expenses/<id>/edit` with valid data updates the row and redirects to `/profile` with a success flash
- [ ] `POST /expenses/<id>/delete` deletes the correct row and redirects to `/profile` with a success flash
- [ ] `POST /expenses/<id>/delete` with a foreign `id` does nothing and redirects to `/profile` with an error flash
- [ ] All SQL queries use parameterised form — no f-strings or string concatenation
- [ ] All styles use CSS variables — no hardcoded colours
- [ ] Amount is displayed as `₹X,XXX.XX` everywhere (list, summary cards)
