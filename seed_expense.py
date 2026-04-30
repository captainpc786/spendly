import sys
import os
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from database.db import get_db

# ── Arguments ────────────────────────────────────────────────────────────────
user_id = 2
count   = 5
months  = 3

# ── Category data (name -> (min_amount, max_amount, weight, descriptions)) ──
CATEGORIES = {
    "Food":          (50,   800,  30, [
        "Lunch at Haldiram's", "Swiggy order", "Zomato dinner",
        "Chai and snacks", "Grocery from DMart", "Breakfast at Udupi",
        "Biryani takeaway", "Street food", "Office canteen lunch",
    ]),
    "Travel":        (20,   500,  20, [
        "Ola ride to office", "Metro recharge", "Rapido bike ride",
        "Auto to market", "Uber airport drop", "Bus pass recharge",
        "Petrol top-up",
    ]),
    "Bills":         (200, 3000, 15, [
        "Electricity bill", "Internet recharge - Jio", "Mobile postpaid bill",
        "Water bill", "Gas cylinder booking", "DTH recharge",
    ]),
    "Shopping":      (200, 5000, 15, [
        "Amazon order", "Flipkart sale purchase", "Myntra kurti",
        "New earphones", "Stationery", "Footwear from Bata",
        "Kitchen utensils",
    ]),
    "Health":        (100, 2000,  8, [
        "Pharmacy - antibiotics", "Doctor consultation",
        "Blood test at lab", "Gym monthly fee", "Vitamin supplements",
    ]),
    "Entertainment": (100, 1500,  7, [
        "BookMyShow - movie", "Netflix subscription",
        "Spotify premium", "Ludo outing with friends",
        "Amusement park entry",
    ]),
    "Other":         (50,  1000,  5, [
        "Laundry service", "Haircut", "Birthday gift",
        "Charity donation", "Newspaper subscription",
    ]),
}

conn = get_db()
try:
    # ── Verify user exists ───────────────────────────────────────────────────
    user = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
    if user is None:
        print(f"❌  No user found with id {user_id}.")
        sys.exit(1)

    # ── Fetch category ids ───────────────────────────────────────────────────
    cat_rows = conn.execute("SELECT id, name FROM categories").fetchall()
    cat_map  = {row["name"]: row["id"] for row in cat_rows}

    # ── Build weighted category list ─────────────────────────────────────────
    weighted_cats = []
    for cat_name, (_, _, weight, _) in CATEGORIES.items():
        if cat_name in cat_map:
            weighted_cats.extend([cat_name] * weight)

    # ── Date range: past <months> months ────────────────────────────────────
    end_date   = datetime.today()
    start_date = end_date - timedelta(days=months * 30)

    def random_date(start, end):
        delta = end - start
        return (start + timedelta(days=random.randint(0, delta.days))).strftime("%Y-%m-%d")

    # ── Generate expenses ────────────────────────────────────────────────────
    expenses = []
    for _ in range(count):
        cat_name   = random.choice(weighted_cats)
        min_amt, max_amt, _, descs = CATEGORIES[cat_name]
        amount      = round(random.uniform(min_amt, max_amt), 2)
        description = random.choice(descs)
        date        = random_date(start_date, end_date)
        cat_id      = cat_map[cat_name]
        expenses.append((user_id, amount, cat_id, description, date))

    # ── Insert in a single transaction ───────────────────────────────────────
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category_id, description, date) "
        "VALUES (?, ?, ?, ?, ?)",
        expenses,
    )
    conn.commit()

    # ── Confirm ──────────────────────────────────────────────────────────────
    dates = [e[4] for e in expenses]
    print(f"✅  Inserted {count} expenses for user_id={user_id}")
    print(f"   Date range : {min(dates)}  →  {max(dates)}")
    print()
    print("   Sample records:")
    print(f"   {'#':<4} {'Category':<15} {'Amount (₹)':<12} {'Description':<35} {'Date'}")
    print("   " + "-" * 80)
    for i, (uid, amt, cid, desc, dt) in enumerate(expenses[:5], 1):
        cat_name = next(n for n, cmap_id in cat_map.items() if cmap_id == cid)
        print(f"   {i:<4} {cat_name:<15} {amt:<12.2f} {desc:<35} {dt}")

finally:
    conn.close()
