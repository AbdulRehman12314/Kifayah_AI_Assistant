import sqlite3
import json
import random
import pandas as pd
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "kifayah_store.db"
DOCS_DIR = BASE_DIR / "company_docs"
KB_DIR = BASE_DIR / "knowledge_base"
KB_DIR.mkdir(parents=True, exist_ok=True)

ORDERS_CSV = KB_DIR / "orders.csv"
REVIEWS_CSV = KB_DIR / "reviews.csv"

VERIFIED_IMAGE_POOLS = {
    "potato": [
        "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=450&q=80",
        "https://images.unsplash.com/photo-1590165482129-1b8b27698780?w=450&q=80",
        "https://images.unsplash.com/photo-1635774855536-9728f2610245?w=450&q=80",
    ],
    "onion": [
        "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=450&q=80",
        "https://images.unsplash.com/photo-1580201092675-a0a6a6cafbb1?w=450&q=80",
        "https://images.unsplash.com/photo-1508747703725-719777637510?w=450&q=80",
    ],
    "tomato": [
        "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=450&q=80",
        "https://images.unsplash.com/photo-1546470427-e26264be0b11?w=450&q=80",
        "https://images.unsplash.com/photo-1561136594-7f68413baa99?w=450&q=80",
    ],
    "carrot": ["https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=450&q=80"],
    "cucumber": ["https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=450&q=80"],
    "spinach": ["https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=450&q=80"],
    "broccoli": ["https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=450&q=80"],
    "garlic": ["https://images.unsplash.com/photo-1540148426945-6cf22a6b2383?w=450&q=80"],
    "ginger": ["https://images.unsplash.com/photo-1615485500704-8e990f9900f7?w=450&q=80"],
    "chilli": ["https://images.unsplash.com/photo-1588252303782-cb80119abd6d?w=450&q=80"],
    "apple": ["https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=450&q=80"],
    "banana": ["https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=450&q=80"],
    "mango": ["https://images.unsplash.com/photo-1553279768-865429fa0078?w=450&q=80"],
    "milk": [
        "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=450&q=80",
        "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=450&q=80",
    ],
    "yogurt": ["https://images.unsplash.com/photo-1488477181946-6428a0291777?w=450&q=80"],
    "cheese": ["https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=450&q=80"],
    "butter": ["https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=450&q=80"],
    "egg": [
        "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=450&q=80",
        "https://images.unsplash.com/photo-1506976785307-8732e854ad03?w=450&q=80",
    ],
    "chicken": [
        "https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=450&q=80",
        "https://images.unsplash.com/photo-1587593810167-a84920ea0781?w=450&q=80",
    ],
    "mutton": ["https://images.unsplash.com/photo-1603048297172-c92544798d5a?w=450&q=80"],
    "beef": ["https://images.unsplash.com/photo-1588168333986-5078d3ae3976?w=450&q=80"],
    "fish": ["https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=450&q=80"],
    "rice": ["https://images.unsplash.com/photo-1586201375761-83865001e31c?w=450&q=80"],
    "flour": ["https://images.unsplash.com/photo-1509440159596-0249088772ff?w=450&q=80"],
    "daal": ["https://images.unsplash.com/photo-1585996845238-808762c22d46?w=450&q=80"],
    "oil": ["https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=450&q=80"],
    "masala": ["https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=450&q=80"],
    "bread": ["https://images.unsplash.com/photo-1549931319-a545dcf3bc73?w=450&q=80"],
    "tea": ["https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9?w=450&q=80"],
    "almond": ["https://images.unsplash.com/photo-1508061253366-f7da158b6d46?w=450&q=80"],
}

CATEGORY_FALLBACK_IMAGES = {
    "Fresh Produce": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=450&q=80",
    "Dairy & Eggs": "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=450&q=80",
    "Meat & Seafood": "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=450&q=80",
    "Staples & Grains": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=450&q=80",
    "Spices & Condiments": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=450&q=80",
    "Bakery & Snacks": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=450&q=80",
}


def clean_product_name(name: str) -> str:
    words = str(name).split()
    cleaned = []
    for w in words:
        if not cleaned or cleaned[-1].lower() != w.lower():
            cleaned.append(w)
    return " ".join(cleaned)


