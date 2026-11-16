# 🛒 Kifayah Smart Mart & AI Grocery Copilot

An AI-powered Pakistani online grocery store and smart shopping assistant built with **Streamlit**, **Groq LLM (Function Calling)**, and **SQLite + CSV dual persistence**.

## ✨ Key Features

### 🛍️ Customer Portal

* **Dashboard & Pakistani Household Favorites:** Displays live catalog metrics, active cart totals, and curated everyday Pakistani kitchen essentials (*Basmati Rice, Chakki Atta, Chicken, Cooking Oil, Milk, Yogurt, Desi Ghee, Eggs, Biryani Masala, Daal, Tea,* and seasonal produce).

* **Shop & Smart Filtering:** Browse **552 unique, duplicate-free supermart products** across 6 balanced categories (*Staples & Grains, Dairy & Eggs, Meat & Seafood, Spices & Condiments, Bakery & Snacks, Fresh Produce*) with filters for category, brand, dietary goals (`keto`, `high-protein`, `weight-loss`, `vegan`, `diabetic-friendly`, `gluten-free`), allergen exclusions, and max price.

* **AI Shopping Copilot:**

  * **Budget Meal & Grocery Planning:** Generates prioritized weekly/10-day grocery lists within a specified PKR budget while respecting dietary goals and allergies.

  * **100 Pakistani & Diet Recipes:** Fetches exact ingredients for dishes like *Chicken Biryani, Aloo Gosht, Chicken Karahi,* and *Keto Bowls* with one-click **Add All to Cart**.

  * **Natural Language Cart & Cost Control:** Add/remove items, update quantities, view clean single-table cost breakdowns (`Unit Price × Qty = Final Price`), and checkout directly via chat with inline product cards and auto-scroll.

* **Cart, Checkout, Tracking & Reviews:**

  * Live quantity steppers (`➖` / `➕`), automatic free delivery over **Rs. 2,000**, and instant stock deduction upon order placement.

  * Real-time order status tracking (`Pending` → `Packed` → `Handed Out for Delivery` → `Arrived`).

  * Verified customer reviews unlocked automatically once an order is marked `Arrived`.

### 🛡️ Store Admin Portal

* **Product Inventory Manager:** Full CRUD with modal editing (`@st.dialog`), custom `Image URL` input with live preview, dietary/brand tags, and instant search/category filtering.

* **Recipe Manager:** Manage all **100 store recipes** with search, diet category filters, and an interactive modal editor to modify ingredient quantities or add/remove ingredients.

* **Manage Orders:** Visual order cards with item thumbnails and live status dropdowns synced to SQLite and `knowledge_base/orders.csv`.

* **Customer Reviews & Low-Stock Alerts:** View verified feedback (`knowledge_base/reviews.csv`) and restock individual low-stock items (`< 15` units) or bulk-restock all items in one click.

## 📁 Project Structure

```
Kifaya Assistant/
├── app.py                                      # Main Streamlit Customer & Admin UI (Light & Dark Theme)
├── agent_tools.py                              # Groq LLM multi-step tool calling & cart/recipe tools
├── database.py                                 # SQLite & CSV persistence, auto-seeding, CRUD & restock helpers
├── kifayah_store.db                            # Auto-generated SQLite database
├── company_docs/
│   ├── kifayah_supermart_inventory_552.csv     # Balanced 552-product branded Pakistani supermart catalog
│   ├── recipes_master_100.csv                  # 100 Pakistani & dietary recipes mapped to product IDs
│   ├── historical_sales_logs_650.csv           # Historical sales dataset
│   └── supplier_vendor_directory_40.csv        # Vendor directory
├── knowledge_base/
│   ├── orders.csv                              # Live synced customer orders
│   └── reviews.csv                             # Live synced customer reviews
├── .env                                        # API keys (GROQ_API_KEY)
└── README.md

```

## 🚀 Setup & Running Instructions

1. **Install Dependencies:**

   ```
   pip install streamlit pandas groq python-dotenv
   
   ```

2. **Configure Environment Variables (`.env`):**
   Create a `.env` file in the project root:

   ```
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=openai/gpt-oss-120b
   
   ```

3. **Run the Application:**

   ```
   python -m streamlit run app.py
   
   ```

   *(Note: If replacing the inventory CSV inside `company_docs/`, delete `kifayah_store.db` once before starting the app so SQLite re-seeds from the updated CSV.)*

## 🔐 Admin Portal Credentials

* **Email:** `admin@kifayah.pk`

* **Password:** `admin123`