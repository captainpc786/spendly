from flask import Flask, render_template, request, flash, redirect, url_for, session
from database.db import (
    init_db, get_db, get_user_by_email, get_user_by_id, get_expense_summary,
    get_all_expenses, get_all_categories, get_expense_by_id,
    add_expense as db_add_expense,
    update_expense,
    delete_expense as db_delete_expense,
)
import re
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"


@app.template_filter("format_inr")
def format_inr(value):
    """Format a number as Indian Rupees: ₹1,234.56"""
    return "₹{:,.2f}".format(float(value or 0))

# Create tables on first run
with app.app_context():
    init_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("register.html")

    # ── Read form fields ────────────────────────────────────────────
    username         = request.form.get("username", "").strip()
    email            = request.form.get("email", "").strip().lower()
    password         = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    # ── Helper: re-render form preserving safe fields ───────────────
    def fail(message):
        flash(message, "error")
        return render_template("register.html", username=username, email=email)

    # ── Format validation ───────────────────────────────────────────
    if not (3 <= len(username) <= 30):
        return fail("Username must be 3–30 characters.")

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return fail("Username may only contain letters, numbers, and underscores.")

    if "@" not in email or "." not in email:
        return fail("Please enter a valid email address.")

    if len(password) < 8:
        return fail("Password must be at least 8 characters.")

    if password != confirm_password:
        return fail("Passwords do not match.")

    # ── Uniqueness checks ───────────────────────────────────────────
    conn = get_db()
    try:
        if conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone():
            return fail("Username already taken.")

        if conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone():
            return fail("Email already registered.")

        # ── Insert new user ─────────────────────────────────────────
        pw_hash = generate_password_hash(password)
        conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, pw_hash),
        )
        conn.commit()
    finally:
        conn.close()

    flash("Account created! Please log in.", "success")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("login.html")

    email    = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = get_user_by_email(email)
    if user and check_password_hash(user["password_hash"], password):
        session.clear()
        session["user_id"] = user["id"]
        return redirect(url_for("profile"))

    flash("Invalid email or password.", "error")
    return render_template("login.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to view your profile.", "error")
        return redirect(url_for("login"))

    user       = get_user_by_id(user_id)
    summary    = get_expense_summary(user_id)
    expenses   = get_all_expenses(user_id)
    categories = get_all_categories()
    return render_template(
        "profile.html",
        user=user,
        summary=summary,
        expenses=expenses,
        categories=categories,
    )


@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to add an expense.", "error")
        return redirect(url_for("login"))

    categories = get_all_categories()
    today      = datetime.date.today().isoformat()

    if request.method == "GET":
        return render_template("expenses/add.html", categories=categories, today=today)

    # ── Parse form ────────────────────────────────────────────────
    raw_amount  = request.form.get("amount", "").strip()
    raw_date    = request.form.get("date", "").strip()
    cat_raw     = request.form.get("category_id", "").strip()
    description = request.form.get("description", "").strip() or None

    def fail(msg):
        flash(msg, "error")
        return render_template(
            "expenses/add.html",
            categories=categories,
            today=today,
            amount=raw_amount,
            date=raw_date,
            category_id=cat_raw,
            description=description,
        )

    # ── Validate amount ───────────────────────────────────────────────
    try:
        amount = float(raw_amount)
        if amount <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return fail("Amount must be a positive number.")

    # ── Validate date ────────────────────────────────────────────────
    try:
        datetime.datetime.strptime(raw_date, "%Y-%m-%d")
    except ValueError:
        return fail("Please enter a valid date (YYYY-MM-DD).")

    category_id = int(cat_raw) if cat_raw else None

    db_add_expense(user_id, amount, category_id, description, raw_date)
    flash("Expense added.", "success")
    return redirect(url_for("profile"))


@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
def edit_expense(id):
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to edit an expense.", "error")
        return redirect(url_for("login"))

    expense = get_expense_by_id(id, user_id)
    if not expense:
        flash("Expense not found.", "error")
        return redirect(url_for("profile"))

    categories = get_all_categories()

    if request.method == "GET":
        return render_template("expenses/edit.html", expense=expense, categories=categories)

    # ── Parse form ────────────────────────────────────────────────
    raw_amount  = request.form.get("amount", "").strip()
    raw_date    = request.form.get("date", "").strip()
    cat_raw     = request.form.get("category_id", "").strip()
    description = request.form.get("description", "").strip() or None

    def fail(msg):
        flash(msg, "error")
        return render_template(
            "expenses/edit.html",
            expense=expense,
            categories=categories,
        )

    # ── Validate amount ───────────────────────────────────────────────
    try:
        amount = float(raw_amount)
        if amount <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return fail("Amount must be a positive number.")

    # ── Validate date ────────────────────────────────────────────────
    try:
        datetime.datetime.strptime(raw_date, "%Y-%m-%d")
    except ValueError:
        return fail("Please enter a valid date (YYYY-MM-DD).")

    category_id = int(cat_raw) if cat_raw else None

    update_expense(id, user_id, amount, category_id, description, raw_date)
    flash("Expense updated.", "success")
    return redirect(url_for("profile"))


@app.route("/expenses/<int:id>/delete", methods=["POST"])
def delete_expense(id):
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in.", "error")
        return redirect(url_for("login"))

    expense = get_expense_by_id(id, user_id)
    if not expense:
        flash("Expense not found.", "error")
    else:
        db_delete_expense(id, user_id)
        flash("Expense deleted.", "success")

    return redirect(url_for("profile"))


# ------------------------------------------------------------------ #
# DEV ONLY — remove after seeding                                     #
# ------------------------------------------------------------------ #

@app.route("/dev/seed-user4")
def dev_seed_user4():
    """Temporary route: inserts 3 sample expenses for user_id=4."""
    conn = get_db()
    try:
        user = conn.execute("SELECT id FROM users WHERE id = 4").fetchone()
        if not user:
            return "No user with id=4 found. Register first.", 404

        # Fetch category ids by name
        def cat_id(name):
            row = conn.execute(
                "SELECT id FROM categories WHERE name = ?", (name,)
            ).fetchone()
            return row["id"] if row else None

        expenses = [
            # (user_id, amount, category_id, description, date)
            (4, 1_250.00, cat_id("Food"),          "Swiggy order – Biryani",       "2026-04-10"),
            (4, 3_400.00, cat_id("Bills"),          "Electricity bill – April",     "2026-03-22"),
            (4,   799.00, cat_id("Entertainment"),  "Movie tickets – 2 seats",      "2026-02-14"),
            (4, 2_100.00, cat_id("Shopping"),       "Amazon – headphones",          "2026-01-30"),
            (4,   450.00, cat_id("Travel"),         "Ola cab to airport",           "2025-12-05"),
            (4,   320.00, cat_id("Health"),         "Pharmacy – medicines",         "2025-11-18"),
        ]

        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category_id, description, date)"
            " VALUES (?, ?, ?, ?, ?)",
            expenses,
        )
        conn.commit()

        lines = [f"{d} | ₹{a:,.2f} | {desc}" for _, a, _, desc, d in expenses]
        return (
            "<h2>✅ Seeded {} expenses for user 4 (Nithish_)</h2><pre>{}</pre>"
            '<p><a href="/profile">→ Go to profile</a></p>'
            '<p><strong>Delete the /dev/seed-user4 route from app.py when done.</strong></p>'
        ).format(len(expenses), "\n".join(lines))

    finally:
        conn.close()


if __name__ == "__main__":
    app.run(debug=True, port=5001)
