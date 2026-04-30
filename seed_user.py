import sys
import os
import random
from datetime import datetime

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(__file__))

from database.db import get_db
from werkzeug.security import generate_password_hash

# ── Indian name pool ─────────────────────────────────────────────────────────
first_names = [
    'Rahul', 'Priya', 'Arjun', 'Sneha', 'Vikram',
    'Ananya', 'Rohan', 'Meera', 'Karan', 'Divya',
    'Aditya', 'Pooja', 'Nikhil', 'Shreya', 'Ravi',
    'Kavya', 'Siddharth', 'Neha', 'Manish', 'Swati',
]
last_names = [
    'Sharma', 'Patel', 'Singh', 'Verma', 'Nair',
    'Iyer', 'Reddy', 'Gupta', 'Joshi', 'Mehta',
    'Rao', 'Pillai', 'Chopra', 'Bose', 'Kumar',
    'Das', 'Shah', 'Malhotra', 'Kapoor', 'Mishra',
]


def make_user():
    first    = random.choice(first_names)
    last     = random.choice(last_names)
    num      = random.randint(10, 999)
    email    = f"{first.lower()}.{last.lower()}{num}@gmail.com"
    username = f"{first.lower()}{last.lower()}{num}"
    name     = f"{first} {last}"
    return name, username, email


conn = get_db()
try:
    # Keep regenerating until we find a unique email + username combo
    while True:
        name, username, email = make_user()
        row = conn.execute(
            "SELECT id FROM users WHERE email = ? OR username = ?",
            (email, username),
        ).fetchone()
        if row is None:
            break

    pw_hash = generate_password_hash("password123")
    now     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur = conn.execute(
        "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (username, email, pw_hash, now),
    )
    conn.commit()
    user_id = cur.lastrowid

    print("✅ Seed user created!")
    print(f"   id       : {user_id}")
    print(f"   name     : {name}")
    print(f"   username : {username}")
    print(f"   email    : {email}")
    print(f"   password : password123  (stored hashed)")
    print(f"   created  : {now}")

finally:
    conn.close()
