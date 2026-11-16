import json
import streamlit as st
import pandas as pd
from database import (
    init_db, get_products_df, get_pakistani_favorites,
    place_order, get_orders_df, update_order_status,
    upsert_product, delete_product,
    restock_single_product, restock_all_low_stock,
    add_review, get_reviews_df,
    get_recipes_df, add_recipe_item, save_updated_recipe, delete_recipe
)
from agent_tools import run_kifayah_agent

st.set_page_config(
    page_title="Kifayah Smart Mart & AI Agent",
    page_icon="🛒",
    layout="wide"
)

init_db()

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "cart" not in st.session_state:
    st.session_state.cart = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": "Assalam-o-Alaikum! I am **Kifayah Smart Grocery Copilot**. Ask me anything:\n- *\"Make a weekly grocery plan within 2500 PKR for weight-loss\"*\n- *\"Show ingredients for Chicken Biryani or Aloo Gosht\"*\n- *\"Add onions to my cart\"* or *\"Update onion quantity to 3\"*\n- *\"What is my cart total cost?\"* or *\"Checkout my order\"*",
            "products": []
        }
    ]
if "last_shown_products" not in st.session_state:
    st.session_state.last_shown_products = []
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "admin_page" not in st.session_state:
    st.session_state.admin_page = "Products Inventory"
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Dashboard"
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "restocking_product_id" not in st.session_state:
    st.session_state.restocking_product_id = None
if "reviewing_order_id" not in st.session_state:
    st.session_state.reviewing_order_id = None

# ==========================================
# CRISP LIGHT & DARK THEME CSS
# ==========================================
is_dark = st.session_state.dark_mode
if is_dark:
    bg_main = "#0B0F19"
    bg_sidebar = "#111625"
    bg_card = "#161D2F"
    bg_input = "#1E293B"
    text_main = "#F8FAFC"
    text_muted = "#CBD5E1"
    border_col = "#2E3B5B"
    btn_sec_bg = "#1E293B"
    btn_sec_text = "#F8FAFC"
    btn_sec_hover = "#334155"
    pill_bg = "#1E293B"
    pill_text = "#60A5FA"
else:
    bg_main = "#F4F6FB"
    bg_sidebar = "#FFFFFF"
    bg_card = "#FFFFFF"
    bg_input = "#FFFFFF"
    text_main = "#0F172A"
    text_muted = "#475569"
    border_col = "#CBD5E1"
    btn_sec_bg = "#F1F5F9"
    btn_sec_text = "#0F172A"
    btn_sec_hover = "#E2E8F0"
    pill_bg = "#EEF2FF"
    pill_text = "#4338CA"

st.markdown(f"""
<style>
    header[data-testid="stHeader"] {{
        background-color: {bg_main} !important;
        border-bottom: 1px solid {border_col};
    }}
    header[data-testid="stHeader"] * {{
        color: {text_main} !important;
    }}
    .stApp {{
        background-color: {bg_main} !important;
        color: {text_main} !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: {bg_sidebar} !important;
        border-right: 1px solid {border_col};
    }}
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {{
        color: {text_main};
    }}
    .stMarkdown p, .stMarkdown li, .stMarkdown span, label,
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{
        color: {text_main} !important;
    }}

    /* Crisp Markdown Tables in Light & Dark Mode */
    table {{
        width: 100% !important;
        border-collapse: collapse !important;
        margin: 12px 0 !important;
        background-color: {bg_card} !important;
        border: 1px solid {border_col} !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }}
    th {{
        background-color: {bg_input} !important;
        color: {text_main} !important;
        font-weight: 700 !important;
        padding: 10px 12px !important;
        border: 1px solid {border_col} !important;
        text-align: left !important;
    }}
    td {{
        color: {text_main} !important;
        padding: 9px 12px !important;
        border: 1px solid {border_col} !important;
    }}
    tr:nth-child(even) td {{
        background-color: {bg_main} !important;
    }}

    /* Expanders & Alerts */
    [data-testid="stExpander"] {{
        background-color: {bg_card} !important;
        border: 1px solid {border_col} !important;
        border-radius: 12px !important;
        overflow: hidden;
    }}
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] details > summary {{
        background-color: {bg_input} !important;
        color: {text_main} !important;
        border-bottom: 1px solid {border_col} !important;
        padding: 12px 16px !important;
    }}
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary svg {{
        color: {text_main} !important;
        fill: {text_main} !important;
    }}
    [data-testid="stAlert"],
    [data-testid="stAlertContainer"],
    [data-testid="stNotification"],
    div[role="alert"] {{
        background-color: {bg_card} !important;
        color: {text_main} !important;
        border: 1px solid {border_col} !important;
        border-left: 4px solid #6366F1 !important;
        border-radius: 10px !important;
    }}
    [data-testid="stAlert"] p,
    [data-testid="stAlertContainer"] p,
    div[role="alert"] p,
    div[role="alert"] span {{
        color: {text_main} !important;
    }}
    code {{
        background-color: {bg_input} !important;
        color: #38BDF8 !important;
        border: 1px solid {border_col};
        padding: 2px 6px;
        border-radius: 6px;
    }}

    /* Buttons */
    button[kind="secondary"],
    button[kind="secondaryFormSubmit"],
    [data-testid="baseButton-secondary"],
    [data-testid="baseButton-secondaryFormSubmit"] {{
        background-color: {btn_sec_bg} !important;
        color: {btn_sec_text} !important;
        border: 1px solid {border_col} !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }}
    button[kind="secondary"]:hover,
    button[kind="secondaryFormSubmit"]:hover {{
        background-color: {btn_sec_hover} !important;
        border-color: #6366F1 !important;
    }}
    button[kind="primary"],
    button[kind="primaryFormSubmit"],
    [data-testid="baseButton-primary"],
    [data-testid="baseButton-primaryFormSubmit"] {{
        background-color: #4F46E5 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }}
    button[kind="primary"]:hover,
    button[kind="primaryFormSubmit"]:hover {{
        background-color: #4338CA !important;
    }}

    /* Inputs, Dropdowns & Dialog Modals */
    input, textarea,
    [data-baseweb="input"] > div,
    [data-baseweb="select"] > div {{
        background-color: {bg_input} !important;
        color: {text_main} !important;
        border-color: {border_col} !important;
    }}
    [data-baseweb="select"] span,
    [data-baseweb="select"] div,
    [data-baseweb="select"] svg {{
        color: {text_main} !important;
        fill: {text_main} !important;
    }}
    ul[role="listbox"], ul[role="listbox"] li {{
        background-color: {bg_card} !important;
        color: {text_main} !important;
    }}
    ul[role="listbox"] li:hover {{
        background-color: {btn_sec_hover} !important;
    }}
    [data-testid="stNumberInput"] button {{
        background-color: {btn_sec_bg} !important;
        color: {text_main} !important;
        border-color: {border_col} !important;
    }}
    [data-testid="stDialog"] > div,
    [data-testid="stDialog"] [role="dialog"] {{
        background-color: {bg_card} !important;
        color: {text_main} !important;
        border: 1px solid {border_col} !important;
    }}
    [data-testid="stDialog"] p,
    [data-testid="stDialog"] span,
    [data-testid="stDialog"] label,
    [data-testid="stDialog"] div {{
        color: {text_main} !important;
    }}
    input::placeholder, textarea::placeholder {{
        color: {text_muted} !important;
        opacity: 0.75 !important;
    }}

    /* Chat Input & Messages */
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInputContainer"] {{
        background-color: {bg_card} !important;
        border: 1px solid {border_col} !important;
        border-radius: 14px !important;
    }}
    [data-testid="stChatInput"] textarea {{
        background-color: transparent !important;
        color: {text_main} !important;
    }}
    [data-testid="stChatMessage"] {{
        background-color: {bg_card} !important;
        border: 1px solid {border_col};
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }}

    /* Sidebar & Product Cards */
    .brand-box {{
        padding: 10px 6px 14px 6px;
        border-bottom: 1px solid {border_col};
        margin-bottom: 14px;
    }}
    .brand-title {{
        font-size: 1.35rem;
        font-weight: 800;
        color: {text_main} !important;
        margin: 0;
    }}
    .brand-sub {{
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: #6366F1 !important;
        text-transform: uppercase;
    }}
    .user-card {{
        background-color: {bg_card};
        border: 1px solid {border_col};
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 16px;
    }}
    .product-card {{
        background-color: {bg_card};
        border: 1px solid {border_col};
        border-radius: 14px;
        padding: 12px;
        margin-bottom: 10px;
        overflow: hidden !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.10);
        transition: all 0.2s ease;
    }}
    .product-card:hover {{
        transform: translateY(-3px);
        border-color: #6366F1;
    }}
    .product-card img, .product-img {{
        width: 100% !important;
        height: 140px !important;
        max-height: 140px !important;
        object-fit: cover !important;
        display: block !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
    }}
    .product-title {{
        font-weight: 700;
        font-size: 0.94rem;
        color: {text_main} !important;
        margin-bottom: 3px;
        line-height: 1.3;
    }}
    .product-meta {{
        font-size: 0.77rem;
        color: {text_muted} !important;
        margin-bottom: 8px;
    }}
    .tag-pill {{
        display: inline-block;
        background-color: {pill_bg};
        color: {pill_text} !important;
        font-size: 0.67rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 999px;
        margin-right: 4px;
        margin-bottom: 4px;
    }}
    .price-tag {{
        font-size: 1.06rem;
        font-weight: 800;
        color: #10B981 !important;
        margin-top: 6px;
    }}
    .hero-banner {{
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        padding: 24px 28px;
        border-radius: 16px;
        margin-bottom: 20px;
    }}
    .hero-banner h2, .hero-banner p {{
        color: #FFFFFF !important;
    }}
</style>
""", unsafe_allow_html=True)


