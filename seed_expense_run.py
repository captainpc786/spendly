"""
Seed script — /seed-expense 3 3 6
user_id=3, count=3, months=6
Run from: c:\Users\DELL\OneDrive\Desktop\expense-tracker
"""
import sys, os, random, datetime, sqlite3

# Use same DB_PATH as database/db.py
DB_PATH = os.path.join(os.path.dirname(__file__), 'spendly.db')

USER_ID = 4
COUNT   = 3
MONTHS  = 6

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")

# ── Step 2: Verify user exists ───────────────────────────────────────
user = conn.execute("SELECT id, username FROM users WHERE id = ?", (USER_ID,)).fetchone()
if not user:
    print(f"No user found with id {USER_ID}.")
    conn.close()
    sys.exit(1)
print(f"Found user: id={user['id']}, username={user['username']}")

# ── Fetch category ids ───────────────────────────────────────────────
cats    = conn.execute("SELECT id, name FROM categories").fetchall()
cat_map = {row['name']: row['id'] for row in cats}

# ── Weighted category pool ───────────────────────────────────────────
POOL = [
    (30, 'Food',          ['Lunch at Subway','Swiggy order','Zomato delivery','Grocery BigBasket','Chai and snacks','Dinner at Dominos'], (50, 800)),
    (20, 'Travel',        ['Ola ride','Uber to airport','Metro card recharge','Auto-rickshaw','Rapido bike'], (20, 500)),
    (15, 'Bills',         ['Electricity bill','Internet recharge','Mobile prepaid','Water bill','OTT subscription'], (200, 3000)),
    (15, 'Shopping',      ['Amazon order','Flipkart sale','New headphones','Clothes shopping','Books'], (200, 5000)),
    (10, 'Health',        ['Pharmacy','Doctor consultation','Lab test','Vitamins'], (100, 2000)),
    (5,  'Entertainment', ['Movie tickets','Gaming recharge','Concert ticket'], (100, 1500)),
    (5,  'Other',         ['Miscellaneous','Gift for friend','Parking fee'], (50, 1000)),
]

weighted = []
for weight, name, descs, rng in POOL:
    cid = cat_map.get(name)
    if cid:
        weighted.extend([(cid, name, descs, rng)] * weight)

# Fall back to first available category if none matched
if not weighted:
    for row in cats:
        weighted.append((row['id'], row['name'], ['Expense'], (100, 1000)))

# ── Generate random dates across past MONTHS months ──────────────────
today      = datetime.date.today()
date_start = (today.replace(day=1) - datetime.timedelta(days=MONTHS * 30))

def rnd_date():
    delta = (today - date_start).days
    return (date_start + datetime.timedelta(days=random.randint(0, delta))).isoformat()

# ── Build rows ───────────────────────────────────────────────────────
rows = []
for _ in range(COUNT):
    cid, cname, descs, (lo, hi) = random.choice(weighted)
    rows.append((USER_ID, round(random.uniform(lo, hi), 2), cid, random.choice(descs), rnd_date()))

# ── Insert in single transaction ─────────────────────────────────────
try:
    conn.execute("BEGIN")
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category_id, description, date) VALUES (?, ?, ?, ?, ?)",
        rows
    )
    conn.commit()
except Exception as exc:
    conn.rollback()
    print(f"ERROR — rolled back: {exc}")
    conn.close()
    sys.exit(1)

# ── Report ───────────────────────────────────────────────────────────
dates = sorted(r[4] for r in rows)
id_to_name = {v: k for k, v in cat_map.items()}
print(f"\n✅  Inserted {len(rows)} expense(s) for user_id={USER_ID}")
print(f"    Date range : {dates[0]} → {dates[-1]}")
print(f"\n    Sample records:")
for uid, amt, cid, desc, date in rows[:5]:
    print(f"      {date}  {id_to_name.get(cid,'?'):<14}  ₹{amt:>8,.2f}  {desc}")

conn.close()
