from flask import Flask, render_template
from database.db import init_db

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"

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


@app.route("/login")
def login():
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
    return "Logout — coming in Step 3"


@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