def add_to_cart_helper(prod: dict, qty: int = 1):
    pid = prod["product_id"]
    if pid in st.session_state.cart:
        st.session_state.cart[pid]["qty"] += qty
    else:
        st.session_state.cart[pid] = {
            "product_id": pid,
            "name": prod["product_name"],
            "price": int(prod["sale_price_pkr"]),
            "qty": qty,
            "image": prod.get("image_url", "")
        }


def render_product_card(prod: dict, key_prefix: str):
    tags = [t.strip() for t in str(prod.get("dietary_labels", "")).split(",") if t.strip()][:3]
    pills_html = "".join([f'<span class="tag-pill">{t}</span>' for t in tags])
    stock = int(prod.get("stock_level", 0))
    stock_badge = f"Stock: {stock}" if stock > 0 else "Out of Stock"

    st.markdown(f"""
    <div class="product-card">
        <img src="{prod.get('image_url', '')}" class="product-img" />
        <div class="product-title">{prod['product_name']}</div>
        <div class="product-meta">{prod.get('brand', 'Kifayah')} · {prod.get('unit_quantity', '')} · {stock_badge}</div>
        <div>{pills_html}</div>
        <div class="price-tag">Rs. {prod['sale_price_pkr']}</div>
    </div>
    """, unsafe_allow_html=True)

    if stock > 0:
        if st.button("Add to Cart", key=f"{key_prefix}_{prod['product_id']}", type="primary", use_container_width=True):
            add_to_cart_helper(prod, 1)
            st.toast(f"Added {prod['product_name']} to cart!")
            st.rerun()
    else:
        st.button("Out of Stock", key=f"{key_prefix}_{prod['product_id']}_oos", disabled=True, use_container_width=True)


