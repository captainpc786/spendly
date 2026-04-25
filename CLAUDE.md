# Spendly — Expense Tracker

A Flask-based personal expense tracking web application built as a multi-step student project.

## Project Overview

- **App name:** Spendly
- **Tagline:** "Track every rupee. Own your finances."
- **Currency:** Indian Rupees (₹)
- **Tech stack:** Python 3 · Flask 3 · SQLite · Jinja2 · Vanilla CSS
- **Entry point:** `app.py` — runs on `http://localhost:5001`

---

## Project Structure

```
expense-tracker/
├── app.py                  # Flask application & all route definitions
├── requirements.txt        # Python dependencies
├── CLAUDE.md               # This file
├── database/
│   ├── __init__.py
│   └── db.py               # DB helpers: get_db(), init_db(), seed_db()
├── templates/
│   ├── base.html           # Shared layout: navbar, footer, font/CSS links
│   ├── landing.html        # Marketing/home page (extends base.html)
│   ├── login.html          # Sign-in form (extends base.html)
│   ├── register.html       # Sign-up form (extends base.html)
│   ├── terms.html          # Terms and Conditions (extends base.html)
│   └── privacy.html        # Privacy Policy (extends base.html)
├── static/
│   ├── css/
│   │   ├── style.css       # Global design system (variables, components)
│   │   └── landing.css     # Landing page-specific styles
│   └── js/
│       └── main.js         # Shared JavaScript
└── venv/                   # Python virtual environment
```

---

## Running the App

```powershell
# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Run the development server
python app.py
# → http://localhost:5001
```

---

## Design System

### Typography
| Role    | Font              | Fallback         |
|---------|-------------------|------------------|
| Display | DM Serif Display  | Georgia, serif   |
| Body    | DM Sans           | system-ui, sans  |

### Color Tokens (CSS custom properties in `style.css`)
| Token              | Value     | Usage                        |
|--------------------|-----------|------------------------------|
| `--ink`            | `#0f0f0f` | Primary text / buttons       |
| `--ink-soft`       | `#2d2d2d` | Secondary text               |
| `--ink-muted`      | `#6b6b6b` | Muted text, placeholders     |
| `--paper`          | `#f7f6f3` | Page background              |
| `--paper-warm`     | `#f0ede6` | Alternate section background |
| `--paper-card`     | `#ffffff` | Card / form backgrounds      |
| `--accent`         | `#1a472a` | Primary accent (forest green)|
| `--accent-light`   | `#e8f0eb` | Accent tints / badges        |
| `--accent-2`       | `#c17f24` | Secondary accent (amber)     |
| `--danger`         | `#c0392b` | Error states                 |
| `--border`         | `#e4e1da` | Standard border              |

### Border Radius
- `--radius-sm: 6px` — buttons, inputs
- `--radius-md: 12px` — cards, auth forms
- `--radius-lg: 20px` — hero mock widget

### Layout
- `--max-width: 1200px` — content max-width
- `--auth-width: 440px` — auth form max-width

### Reusable CSS Classes
- `.btn-primary` — dark filled button (hover → accent green)
- `.btn-ghost` — bordered ghost button
- `.btn-submit` — full-width form submit
- `.form-group`, `.form-input` — form field structure
- `.auth-section`, `.auth-card` — auth page layout
- `.feature-card` — feature grid card
- `.mock-card` — hero dashboard widget

---

## Database

**Engine:** SQLite (via Python `sqlite3` standard library)  
**Module:** `database/db.py`

### Required functions (to be implemented by students)
```python
get_db()   # Returns sqlite3 connection with row_factory=Row and PRAGMA foreign_keys=ON
init_db()  # Creates all tables with CREATE TABLE IF NOT EXISTS
seed_db()  # Inserts sample rows for development/testing
```

### Expected schema (to be designed)
- `users` — id, username, email, password_hash, created_at
- `expenses` — id, user_id (FK), amount, category, description, date, created_at
- `categories` — id, name (Food, Travel, Bills, Shopping, etc.)

---

## Routes

| Method | Path                     | Status        | Notes                          |
|--------|--------------------------|---------------|--------------------------------|
| GET    | `/`                      | ✅ Live       | Landing page                   |
| GET    | `/register`              | ✅ Live       | Registration form              |
| GET    | `/login`                 | ✅ Live       | Login form                     |
| GET    | `/terms`                 | ✅ Live       | Terms & Conditions             |
| GET    | `/privacy`               | ✅ Live       | Privacy Policy                 |
| GET    | `/logout`                | ⬜ Stub       | Step 3 — session clear         |
| GET    | `/profile`               | ⬜ Stub       | Step 4 — user dashboard        |
| GET    | `/expenses/add`          | ⬜ Stub       | Step 7 — add expense form      |
| GET    | `/expenses/<id>/edit`    | ⬜ Stub       | Step 8 — edit expense form     |
| GET    | `/expenses/<id>/delete`  | ⬜ Stub       | Step 9 — delete expense        |

---

## Dependencies

```
flask==3.1.3
werkzeug==3.1.6
pytest==8.3.5
pytest-flask==1.3.0
```

Install with:
```powershell
pip install -r requirements.txt
```

---

## Implementation Steps (Student Roadmap)

1. **Database Setup** — implement `get_db()`, `init_db()`, `seed_db()` in `database/db.py`
2. **User Registration** — `POST /register` with hashed passwords via `werkzeug.security`
3. **User Login / Logout** — `POST /login`, session management, `GET /logout`
4. **Profile / Dashboard** — `GET /profile` showing expense summary for logged-in user
5. **Expense List** — display all expenses for the current user
6. **Expense Filtering** — filter by category, date range
7. **Add Expense** — `GET/POST /expenses/add` form
8. **Edit Expense** — `GET/POST /expenses/<id>/edit` form
9. **Delete Expense** — `GET /expenses/<id>/delete` with confirmation

---

## Coding Conventions

- **Templates** always extend `base.html` via `{% extends "base.html" %}`
- **CSS** uses CSS custom properties (no Tailwind, no Bootstrap)
- **No JavaScript frameworks** — plain vanilla JS in `static/js/main.js`
- **Passwords** must be hashed with `werkzeug.security.generate_password_hash`
- **Database access** always uses `get_db()` from `database/db.py`
- Routes requiring login should redirect to `/login` if session is missing
- All forms use `POST` method with CSRF awareness (no library required for this project)
- Keep comments in the existing `# Students will implement...` format for stub functions
