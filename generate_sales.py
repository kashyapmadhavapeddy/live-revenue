"""
generate_sales.py
-----------------
Runs continuously and appends one fake sale every 30 seconds to sales_data.csv
Weather-aware: rainy/hot cities get lower sales probability, cool/clear cities get higher
Run this in a SEPARATE terminal before launching the dashboard.
    python generate_sales.py
"""

import csv
import os
import random
import time
from datetime import datetime

# ── OUTPUT FILE ──────────────────────────────────────────────────────────────────
OUTPUT_FILE = "sales_data.csv"
FIELDNAMES  = ["timestamp", "order_id", "product", "category", "price", "quantity", "city", "region", "weather_condition", "revenue"]

# ── PRODUCT CATALOGUE ────────────────────────────────────────────────────────────
PRODUCTS = [
    # (name, category, base_price_min, base_price_max)
    ("UltraBook Pro",       "Electronics",  45000, 85000),
    ("Wireless Earbuds",    "Electronics",   2500,  8000),
    ("Smart Watch",         "Electronics",  12000, 35000),
    ("Office Chair",        "Furniture",     8000, 25000),
    ("Standing Desk",       "Furniture",    15000, 40000),
    ("Running Shoes",       "Apparel",       3000,  9000),
    ("Winter Jacket",       "Apparel",       2500,  7500),
    ("Protein Powder",      "Health",        1500,  4500),
    ("Yoga Mat",            "Health",         800,  2500),
    ("Coffee Maker",        "Appliances",    3500, 12000),
    ("Air Purifier",        "Appliances",    8000, 20000),
    ("Mechanical Keyboard", "Electronics",   4000, 15000),
    ("Monitor 4K",          "Electronics",  18000, 45000),
    ("Water Bottle",        "Health",         500,  1800),
    ("Backpack",            "Apparel",       1500,  5000),
]

# ── CITIES WITH REGIONS ───────────────────────────────────────────────────────────
CITIES = [
    ("Hyderabad",  "South"),
    ("Mumbai",     "West"),
    ("Delhi",      "North"),
    ("Bangalore",  "South"),
    ("Chennai",    "South"),
    ("Kolkata",    "East"),
    ("Pune",       "West"),
    ("Ahmedabad",  "West"),
    ("Jaipur",     "North"),
    ("Lucknow",    "North"),
]

# ── WEATHER CONDITIONS WITH SALES MULTIPLIERS ────────────────────────────────────
# Rain and extreme heat reduce sales; clear weather boosts sales
WEATHER_PROFILES = [
    ("Clear",        1.25),   # best for sales
    ("Partly Cloudy",1.10),
    ("Cloudy",       0.95),
    ("Drizzle",      0.80),
    ("Rain",         0.65),   # reduces sales
    ("Heavy Rain",   0.50),   # severely reduces sales
    ("Thunderstorm", 0.40),   # worst for sales
    ("Extreme Heat", 0.70),   # heat reduces outdoor shopping
    ("Foggy",        0.85),
    ("Windy",        0.90),
]

# ── ORDER ID COUNTER ─────────────────────────────────────────────────────────────
def get_next_order_id():
    if not os.path.exists(OUTPUT_FILE):
        return 1001
    with open(OUTPUT_FILE, "r") as f:
        rows = list(csv.DictReader(f))
        return 1001 + len(rows)

# ── GENERATE ONE SALE ────────────────────────────────────────────────────────────
def generate_sale():
    product_name, category, price_min, price_max = random.choice(PRODUCTS)
    city, region   = random.choice(CITIES)
    weather, mult  = random.choice(WEATHER_PROFILES)

    # Weather affects both quantity and whether sale happens at all
    if random.random() > (0.3 + mult * 0.5):
        quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]
    else:
        quantity = 1

    base_price = random.randint(price_min, price_max)
    # Apply small weather discount/premium
    price = round(base_price * (0.9 + mult * 0.1))
    revenue = price * quantity

    return {
        "timestamp":         datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "order_id":          f"ORD-{get_next_order_id()}",
        "product":           product_name,
        "category":          category,
        "price":             price,
        "quantity":          quantity,
        "city":              city,
        "region":            region,
        "weather_condition": weather,
        "revenue":           revenue,
    }

# ── WRITE HEADER IF NEW FILE ─────────────────────────────────────────────────────
def ensure_file():
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
        print(f"✅ Created {OUTPUT_FILE}")

# ── MAIN LOOP ────────────────────────────────────────────────────────────────────
def main():
    ensure_file()
    print("🚀 Sales generator started — generating one sale every 30 seconds")
    print("   Press Ctrl+C to stop\n")

    count = 0
    while True:
        sale = generate_sale()
        with open(OUTPUT_FILE, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writerow(sale)

        count += 1
        print(f"[{sale['timestamp']}] #{count} | {sale['order_id']} | "
              f"{sale['product']} | ₹{sale['revenue']:,} | "
              f"{sale['city']} | {sale['weather_condition']}")

        time.sleep(30)

if __name__ == "__main__":
    main()