def get_accurate_image(product_name: str, category: str, idx: int = 0, pid: str = "") -> str:
    name_lower = str(product_name).lower()
    for key, pool in VERIFIED_IMAGE_POOLS.items():
        if key in name_lower:
            base = pool[idx % len(pool)]
            return f"{base}&pid={pid}" if pid else base
    base = CATEGORY_FALLBACK_IMAGES.get(category, "https://images.unsplash.com/photo-1542838132-92c53300491e?w=450&q=80")
    return f"{base}&pid={pid}" if pid else base


def _find_inventory_csv() -> Path | None:
    priority_names = [
        "kifayah_supermart_inventory_552.csv"
    ]
    for folder in [DOCS_DIR, KB_DIR, BASE_DIR, Path(".")]:
        if folder.exists():
            for fname in priority_names:
                cand = folder / fname
                if cand.exists() and cand.stat().st_size > 1000:
                    return cand
            matches = sorted(folder.glob("*inventory*.csv"), key=lambda p: p.stat().st_size, reverse=True)
            for m in matches:
                if m.stat().st_size > 1000:
                    return m
    return None


def _find_recipes_csv() -> Path:
    for folder in [DOCS_DIR, KB_DIR, BASE_DIR, Path(".")]:
        if folder.exists():
            matches = sorted(folder.glob("*recipe*.csv"), key=lambda p: p.stat().st_size, reverse=True)
            for m in matches:
                if m.stat().st_size > 2000:
                    return m
    return DOCS_DIR / "recipes_master_100.csv"


def _builtin_fallback_rows() -> list:
    templates = [
        ("Potato (Aloo)", "Kifayah Fresh", "Fresh Produce", "Vegetables", "1 kg", 75, 70, "vegan, gluten-free, budget-friendly, halal", "allergen-free", 1),
        ("Red Onion (Pyaz)", "Kifayah Fresh", "Fresh Produce", "Vegetables", "1 kg", 110, 105, "vegan, gluten-free, budget-friendly, halal", "allergen-free", 1),
        ("Fresh Tomato", "Thatta Farms", "Fresh Produce", "Vegetables", "1 kg", 130, 120, "vegan, gluten-free, budget-friendly, halal", "allergen-free", 1),
        ("Spinach (Palak)", "Sabzi Mandi", "Fresh Produce", "Leafy Greens", "500g", 80, 75, "weight-loss, low-calorie, keto, low-carb, halal", "allergen-free", 2),
        ("Cucumber (Kheera)", "Multan Orchards", "Fresh Produce", "Vegetables", "1 kg", 95, 90, "weight-loss, low-calorie, keto, low-carb, halal", "allergen-free", 2),
        ("Full Cream Milk", "Olper's", "Dairy & Eggs", "Milk", "1 Liter", 290, 280, "vegetarian, gluten-free, halal", "dairy, milk", 1),
        ("Natural Yogurt (Dahi)", "Nestle", "Dairy & Eggs", "Yogurt", "400g", 195, 185, "high-protein, keto, gluten-free, halal", "dairy, milk", 1),
        ("Cheddar Cheese", "Adams", "Dairy & Eggs", "Cheese", "200g", 520, 490, "keto, low-carb, high-protein, halal", "dairy, milk", 2),
        ("Farm Fresh Eggs", "Kifayah Organic", "Dairy & Eggs", "Eggs", "12 pcs", 360, 345, "high-protein, keto, weight-loss, halal", "eggs", 1),
        ("Chicken Boneless Breast", "K&N's", "Meat & Seafood", "Poultry", "1 kg", 950, 910, "high-protein, keto, weight-loss, halal", "allergen-free", 1),
        ("Chicken Curry Cut", "Menu", "Meat & Seafood", "Poultry", "1 kg", 680, 650, "high-protein, keto, gluten-free, halal", "allergen-free", 1),
        ("Mutton Curry Cut", "Kifayah Butcher", "Meat & Seafood", "Mutton", "1 kg", 2100, 1990, "high-protein, keto, family-pack, halal", "allergen-free", 2),
        ("Beef Boneless Boti", "Kifayah Butcher", "Meat & Seafood", "Beef", "1 kg", 1250, 1190, "high-protein, keto, family-pack, halal", "allergen-free", 2),
        ("Rohu Fish Steaks", "Karachi Fishery", "Meat & Seafood", "Seafood", "1 kg", 890, 840, "high-protein, keto, weight-loss, halal", "fish", 2),
        ("Super Kernel Basmati Rice", "Guard", "Staples & Grains", "Rice", "1 kg", 380, 360, "vegan, gluten-free, halal", "allergen-free", 1),
        ("Chakki Whole Wheat Atta", "Sunridge", "Staples & Grains", "Flour", "5 kg", 820, 790, "vegan, high-fiber, halal", "gluten, wheat", 1),
        ("Daal Masoor", "Kifayah Staples", "Staples & Grains", "Pulses", "1 kg", 310, 295, "high-protein, weight-loss, vegan, halal", "allergen-free", 1),
        ("Canola Cooking Oil", "Dalda", "Staples & Grains", "Oils", "1 Liter", 540, 520, "keto, vegan, gluten-free, halal", "allergen-free", 1),
        ("Rolled Oats", "Fauji", "Staples & Grains", "Breakfast", "500g", 420, 395, "weight-loss, diabetic-friendly, vegan, halal", "allergen-free", 2),
        ("Biryani Masala", "Shan", "Spices & Condiments", "Spices", "50g", 130, 120, "vegan, gluten-free, budget-friendly, halal", "allergen-free", 2),
        ("Qorma Masala", "Shan", "Spices & Condiments", "Spices", "50g", 130, 120, "vegan, gluten-free, budget-friendly, halal", "allergen-free", 2),
        ("Karahi Masala", "National", "Spices & Condiments", "Spices", "50g", 125, 115, "vegan, gluten-free, budget-friendly, halal", "allergen-free", 2),
        ("Iodized Salt", "National", "Spices & Condiments", "Salt", "800g", 65, 60, "keto, vegan, budget-friendly, halal", "allergen-free", 1),
        ("Whole Wheat Bran Bread", "Dawn", "Bakery & Snacks", "Bread", "Large", 165, 155, "weight-loss, diabetic-friendly, vegan, halal", "gluten, wheat", 1),
        ("Danedar Black Tea", "Tapal", "Bakery & Snacks", "Tea", "450g", 780, 740, "keto, vegan, gluten-free, halal", "allergen-free", 1),
    ]
    rows = []
    for i, t in enumerate(templates, start=1):
        pid = f"KFY-{i:04d}"
        p_name = f"{t[1]} {t[0]}"
        prio = t[9]
        prio_lbl = {1: "Essential (Priority 1)", 2: "Important (Priority 2)", 3: "Optional / Snack (Priority 3)"}[prio]
        rows.append((
            pid, p_name, t[1], t[2], t[3], t[4],
            t[5], t[6], random.randint(10, 120), t[7], t[8],
            prio, prio_lbl, get_accurate_image(p_name, t[2], i, pid)
        ))
    return rows