# ==========================================
# ADMIN MODE (SIDEBAR + 5 PAGES)
# ==========================================
if st.session_state.admin_logged_in:
    prods_df = get_products_df()
    orders_df = get_orders_df()
    reviews_df = get_reviews_df()
    low_stock_df = prods_df[prods_df["stock_level"] < 15]

    @st.dialog("✏️ Edit Product Details")
    def open_edit_product_modal(prod_dict: dict):
        with st.form("modal_edit_prod_form"):
            c1, c2 = st.columns(2)
            p_name = c1.text_input("Product Name", value=prod_dict["product_name"])
            p_brand = c2.text_input("Brand", value=prod_dict["brand"])

            cats = ["Fresh Produce", "Dairy & Eggs", "Meat & Seafood", "Staples & Grains", "Spices & Condiments", "Bakery & Snacks"]
            curr_cat_idx = cats.index(prod_dict["category"]) if prod_dict["category"] in cats else 0
            c3, c4, c5 = st.columns(3)
            p_cat = c3.selectbox("Category", cats, index=curr_cat_idx)
            p_unit = c4.text_input("Unit Size", value=prod_dict["unit_quantity"])
            p_stock = c5.number_input("Stock Level", min_value=0, max_value=5000, value=int(prod_dict["stock_level"]))

            c6, c7, c8 = st.columns(3)
            p_reg = c6.number_input("Regular Price (PKR)", min_value=10, value=int(prod_dict["regular_price_pkr"]))
            p_sale = c7.number_input("Sale Price (PKR)", min_value=10, value=int(prod_dict["sale_price_pkr"]))
            prio_opts = ["1 - Essential", "2 - Important", "3 - Optional / Snack"]
            curr_prio_idx = (int(prod_dict["priority_tier"]) - 1) if int(prod_dict["priority_tier"]) in [1, 2, 3] else 1
            p_prio = c8.selectbox("Budget Priority", prio_opts, index=curr_prio_idx)

            p_diet = st.text_input("Dietary Tags (comma-separated)", value=prod_dict["dietary_labels"])
            p_allergen = st.text_input("Allergen Warnings", value=prod_dict["allergen_warnings"])

            p_diet = st.text_input("Dietary & Brand Tags (comma-separated)", value=prod_dict["dietary_labels"])
            p_allergen = st.text_input("Allergen Warnings", value=prod_dict["allergen_warnings"])
            p_img = st.text_input("Image URL", value=prod_dict.get("image_url", ""), placeholder="https://...")
            if p_img.strip().startswith("http"):
                st.image(p_img.strip(), width=140)

            if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True) and p_name.strip():
                prio_num = int(p_prio.split(" - ")[0])
                prio_lbl = f"{p_prio.split(' - ')[1]} (Priority {prio_num})"
                upsert_product({
                    "product_id": prod_dict["product_id"],
                    "product_name": p_name.strip(),
                    "brand": p_brand.strip(),
                    "category": p_cat,
                    "sub_category": prod_dict.get("sub_category", p_cat),
                    "unit_quantity": p_unit.strip(),
                    "regular_price_pkr": p_reg,
                    "sale_price_pkr": p_sale,
                    "stock_level": p_stock,
                    "dietary_labels": p_diet.strip(),
                    "allergen_warnings": p_allergen.strip(),
                    "priority_tier": prio_num,
                    "priority_label": prio_lbl,
                    "image_url": prod_dict.get("image_url"),
                })
                st.toast(f"Updated {p_name}!")
                st.rerun()

    with st.sidebar:
        st.markdown("""
        <div class="brand-box">
            <div class="brand-title">🛡️ Kifayah Admin</div>
            <div class="brand-sub">Store Management Portal</div>
        </div>
        """, unsafe_allow_html=True)

        admin_nav = [
            ("Products Inventory", f"📦 Products ({len(prods_df)})"),
            ("Recipe Manager", "🍲 Recipe Manager"),
            ("Manage Orders", f"🚚 Manage Orders ({len(orders_df)})"),
            ("Customer Reviews", f"⭐ Reviews ({len(reviews_df)})"),
            ("Low Stock Alerts", f"⚠️ Low Stock ({len(low_stock_df)})"),
        ]
        for key, label in admin_nav:
            b_type = "primary" if st.session_state.admin_page == key else "secondary"
            if st.button(label, key=f"adm_nav_{key}", type=b_type, use_container_width=True):
                st.session_state.admin_page = key
                st.rerun()

        st.divider()
        new_dark = st.toggle("🌙 Dark Theme", value=st.session_state.dark_mode)
        if new_dark != st.session_state.dark_mode:
            st.session_state.dark_mode = new_dark
            st.rerun()

        st.divider()
        if st.button("🚪 Logout Admin", type="secondary", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.session_state.nav_page = "Dashboard"
            st.rerun()

    # ADMIN PAGE 1: PRODUCTS INVENTORY
    if st.session_state.admin_page == "Products Inventory":
        st.markdown("### 📦 Product Inventory Manager")

        with st.expander("➕ Add New Product", expanded=False):
            with st.form("admin_create_form"):
                c1, c2, c3 = st.columns(3)
                p_id = c1.text_input("Product ID", value=f"KFY-{len(prods_df)+1:04d}")
                p_name = c2.text_input("Product Name", placeholder="e.g., Shan Nihari Masala (100g)")
                p_brand = c3.text_input("Brand", value="Shan")

                c4, c5, c6 = st.columns(3)
                p_cat = c4.selectbox("Category", ["Fresh Produce", "Dairy & Eggs", "Meat & Seafood", "Staples & Grains", "Spices & Condiments", "Bakery & Snacks"])
                p_unit = c5.text_input("Unit Size", value="1 kg")
                p_stock = c6.number_input("Stock Level", min_value=0, max_value=5000, value=50)

                c7, c8, c9 = st.columns(3)
                p_reg = c7.number_input("Regular Price (PKR)", min_value=10, value=250)
                p_sale = c8.number_input("Sale Price (PKR)", min_value=10, value=230)
                p_prio = c9.selectbox("Budget Priority", ["1 - Essential", "2 - Important", "3 - Optional / Snack"])

                c10, c11 = st.columns(2)
                p_diet = c10.text_input("Dietary & Brand Tags", value="halal, vegan, gluten-free")
                p_allergen = c11.text_input("Allergen Warnings", value="allergen-free")
                p_img = st.text_input("Image URL (Optional — auto-assigned if left blank)", placeholder="https://images.unsplash.com/...")

                if st.form_submit_button("Create Product", type="primary") and p_name.strip():
                    prio_num = int(p_prio.split(" - ")[0])
                    prio_lbl = f"{p_prio.split(' - ')[1]} (Priority {prio_num})"
                    upsert_product({
                        "product_id": p_id.strip(),
                        "product_name": p_name.strip(),
                        "brand": p_brand.strip(),
                        "category": p_cat,
                        "sub_category": p_cat,
                        "unit_quantity": p_unit.strip(),
                        "regular_price_pkr": p_reg,
                        "sale_price_pkr": p_sale,
                        "stock_level": p_stock,
                        "dietary_labels": p_diet.strip(),
                        "allergen_warnings": p_allergen.strip(),
                        "priority_tier": prio_num,
                        "priority_label": prio_lbl,
                    })
                    st.success(f"Created {p_name} ({p_id})!")
                    st.rerun()

        sc1, sc2 = st.columns([2, 1])
        admin_search = sc1.text_input("🔍 Search Products by ID, Name, Brand, or Tag", placeholder="Type Chicken, KFY-0025, keto...")
        admin_cat = sc2.selectbox("Filter Category", ["All"] + sorted(prods_df["category"].dropna().unique().tolist()))

        filtered_admin = prods_df
        if admin_search:
            q = admin_search.lower()
            filtered_admin = filtered_admin[
                filtered_admin["product_id"].str.lower().str.contains(q, na=False) |
                filtered_admin["product_name"].str.lower().str.contains(q, na=False) |
                filtered_admin["brand"].str.lower().str.contains(q, na=False) |
                filtered_admin["dietary_labels"].str.lower().str.contains(q, na=False)
            ]
        if admin_cat != "All":
            filtered_admin = filtered_admin[filtered_admin["category"] == admin_cat]

        shown_count = min(40, len(filtered_admin))
        st.caption(f"Showing {shown_count} of {len(filtered_admin)} unique products. Click ✏️ Edit on any card to open the editor.")
        cols = st.columns(4)
        for idx, (_, prod) in enumerate(filtered_admin.head(40).iterrows()):
            with cols[idx % 4]:
                p = prod.to_dict()
                tags = [t.strip() for t in str(p.get("dietary_labels", "")).split(",") if t.strip()][:3]
                pills_html = "".join([f'<span class="tag-pill">{t}</span>' for t in tags])
                st.markdown(f"""
                <div class="product-card">
                    <img src="{p.get('image_url', '')}" class="product-img" />
                    <div class="product-title">{p['product_name']}</div>
                    <div class="product-meta">ID: <b>{p['product_id']}</b> · {p['brand']} · Stock: <b>{p['stock_level']}</b></div>
                    <div>{pills_html}</div>
                    <div class="price-tag">Rs. {p['sale_price_pkr']}</div>
                </div>
                """, unsafe_allow_html=True)
                ec1, ec2 = st.columns(2)
                if ec1.button("✏️ Edit", key=f"edit_{p['product_id']}", type="secondary", use_container_width=True):
                    open_edit_product_modal(p)
                if ec2.button("🗑️ Delete", key=f"del_{p['product_id']}", type="secondary", use_container_width=True):
                    delete_product(p["product_id"])
                    st.toast(f"Deleted {p['product_id']}")
                    st.rerun()

    # ADMIN PAGE 2: RECIPE MANAGER (Modernized Cards + Pencil Edit Modal)
    elif st.session_state.admin_page == "Recipe Manager":
        @st.dialog("✏️ Edit Recipe")
        def open_edit_recipe_modal(r_title: str, sub_df: pd.DataFrame):
            with st.form(f"edit_rcp_modal_{r_title}"):
                c1, c2 = st.columns(2)
                new_title = c1.text_input("Recipe Name", value=r_title)
                new_diet = c2.text_input("Diet Category", value=str(sub_df.iloc[0]["diet_category"]))

                st.markdown("**Current Ingredients (set Qty to 0 to remove):**")
                updated_items = []
                for i, (_, row) in enumerate(sub_df.iterrows()):
                    ic1, ic2 = st.columns([3, 1], vertical_alignment="center")
                    ic1.markdown(f"<div style='font-weight:600;'>{row['product_name']} (`{row['product_id']}`)</div>", unsafe_allow_html=True)
                    q_val = ic2.number_input("Qty", min_value=0, max_value=20, value=int(row["required_qty"]), key=f"rcp_q_{r_title}_{i}", label_visibility="collapsed")
                    if q_val > 0:
                        item_d = row.to_dict()
                        item_d["required_qty"] = q_val
                        updated_items.append(item_d)

                st.markdown("**➕ Add Another Ingredient (Optional):**")
                add_opts = ["None"] + [f"{r['product_id']} — {r['product_name']}" for _, r in prods_df.iterrows()]
                add_sel = st.selectbox("Add Product", add_opts, label_visibility="collapsed")

                if st.form_submit_button("💾 Save Recipe Changes", type="primary", use_container_width=True) and new_title.strip():
                    if add_sel != "None":
                        add_pid = add_sel.split(" — ")[0].strip()
                        pm = prods_df[prods_df["product_id"] == add_pid]
                        if not pm.empty:
                            pr = pm.iloc[0]
                            updated_items.append({
                                "product_id": add_pid,
                                "product_name": pr["product_name"],
                                "required_qty": 1,
                                "unit": pr["unit_quantity"],
                                "is_pantry_staple": False,
                            })
                    save_updated_recipe(r_title, new_title, new_diet, updated_items)
                    st.toast(f"Updated recipe: {new_title}")
                    st.rerun()

        st.markdown("### 🍲 Recipe Manager")
        rdf = get_recipes_df()

        with st.expander("➕ Create New Recipe / Add Ingredient", expanded=False):
            with st.form("recipe_add_form"):
                rc1, rc2, rc3, rc4 = st.columns([2, 1.5, 2, 1])
                r_name = rc1.text_input("Recipe Name", placeholder="e.g., Chicken Qorma")
                r_diet = rc2.text_input("Diet Category", value="Traditional Pakistani")
                prod_options = [f"{r['product_id']} — {r['product_name']}" for _, r in prods_df.iterrows()]
                r_prod_sel = rc3.selectbox("Select Ingredient Product", prod_options)
                r_qty = rc4.number_input("Qty", min_value=1, max_value=20, value=1)

                if st.form_submit_button("Add Recipe Ingredient", type="primary") and r_name.strip():
                    pid_chosen = r_prod_sel.split(" — ")[0].strip()
                    add_recipe_item(r_name, r_diet, pid_chosen, r_qty)
                    st.success(f"Added ingredient to {r_name}!")
                    st.rerun()

        unique_recs = rdf["recipe_name"].unique().tolist() if not rdf.empty else []
        f_col1, f_col2 = st.columns([2.5, 1.2])
        rec_search = f_col1.text_input("🔍 Search Recipes", placeholder="Search across recipes (Biryani, Karahi, Keto, Haleem)...")
        diet_cats = ["All"] + (sorted(rdf["diet_category"].dropna().unique().tolist()) if not rdf.empty else [])
        rec_cat_filter = f_col2.selectbox("Filter Diet Category", diet_cats)

        filtered_recs = unique_recs
        if rec_cat_filter != "All":
            filtered_recs = rdf[rdf["diet_category"] == rec_cat_filter]["recipe_name"].unique().tolist()
        if rec_search:
            filtered_recs = [r for r in filtered_recs if rec_search.lower() in r.lower()]

        st.caption(f"Showing {len(filtered_recs)} of {len(unique_recs)} store recipes · Click ✏️ Edit on any card to modify ingredients")

        r_cols = st.columns(2)
        for idx, r_title in enumerate(filtered_recs):
            sub = rdf[rdf["recipe_name"] == r_title]
            diet_tag = sub.iloc[0]["diet_category"]
            ing_pills = "".join([
                f'<span class="tag-pill">{row["product_name"]} (×{row["required_qty"]})</span>'
                for _, row in sub.iterrows()
            ])
            with r_cols[idx % 2]:
                with st.container(border=True):
                    hc1, hc2, hc3 = st.columns([3.4, 0.8, 0.8], vertical_alignment="center")
                    hc1.markdown(
                        f'<div style="font-weight:800; font-size:1.0rem;">{r_title}</div>'
                        f'<span style="display:inline-block; font-size:0.72rem; background:#6366F122; color:#818CF8; '
                        f'padding:2px 9px; border-radius:999px; margin-top:3px;">{diet_tag}</span>',
                        unsafe_allow_html=True,
                    )
                    if hc2.button("✏️", key=f"edit_rcp_{r_title}_{idx}", type="secondary", use_container_width=True, help="Edit Recipe"):
                        open_edit_recipe_modal(r_title, sub)
                    if hc3.button("🗑️", key=f"del_rcp_{r_title}_{idx}", type="secondary", use_container_width=True, help="Delete Recipe"):
                        delete_recipe(r_title)
                        st.rerun()
                    st.markdown(f'<div style="margin-top:8px; line-height:1.6;">{ing_pills}</div>', unsafe_allow_html=True)

    # ADMIN PAGE 3: MANAGE ORDERS
    elif st.session_state.admin_page == "Manage Orders":
        st.markdown("### 🚚 Manage Customer Orders")
        st.caption("All orders are synced to `knowledge_base/orders.csv` and SQLite.")
        if orders_df.empty:
            st.info("No orders placed yet.")
        else:
            status_options = ["Pending", "Packed", "Handed Out for Delivery", "Arrived"]
            status_colors = {
                "Pending": "#F59E0B",
                "Packed": "#3B82F6",
                "Handed Out for Delivery": "#8B5CF6",
                "Arrived": "#10B981",
            }
            prods_lookup = prods_df.set_index("product_id").to_dict("index") if not prods_df.empty else {}

            for _, o_row in orders_df.iterrows():
                oid = o_row["order_id"]
                curr_status = o_row["status"] if o_row["status"] in status_options else "Pending"
                badge_col = status_colors.get(curr_status, "#6366F1")

                with st.container(border=True):
                    top_info, top_ctrl = st.columns([3.2, 1.3], vertical_alignment="center")
                    top_info.markdown(f"""
                    <div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:12px;">
                        <div>
                            <span style="font-size:1.08rem; font-weight:800; color:#38BDF8;">{oid}</span>
                            <span style="margin-left:8px; background:{badge_col}22; color:{badge_col}; border:1px solid {badge_col};
                                         padding:2px 10px; border-radius:999px; font-size:0.75rem; font-weight:700;">
                                ● {curr_status}
                            </span>
                            <div style="font-size:0.78rem; opacity:0.75; margin-top:3px;">
                                {o_row['created_at']} · {o_row['payment_method']}
                            </div>
                        </div>
                        <div style="font-size:0.84rem; line-height:1.35;">
                            <div><b>{o_row['customer_name']}</b> (`{o_row['phone']}`)</div>
                            <div style="opacity:0.82;">{o_row['address']}</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size:0.72rem; opacity:0.75; text-transform:uppercase;">Total</div>
                            <div style="font-size:1.22rem; font-weight:800; color:#10B981;">Rs. {o_row['total_amount_pkr']:,}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    new_st = top_ctrl.selectbox(
                        "Order Status",
                        status_options,
                        index=status_options.index(curr_status),
                        key=f"st_{oid}",
                    )
                    if new_st != curr_status:
                        update_order_status(oid, new_st)
                        st.toast(f"Order {oid} marked as {new_st}")
                        st.rerun()

                    items = json.loads(o_row["items_json"])
                    st.markdown(f"<div style='font-size:0.84rem; font-weight:700; margin:10px 0 6px 0;'>Ordered Items ({len(items)}):</div>", unsafe_allow_html=True)
                    ic_cols = st.columns(4)
                    for idx, it in enumerate(items):
                        img_url = it.get("image") or prods_lookup.get(it.get("product_id", ""), {}).get(
                            "image_url", "https://images.unsplash.com/photo-1542838132-92c53300491e?w=400&q=80"
                        )
                        with ic_cols[idx % 4]:
                            st.markdown(f"""
                            <div style="background:{bg_main}; border:1px solid {border_col}; border-radius:10px;
                                        padding:8px; margin-bottom:10px; height:152px; display:flex;
                                        flex-direction:column; justify-content:space-between; text-align:center;">
                                <img src="{img_url}" style="width:100%; height:72px; object-fit:cover; border-radius:7px;" />
                                <div style="font-weight:700; font-size:0.80rem; line-height:1.2; height:30px;
                                            overflow:hidden; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;">
                                    {it['name']}
                                </div>
                                <div style="font-size:0.76rem; color:#10B981; font-weight:700;">
                                    Qty: {it['qty']} · Rs. {it['price'] * it['qty']:,}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

    # ADMIN PAGE 4: CUSTOMER REVIEWS
    elif st.session_state.admin_page == "Customer Reviews":
        st.markdown("### ⭐ Customer Reviews & Feedback")
        st.caption("All customer reviews are stored permanently in `knowledge_base/reviews.csv`.")
        if reviews_df.empty:
            st.info("No customer reviews submitted yet.")
        else:
            for _, rev in reviews_df.iterrows():
                with st.container(border=True):
                    rc1, rc2 = st.columns([3, 1])
                    stars = "⭐" * int(rev["rating"])
                    rc1.markdown(f"#### {stars} ({rev['rating']}/5) — Order `{rev['order_id']}`")
                    rc1.write(f"**Customer:** {rev['customer_name']} | **Items:** {rev['items_summary']}")
                    rc1.info(f"\"{rev['comment']}\"")
                    rc2.caption(f"Review ID: `{rev['review_id']}`\n\n{rev['created_at']}")

    # ADMIN PAGE 5: LOW STOCK ALERTS
    elif st.session_state.admin_page == "Low Stock Alerts":
        top_l, top_r = st.columns([3, 1.3])
        top_l.markdown("### ⚠️ Low Stock Alerts (Stock < 15)")
        if not low_stock_df.empty:
            if top_r.button("⚡ Restock All (+50 Units)", type="primary", use_container_width=True):
                restock_all_low_stock(threshold=15, add_qty=50)
                st.session_state.restocking_product_id = None
                st.success("All low-stock items have been restocked by +50 units!")
                st.rerun()

        if st.session_state.restocking_product_id:
            rm = prods_df[prods_df["product_id"] == st.session_state.restocking_product_id]
            if not rm.empty:
                r_item = rm.iloc[0].to_dict()
                with st.container(border=True):
                    st.subheader(f"🔄 Restock Product: {r_item['product_name']} (`{r_item['product_id']}`)")
                    st.write(f"**Brand:** {r_item['brand']} | **Category:** {r_item['category']} | **Current Stock:** `{r_item['stock_level']}` units")
                    with st.form("single_restock_form"):
                        add_q = st.number_input("Quantity to Add to Stock", min_value=1, max_value=2000, value=50)
                        if st.form_submit_button("✅ Confirm Restock", type="primary"):
                            restock_single_product(r_item["product_id"], add_q)
                            st.session_state.restocking_product_id = None
                            st.success(f"Added +{add_q} units to {r_item['product_name']}!")
                            st.rerun()
                    if st.button("Cancel", type="secondary"):
                        st.session_state.restocking_product_id = None
                        st.rerun()

        if low_stock_df.empty:
            st.success("All products have sufficient stock (>= 15)!")
        else:
            st.caption(f"{len(low_stock_df)} products need restocking. Click 🔄 Restock on any item to open its restock panel.")
            cols = st.columns(4)
            for idx, (_, prod) in enumerate(low_stock_df.sort_values("stock_level").iterrows()):
                with cols[idx % 4]:
                    p = prod.to_dict()
                    st.markdown(f"""
                    <div class="product-card">
                        <img src="{p.get('image_url', '')}" class="product-img" />
                        <div class="product-title">{p['product_name']}</div>
                        <div class="product-meta">ID: <b>{p['product_id']}</b> · {p['brand']}</div>
                        <div class="price-tag" style="color:#EF4444 !important;">Low Stock: {p['stock_level']} left</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🔄 Restock", key=f"rstk_{p['product_id']}", type="primary", use_container_width=True):
                        st.session_state.restocking_product_id = p["product_id"]
                        st.rerun()

    st.stop()


# ==========================================
# CUSTOMER PORTAL SIDEBAR
# ==========================================
cart_count = sum(item["qty"] for item in st.session_state.cart.values())
cart_total = sum(item["price"] * item["qty"] for item in st.session_state.cart.values())
orders_df = get_orders_df()
reviews_df = get_reviews_df()

with st.sidebar:
    st.markdown("""
    <div class="brand-box">
        <div class="brand-title">🛒 Kifayah Mart</div>
        <div class="brand-sub">Customer & AI Portal</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="user-card">
        <div style="font-weight:700; font-size:0.95rem;">Sumiya Rashid</div>
        <div style="font-size:0.78rem; opacity:0.80;">Karachi, Pakistan</div>
    </div>
    """, unsafe_allow_html=True)

    nav_items = [
        ("Dashboard", "📊 Dashboard"),
        ("Shop", "🛍️ Shop & Catalog"),
        ("AI Assistant", "✨ AI Shopping Copilot"),
        ("My Cart", f"🛒 My Cart ({cart_count})"),
        ("My Orders", f"📦 My Orders ({len(orders_df)})"),
        ("Track Order", "🚚 Track Order"),
        ("My Reviews", f"⭐ My Reviews ({len(reviews_df)})"),
    ]
    for key, label in nav_items:
        btn_type = "primary" if st.session_state.nav_page == key else "secondary"
        if st.button(label, key=f"nav_{key}", type=btn_type, use_container_width=True):
            st.session_state.nav_page = key
            st.rerun()

    st.divider()
    new_dark = st.toggle("🌙 Dark Theme", value=st.session_state.dark_mode)
    if new_dark != st.session_state.dark_mode:
        st.session_state.dark_mode = new_dark
        st.rerun()

    st.divider()
    if st.button("🔐 Login as Admin", key="nav_admin_login", type="primary" if st.session_state.nav_page == "Admin Login" else "secondary", use_container_width=True):
        st.session_state.nav_page = "Admin Login"
        st.rerun()


# ==========================================
# CUSTOMER PAGE: ADMIN LOGIN
# ==========================================
if st.session_state.nav_page == "Admin Login":
    st.markdown("## 🔐 Admin Portal Authentication")
    st.caption("Authorized store managers only.")
    with st.container(border=True):
        l_col1, l_col2 = st.columns(2)
        admin_email = l_col1.text_input("Admin Email", placeholder="Enter admin email")
        admin_pass = l_col2.text_input("Password", type="password", placeholder="Enter password")
        b1, b2 = st.columns([1, 4])
        if b1.button("Sign In", type="primary", use_container_width=True):
            if admin_email.strip() == "admin@kifayah.pk" and admin_pass.strip() == "admin123":
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("❌ Invalid admin email or password.")
        if b2.button("Back to Store", type="secondary"):
            st.session_state.nav_page = "Dashboard"
            st.rerun()


# ==========================================
# CUSTOMER PAGE 1: DASHBOARD
# ==========================================
elif st.session_state.nav_page == "Dashboard":
    st.markdown("""
    <div class="hero-banner">
        <h2 style="margin:0;">🛒 Welcome to Kifayah Smart Grocery Store</h2>
        <p style="margin:6px 0 0 0; opacity:0.92;">Shop authentic Pakistani groceries, plan budget-friendly meals with AI, and track real-time deliveries.</p>
    </div>
    """, unsafe_allow_html=True)

    prods_df = get_products_df()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Catalog Products", f"{len(prods_df):,}")
    m2.metric("Trusted Brands", f"{prods_df['brand'].nunique() if not prods_df.empty else 0}")
    m3.metric("Active Cart Total", f"Rs. {cart_total:,}", delta=f"{cart_count} items")
    m4.metric("Orders Placed", f"{len(orders_df)}")

    st.markdown("---")
    st.subheader("🇵🇰 Pakistani Household Favorites")
    st.caption("Rozmarra ke sabse zyada pasand kiye jane wale Pakistani kitchen essentials aur fresh items.")
    fav_df = get_pakistani_favorites(limit=8)
    cols = st.columns(4)
    for idx, (_, prod) in enumerate(fav_df.iterrows()):
        with cols[idx % 4]:
            render_product_card(prod.to_dict(), key_prefix="dash")


# ==========================================
# CUSTOMER PAGE 2: SHOP & CATALOG
# ==========================================
elif st.session_state.nav_page == "Shop":
    st.title("🛍️ Kifayah Shop & Catalog")

    df = get_products_df()
    with st.expander("🔍 Search & Filter Products", expanded=True):
        f1, f2, f3, f4, f5 = st.columns(5)
        search_q = f1.text_input("Search Name / Keyword", placeholder="Chicken, Rice, Tea...")
        cat_filter = f2.selectbox("Category", ["All"] + (sorted(df["category"].dropna().unique().tolist()) if not df.empty else []))
        brand_filter = f3.selectbox("Brand", ["All"] + (sorted(df["brand"].dropna().unique().tolist()) if not df.empty else []))
        diet_filter = f4.selectbox("Dietary Goal", ["All", "keto", "high-protein", "weight-loss", "vegan", "diabetic-friendly", "gluten-free"])
        allergy_filter = f5.selectbox("Exclude Allergen", ["None", "dairy", "eggs", "gluten", "tree-nuts", "peanuts", "fish"])
        max_p = st.slider("Max Price (PKR)", min_value=50, max_value=5000, value=3000, step=50)

    filtered = df[df["sale_price_pkr"] <= max_p] if not df.empty else df
    if not filtered.empty:
        if search_q:
            filtered = filtered[filtered["product_name"].str.lower().str.contains(search_q.lower(), na=False)]
        if cat_filter != "All":
            filtered = filtered[filtered["category"] == cat_filter]
        if brand_filter != "All":
            filtered = filtered[filtered["brand"] == brand_filter]
        if diet_filter != "All":
            filtered = filtered[filtered["dietary_labels"].str.lower().str.contains(diet_filter, na=False)]
        if allergy_filter != "None":
            filtered = filtered[~filtered["allergen_warnings"].str.lower().str.contains(allergy_filter, na=False)]

    if not filtered.empty:
        filtered = filtered.assign(
            _base=filtered["product_name"].str.split(" (", regex=False).str[0].str.split(" - ", regex=False).str[0].str.lower()
        )
        filtered = filtered.drop_duplicates(subset=["_base"]).drop(columns=["_base"])

    display_df = filtered.head(40)
    st.markdown(f"**Showing {len(display_df)} of {len(filtered)} distinct products**")

    cols = st.columns(4)
    for idx, (_, prod) in enumerate(display_df.iterrows()):
        with cols[idx % 4]:
            render_product_card(prod.to_dict(), key_prefix="shop")


# ==========================================
# CUSTOMER PAGE 3: AI COPILOT + LIVE CART
# ==========================================
elif st.session_state.nav_page == "AI Assistant":
    st.markdown("""
    <div style="margin-bottom:12px;">
        <h2 style="margin:0;">✨ Kifayah Smart Grocery Copilot</h2>
        <p style="margin:2px 0 0 0; opacity:0.8;">Budget meal planning · Recipe ingredient builder · Allergy-safe search · Instant cart control</p>
    </div>
    """, unsafe_allow_html=True)

    q_cols = st.columns(4)
    quick_prompts = [
        "Plan a Rs. 2,500 weight-loss grocery list",
        "Ingredients for Chicken Biryani",
        "What is my cart total cost?",
        "Add all shown items to cart"
    ]
    triggered_quick = None
    for idx, qp in enumerate(quick_prompts):
        if q_cols[idx].button(f"✨ {qp}", type="secondary", use_container_width=True):
            triggered_quick = qp

    chat_col, cart_col = st.columns([2.2, 1.1])

    with chat_col:
        for m_idx, msg in enumerate(st.session_state.chat_history):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

                msg_products = msg.get("products", [])
                if msg["role"] == "assistant" and msg_products:
                    st.markdown("---")
                    if st.button("➕ Add All Items Above to Cart", key=f"add_all_msg_{m_idx}", type="primary"):
                        for p in msg_products:
                            add_to_cart_helper(p, int(p.get("recommended_qty", 1)))
                        st.toast("Added all items to cart!")
                        st.rerun()

                    p_cols = st.columns(3)
                    for p_i, p in enumerate(msg_products[:9]):
                        with p_cols[p_i % 3]:
                            render_product_card(p, key_prefix=f"ai_m{m_idx}_{p_i}")

        st.markdown('<div id="chat-bottom-anchor"></div>', unsafe_allow_html=True)
        st.components.v1.html(
            """
            <script>
                const anchor = window.parent.document.getElementById('chat-bottom-anchor');
                if (anchor) { anchor.scrollIntoView({ behavior: 'smooth', block: 'end' }); }
            </script>
            """,
            height=0,
        )

        user_prompt = st.chat_input("Ask for a recipe, budget plan (e.g. 3000 PKR), cost breakdown, or cart update...")
        final_query = triggered_quick or user_prompt

        if final_query:
            st.session_state.chat_history.append({"role": "user", "content": final_query, "products": []})
            with st.spinner("Kifayah Copilot is Thinking..."):
                res = run_kifayah_agent(
                    final_query,
                    st.session_state.chat_history,
                    st.session_state.cart,
                    st.session_state.last_shown_products
                )
            turn_products = res["shown_products"] if res["shown_products"] != st.session_state.last_shown_products else []
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": res["reply_text"],
                "products": turn_products
            })
            st.session_state.last_shown_products = res["shown_products"]
            st.session_state.cart = res["cart"]
            if res["order_placed_id"]:
                st.session_state.last_shown_products = []
                st.success(f"🎉 Order Placed Successfully! Tracking ID: **{res['order_placed_id']}**")
            st.rerun()

    with cart_col:
        with st.container(border=True):
            st.markdown("### 🛒 Live Cart Summary")
            if not st.session_state.cart:
                st.info("Cart is empty. Ask Copilot or browse Shop to add items!")
            else:
                subtotal = 0
                for pid in list(st.session_state.cart.keys()):
                    item = st.session_state.cart[pid]
                    line_total = item["price"] * item["qty"]
                    subtotal += line_total
                    with st.container(border=True):
                        ic1, ic2 = st.columns([1, 2.4])
                        if item.get("image"):
                            ic1.image(item["image"], use_container_width=True)
                        ic2.markdown(f"**{item['name']}**\n\n`Rs. {item['price']}` × **{item['qty']}** = **Rs. {line_total:,}**")
                        b_minus, b_plus, b_del = ic2.columns(3)
                        if b_minus.button("➖", key=f"m_{pid}", type="secondary", use_container_width=True):
                            if item["qty"] > 1:
                                st.session_state.cart[pid]["qty"] -= 1
                            else:
                                st.session_state.cart.pop(pid)
                            st.rerun()
                        if b_plus.button("➕", key=f"p_{pid}", type="secondary", use_container_width=True):
                            st.session_state.cart[pid]["qty"] += 1
                            st.rerun()
                        if b_del.button("🗑️", key=f"d_{pid}", type="secondary", use_container_width=True):
                            st.session_state.cart.pop(pid)
                            st.rerun()

                delivery_fee = 0 if subtotal >= 2000 else 150
                grand_total = subtotal + delivery_fee
                st.markdown(f"**Subtotal:** Rs. {subtotal:,} | **Delivery:** {'FREE' if delivery_fee == 0 else f'Rs. {delivery_fee}'}")
                st.markdown(f"### Total: Rs. {grand_total:,}")
                if st.button("Proceed to Checkout →", type="primary", use_container_width=True):
                    st.session_state.nav_page = "My Cart"
                    st.rerun()


# ==========================================
# CUSTOMER PAGE 4: MY CART & CHECKOUT
# ==========================================
elif st.session_state.nav_page == "My Cart":
    st.markdown("""
    <div style="margin-bottom:14px;">
        <h3 style="margin:0; font-size:1.45rem;">🛒 My Shopping Cart & Checkout</h3>
        <p style="margin:2px 0 0 0; font-size:0.86rem; opacity:0.78;">Review your items, adjust quantities, and complete your delivery details.</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.cart:
        st.info("Your cart is currently empty.")
        if st.button("Browse Shop", type="primary"):
            st.session_state.nav_page = "Shop"
            st.rerun()
    else:
        left_c, right_c = st.columns([2.1, 1.15], gap="large")
        subtotal = 0

        with left_c:
            top_bar_l, top_bar_r = st.columns([3, 1])
            top_bar_l.markdown(f"**Cart Items ({sum(i['qty'] for i in st.session_state.cart.values())})**")
            if top_bar_r.button("🗑️ Clear Cart", type="secondary", use_container_width=True):
                st.session_state.cart.clear()
                st.rerun()

            for pid in list(st.session_state.cart.keys()):
                item = st.session_state.cart[pid]
                line_total = item["price"] * item["qty"]
                subtotal += line_total

                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([0.75, 2.4, 1.65, 1.0], vertical_alignment="center")
                    if item.get("image"):
                        c1.markdown(
                            f'<img src="{item["image"]}" style="width:58px; height:58px; object-fit:cover; border-radius:10px; display:block;" />',
                            unsafe_allow_html=True,
                        )
                    c2.markdown(
                        f'<div style="font-weight:700; font-size:0.94rem; line-height:1.3;">{item["name"]}</div>'
                        f'<div style="font-size:0.79rem; opacity:0.75; margin-top:2px;">Unit Price: Rs. {item["price"]:,}</div>',
                        unsafe_allow_html=True,
                    )

                    q_minus, q_val, q_plus = c3.columns([1.1, 0.8, 1.1], vertical_alignment="center")
                    if q_minus.button("➖", key=f"cpg_m_{pid}", type="secondary", use_container_width=True):
                        if item["qty"] > 1:
                            st.session_state.cart[pid]["qty"] -= 1
                        else:
                            st.session_state.cart.pop(pid)
                        st.rerun()
                    q_val.markdown(
                        f'<div style="text-align:center; font-weight:800; font-size:0.98rem;">{item["qty"]}</div>',
                        unsafe_allow_html=True,
                    )
                    if q_plus.button("➕", key=f"cpg_p_{pid}", type="secondary", use_container_width=True):
                        st.session_state.cart[pid]["qty"] += 1
                        st.rerun()

                    c4.markdown(
                        f'<div style="text-align:right; font-weight:800; font-size:1.0rem; color:#10B981;">Rs. {line_total:,}</div>',
                        unsafe_allow_html=True,
                    )

        with right_c:
            with st.container(border=True):
                delivery_fee = 0 if subtotal >= 2000 else 150
                grand_total = subtotal + delivery_fee
                free_ship_note = (
                    "🎉 You unlocked FREE delivery!"
                    if delivery_fee == 0
                    else f"Add Rs. {2000 - subtotal:,} more for FREE delivery"
                )

                st.markdown(f"""
                <div style="font-weight:800; font-size:1.12rem; margin-bottom:10px;">🧾 Order Summary</div>
                <div style="display:flex; justify-content:space-between; font-size:0.88rem; margin-bottom:6px;">
                    <span style="opacity:0.8;">Subtotal</span>
                    <span style="font-weight:600;">Rs. {subtotal:,}</span>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.88rem; margin-bottom:8px;">
                    <span style="opacity:0.8;">Delivery Fee</span>
                    <span style="font-weight:600; color:{'#10B981' if delivery_fee == 0 else 'inherit'};">
                        {'FREE' if delivery_fee == 0 else f'Rs. {delivery_fee}'}
                    </span>
                </div>
                <div style="font-size:0.76rem; color:#6366F1; margin-bottom:10px;">{free_ship_note}</div>
                <div style="display:flex; justify-content:space-between; align-items:center;
                            padding-top:10px; border-top:1px solid {border_col}; margin-bottom:12px;">
                    <span style="font-weight:700; font-size:0.98rem;">Grand Total</span>
                    <span style="font-weight:800; font-size:1.25rem; color:#10B981;">Rs. {grand_total:,}</span>
                </div>
                """, unsafe_allow_html=True)

                cust_name = st.text_input("Full Name", value="Sumiya Rashid")
                cust_phone = st.text_input("Phone Number", value="0300-1234567")
                cust_addr = st.text_area("Delivery Address", value="Gulshan-e-Iqbal, Karachi", height=62)
                pay_method = st.selectbox("Payment Method", ["Cash on Delivery (COD)", "JazzCash", "EasyPaisa", "Credit/Debit Card"])

                if st.button("✅ Confirm & Place Order", type="primary", use_container_width=True):
                    oid = place_order(cust_name, cust_phone, cust_addr, pay_method, st.session_state.cart)
                    st.session_state.cart.clear()
                    st.success(f"🎉 Order Confirmed! ID: **{oid}**")
                    st.balloons()


# ==========================================
# CUSTOMER PAGE 5: MY ORDERS
# ==========================================
elif st.session_state.nav_page == "My Orders":
    st.title("📦 My Orders History")
    if orders_df.empty:
        st.info("No orders placed yet.")
    else:
        reviewed_order_ids = set(reviews_df["order_id"].tolist()) if not reviews_df.empty else set()
        prods_lookup = get_products_df().set_index("product_id").to_dict("index")

        status_colors = {
            "Pending": "#F59E0B",
            "Packed": "#3B82F6",
            "Handed Out for Delivery": "#8B5CF6",
            "Arrived": "#10B981",
        }

        for _, row in orders_df.iterrows():
            oid = row["order_id"]
            status = row["status"]
            badge_col = status_colors.get(status, "#6366F1")

            with st.container(border=True):
                st.markdown(f"""
                <div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center;
                            padding-bottom:12px; margin-bottom:14px; border-bottom:1px solid {border_col}; gap:12px;">
                    <div>
                        <span style="font-size:1.15rem; font-weight:800; color:#38BDF8;">{oid}</span>
                        <span style="margin-left:10px; background:{badge_col}22; color:{badge_col}; border:1px solid {badge_col};
                                     padding:3px 10px; border-radius:999px; font-size:0.78rem; font-weight:700;">
                            ● {status}
                        </span>
                        <div style="font-size:0.80rem; opacity:0.75; margin-top:4px;">
                            Placed on {row['created_at']} · {row['payment_method']}
                        </div>
                    </div>
                    <div style="font-size:0.86rem; line-height:1.4;">
                        <div><b>Customer:</b> {row['customer_name']}</div>
                        <div style="opacity:0.85;"><b>Address:</b> {row['address']}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:0.75rem; opacity:0.75; text-transform:uppercase;">Order Total</div>
                        <div style="font-size:1.35rem; font-weight:800; color:#10B981;">Rs. {row['total_amount_pkr']:,}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                items = json.loads(row["items_json"])
                st.markdown(f"**Ordered Items ({len(items)}):**")
                ic_cols = st.columns(4)
                for idx, it in enumerate(items):
                    img_url = it.get("image") or prods_lookup.get(it.get("product_id", ""), {}).get(
                        "image_url", "https://images.unsplash.com/photo-1542838132-92c53300491e?w=400&q=80"
                    )
                    with ic_cols[idx % 4]:
                        st.markdown(f"""
                        <div style="background:{bg_main}; border:1px solid {border_col}; border-radius:12px;
                                    padding:10px; margin-bottom:12px; height:168px; display:flex;
                                    flex-direction:column; justify-content:space-between; text-align:center;">
                            <img src="{img_url}" style="width:100%; height:82px; object-fit:cover; border-radius:8px;" />
                            <div style="font-weight:700; font-size:0.82rem; line-height:1.25; height:32px;
                                        overflow:hidden; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;">
                                {it['name']}
                            </div>
                            <div style="font-size:0.78rem; color:#10B981; font-weight:700;">
                                Qty: {it['qty']} · Rs. {it['price'] * it['qty']:,}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                if status == "Arrived":
                    st.markdown("")
                    if oid in reviewed_order_ids:
                        st.success("✅ You have already reviewed this order.")
                    else:
                        if st.button(f"⭐ Write a Review for {oid}", key=f"rev_btn_{oid}", type="primary"):
                            st.session_state.reviewing_order_id = oid

                        if st.session_state.reviewing_order_id == oid:
                            with st.form(f"rev_form_{oid}"):
                                rating = st.slider("Rating (1 to 5 Stars)", min_value=1, max_value=5, value=5)
                                comment = st.text_area("Your Feedback", placeholder="Share your experience with product quality & delivery...")
                                if st.form_submit_button("Submit Review", type="primary") and comment.strip():
                                    items_sum = ", ".join([f"{i['name']} (x{i['qty']})" for i in items])
                                    add_review(oid, row["customer_name"], rating, comment, items_sum)
                                    st.session_state.reviewing_order_id = None
                                    st.success("Thank you! Your review has been saved to `reviews.csv`.")
                                    st.rerun()


# ==========================================
# CUSTOMER PAGE 6: TRACK ORDER
# ==========================================
elif st.session_state.nav_page == "Track Order":
    st.title("🚚 Track Your Order")
    track_id = st.text_input("Enter Exact Order ID", placeholder="ORD-XXXXX").strip().upper()
    if st.button("Track Status", type="primary"):
        match = orders_df[orders_df["order_id"] == track_id]
        if match.empty:
            st.error(f"❌ Order ID `{track_id}` not found.")
        else:
            order = match.iloc[0]
            status = order["status"]
            st.success(f"✅ Order Found: **{track_id}**")

            steps = ["Pending", "Packed", "Handed Out for Delivery", "Arrived"]
            curr_idx = steps.index(status) if status in steps else 0
            st.progress((curr_idx + 1) / len(steps))

            cols = st.columns(4)
            for idx, step_name in enumerate(steps):
                if idx <= curr_idx:
                    cols[idx].success(f"✔ {step_name}")
                else:
                    cols[idx].info(f"⏳ {step_name}")


# ==========================================
# CUSTOMER PAGE 7: MY REVIEWS
# ==========================================
elif st.session_state.nav_page == "My Reviews":
    st.title("⭐ My Submitted Reviews")
    if reviews_df.empty:
        st.info("You haven't submitted any reviews yet. Once an order status is marked 'Arrived' by Admin, you can review it in 'My Orders'.")
    else:
        for _, rev in reviews_df.iterrows():
            with st.container(border=True):
                stars = "⭐" * int(rev["rating"])
                st.markdown(f"### {stars} ({rev['rating']}/5) — Order `{rev['order_id']}`")
                st.caption(f"Submitted on: {rev['created_at']} | Items: {rev['items_summary']}")
                st.write(f"\"{rev['comment']}\"")