def _sync_orders_csv():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM orders", conn)
    df.to_csv(ORDERS_CSV, index=False)


def _sync_reviews_csv():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM reviews", conn)
    df.to_csv(REVIEWS_CSV, index=False)


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT PRIMARY KEY,
                product_name TEXT NOT NULL,
                brand TEXT,
                category TEXT,
                sub_category TEXT,
                unit_quantity TEXT,
                regular_price_pkr INTEGER,
                sale_price_pkr INTEGER,
                stock_level INTEGER,
                dietary_labels TEXT,
                allergen_warnings TEXT,
                priority_tier INTEGER,
                priority_label TEXT,
                image_url TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_name TEXT,
                phone TEXT,
                address TEXT,
                payment_method TEXT,
                items_json TEXT,
                total_amount_pkr INTEGER,
                status TEXT,
                created_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                review_id TEXT PRIMARY KEY,
                order_id TEXT,
                customer_name TEXT,
                rating INTEGER,
                comment TEXT,
                items_summary TEXT,
                created_at TEXT
            )
        """)

        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            rows_to_insert = []
            inv_file = _find_inventory_csv()
            if inv_file is not None:
                try:
                    df = pd.read_csv(inv_file)
                    for idx, r in df.iterrows():
                        pid = str(r.get("product_id", f"KFY-{idx+1:04d}"))
                        p_name = clean_product_name(str(r.get("product_name", f"Item {idx+1}")))
                        cat = str(r.get("category", "Staples & Grains"))
                        img_val = str(r.get("image_url", ""))
                        img = img_val if img_val.startswith("http") else get_accurate_image(p_name, cat, idx, pid)
                        rows_to_insert.append((
                            pid,
                            p_name,
                            str(r.get("brand", "Kifayah Select")),
                            cat,
                            str(r.get("sub_category", cat)),
                            str(r.get("unit_quantity", "1 unit")),
                            int(float(r.get("regular_price_pkr", 100))),
                            int(float(r.get("sale_price_pkr", 100))),
                            int(float(r.get("stock_level", 50))),
                            str(r.get("dietary_labels", "halal")),
                            str(r.get("allergen_warnings", "allergen-free")),
                            int(float(r.get("priority_tier", 2))),
                            str(r.get("priority_label", "Important (Priority 2)")),
                            img
                        ))
                except Exception:
                    rows_to_insert = []

            if not rows_to_insert:
                rows_to_insert = _builtin_fallback_rows()

            conn.executemany(
                "INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                rows_to_insert
            )

        ord_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        if ord_count == 0 and ORDERS_CSV.exists():
            odf = pd.read_csv(ORDERS_CSV)
            for _, r in odf.iterrows():
                conn.execute(
                    "INSERT OR REPLACE INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        str(r["order_id"]), str(r["customer_name"]), str(r["phone"]),
                        str(r["address"]), str(r["payment_method"]), str(r["items_json"]),
                        int(r["total_amount_pkr"]), str(r["status"]), str(r["created_at"])
                    )
                )

        rev_count = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
        if rev_count == 0 and REVIEWS_CSV.exists():
            rdf = pd.read_csv(REVIEWS_CSV)
            for _, r in rdf.iterrows():
                conn.execute(
                    "INSERT OR REPLACE INTO reviews VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        str(r["review_id"]), str(r["order_id"]), str(r["customer_name"]),
                        int(r["rating"]), str(r["comment"]), str(r["items_summary"]), str(r["created_at"])
                    )
                )


def get_products_df() -> pd.DataFrame:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM products", conn)


def get_pakistani_favorites(limit: int = 8) -> pd.DataFrame:
    """Returns everyday Pakistani household favorites for the Dashboard."""
    prods = get_products_df()
    if prods.empty:
        return prods

    pakistani_staples = [
        "basmati rice",
        "chicken",
        "chakki",
        "cooking oil",
        "milk",
        "yogurt",
        "desi ghee",
        "egg",
        "biryani masala",
        "daal masoor",
        "tea",
        "mango",
        "potato",
        "onion",
        "tomato",
        "samosa",
    ]

    picked_rows = []
    seen_ids = set()
    for kw in pakistani_staples:
        matches = prods[prods["product_name"].str.lower().str.contains(kw, na=False)]
        if not matches.empty:
            row = matches.iloc[0]
            if row["product_id"] not in seen_ids:
                picked_rows.append(row)
                seen_ids.add(row["product_id"])
        if len(picked_rows) >= limit:
            break

    if len(picked_rows) < limit:
        for _, r in prods.iterrows():
            if r["product_id"] not in seen_ids:
                picked_rows.append(r)
                seen_ids.add(r["product_id"])
            if len(picked_rows) >= limit:
                break

    return pd.DataFrame(picked_rows)


def place_order(customer_name: str, phone: str, address: str, payment_method: str, cart: dict) -> str:
    init_db()
    order_id = f"ORD-{random.randint(10000, 99999)}"
    total = sum(item["price"] * item["qty"] for item in cart.values())
    now_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (order_id, customer_name, phone, address, payment_method, json.dumps(list(cart.values())), int(total), "Pending", now_str)
        )
        for pid, item in cart.items():
            conn.execute(
                "UPDATE products SET stock_level = MAX(0, stock_level - ?) WHERE product_id = ?",
                (int(item["qty"]), pid)
            )
    _sync_orders_csv()
    return order_id


def get_orders_df() -> pd.DataFrame:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM orders ORDER BY rowid DESC", conn)


def update_order_status(order_id: str, new_status: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE orders SET status = ? WHERE order_id = ?", (new_status, order_id))
    _sync_orders_csv()


def upsert_product(prod_dict: dict):
    with sqlite3.connect(DB_PATH) as conn:
        pid = prod_dict["product_id"]
        img = prod_dict.get("image_url") or get_accurate_image(prod_dict["product_name"], prod_dict["category"], 0, pid)
        conn.execute(
            "INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                pid, prod_dict["product_name"], prod_dict["brand"],
                prod_dict["category"], prod_dict.get("sub_category", "General"),
                prod_dict["unit_quantity"], int(prod_dict["regular_price_pkr"]),
                int(prod_dict["sale_price_pkr"]), int(prod_dict["stock_level"]),
                prod_dict["dietary_labels"], prod_dict["allergen_warnings"],
                int(prod_dict["priority_tier"]), prod_dict["priority_label"], img
            )
        )


def restock_single_product(product_id: str, add_qty: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE products SET stock_level = stock_level + ? WHERE product_id = ?",
            (int(add_qty), product_id)
        )


def restock_all_low_stock(threshold: int = 15, add_qty: int = 50):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE products SET stock_level = stock_level + ? WHERE stock_level < ?",
            (int(add_qty), int(threshold))
        )


def delete_product(product_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM products WHERE product_id = ?", (product_id,))


def add_review(order_id: str, customer_name: str, rating: int, comment: str, items_summary: str) -> str:
    init_db()
    rev_id = f"REV-{random.randint(1000, 9999)}"
    now_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO reviews VALUES (?, ?, ?, ?, ?, ?, ?)",
            (rev_id, order_id, customer_name, int(rating), comment.strip(), items_summary, now_str)
        )
    _sync_reviews_csv()
    return rev_id


def get_reviews_df() -> pd.DataFrame:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM reviews ORDER BY rowid DESC", conn)


def get_recipes_df() -> pd.DataFrame:
    r_path = _find_recipes_csv()
    if r_path.exists():
        return pd.read_csv(r_path)
    return pd.DataFrame(columns=["recipe_id", "recipe_name", "diet_category", "product_id", "product_name", "required_qty", "unit", "is_pantry_staple"])


def add_recipe_item(recipe_name: str, diet_category: str, product_id: str, required_qty: int = 1):
    r_path = _find_recipes_csv()
    rdf = get_recipes_df()
    prods = get_products_df()
    p_match = prods[prods["product_id"] == product_id]
    if p_match.empty:
        return
    p_row = p_match.iloc[0]

    existing = rdf[rdf["recipe_name"].str.lower() == recipe_name.strip().lower()]
    if not existing.empty:
        rec_id = existing.iloc[0]["recipe_id"]
    else:
        rec_id = f"RCP-{rdf['recipe_name'].nunique() + 1:03d}"

    new_row = pd.DataFrame([{
        "recipe_id": rec_id,
        "recipe_name": recipe_name.strip(),
        "diet_category": diet_category.strip(),
        "product_id": product_id,
        "product_name": p_row["product_name"],
        "required_qty": int(required_qty),
        "unit": p_row["unit_quantity"],
        "is_pantry_staple": False
    }])
    rdf = pd.concat([rdf, new_row], ignore_index=True)
    rdf.to_csv(r_path, index=False)


def save_updated_recipe(old_name: str, new_name: str, new_diet: str, items_list: list):
    r_path = _find_recipes_csv()
    rdf = get_recipes_df()
    rec_id = f"RCP-{random.randint(100, 999)}"
    if not rdf.empty and old_name in rdf["recipe_name"].values:
        rec_id = rdf[rdf["recipe_name"] == old_name].iloc[0]["recipe_id"]
        rdf = rdf[rdf["recipe_name"] != old_name]

    new_rows = []
    for it in items_list:
        new_rows.append({
            "recipe_id": rec_id,
            "recipe_name": new_name.strip(),
            "diet_category": new_diet.strip(),
            "product_id": it["product_id"],
            "product_name": it["product_name"],
            "required_qty": int(it["required_qty"]),
            "unit": it.get("unit", "1 unit"),
            "is_pantry_staple": bool(it.get("is_pantry_staple", False)),
        })
    if new_rows:
        rdf = pd.concat([rdf, pd.DataFrame(new_rows)], ignore_index=True)
    rdf.to_csv(r_path, index=False)


def delete_recipe(recipe_name: str):
    r_path = _find_recipes_csv()
    rdf = get_recipes_df()
    if not rdf.empty:
        rdf = rdf[rdf["recipe_name"] != recipe_name]
        rdf.to_csv(r_path, index=False)