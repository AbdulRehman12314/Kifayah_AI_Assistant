# 🛒 Kifayah Smart Mart & AI Grocery Copilot

An AI-powered Pakistani online grocery store, Enterprise RAG knowledge assistant, and smart shopping agent built with **Streamlit**, **Groq LLM (Function Calling)**, **Hybrid Search + CrossEncoder Reranking**, and **SQLite + CSV dual persistence**[cite: 14].

## 🎥 Demo Videos

* **Kifayah Assistant (Enterprise RAG, Document Lookups & Guardrails):** [Watch Demo Video](https://drive.google.com/file/d/1E1PiGbVb_McoEff2WywpGaBX3kRJlPLs/view?usp=sharing)
* **Kifayah Agent (Recipes, Budget Meal Planner, Live Cart & Checkout):** [Watch Demo Video](https://drive.google.com/file/d/1sOiyDHaH4adq5BzN06McFM6EkajXj7Jh/view?usp=sharing)

---

## ✨ Key Features

### 🛍️ Customer Portal

* **Dashboard & Pakistani Household Favorites:** Displays live catalog metrics, active cart totals, and curated everyday Pakistani kitchen essentials (*Basmati Rice, Chakki Atta, Chicken, Cooking Oil, Milk, Yogurt, Desi Ghee, Eggs, Biryani Masala, Daal, Tea,* and seasonal produce)[cite: 14].
* **Shop & Smart Filtering:** Browse **552 unique, duplicate-free supermart products** across 6 balanced categories (*Staples & Grains, Dairy & Eggs, Meat & Seafood, Spices & Condiments, Bakery & Snacks, Fresh Produce*) with filters for category, brand, dietary goals (`keto`, `high-protein`, `weight-loss`, `vegan`, `diabetic-friendly`, `gluten-free`), allergen exclusions, and max price[cite: 14].
* **AI Shopping Copilot & Enterprise RAG:**
  * **Enterprise Company Knowledge & Policy RAG:** Hybrid semantic + BM25 search with Reciprocal Rank Fusion (RRF), CrossEncoder reranking, Roman Urdu query rewriting, source citations, and prompt-injection/out-of-scope guardrails.
  * **Budget Meal & Grocery Planning:** Generates prioritized weekly/10-day grocery lists within a specified PKR budget while respecting dietary goals and allergies[cite: 14].
  * **100 Pakistani & Diet Recipes:** Fetches exact ingredients for dishes like *Chicken Biryani, Aloo Gosht, Chicken Karahi,* and *Keto Bowls* with one-click **Add All to Cart**[cite: 14].
  * **Natural Language Cart & Cost Control:** Add/remove items, update quantities, view clean single-table cost breakdowns (`Unit Price × Qty = Final Price`), and checkout directly via chat with inline product cards and auto-scroll[cite: 14].
* **Cart, Checkout, Tracking & Reviews:**
  * Live quantity steppers (`➖` / `➕`), automatic free delivery over **Rs. 2,000**, and instant stock deduction upon order placement[cite: 14].
  * Real-time order status tracking (`Pending` → `Packed` → `Handed Out for Delivery` → `Arrived`)[cite: 14].
  * Verified customer reviews unlocked automatically once an order is marked `Arrived`[cite: 14].

### 🛡️ Store Admin Portal

* **Product Inventory Manager:** Full CRUD with modal editing (`@st.dialog`), custom `Image URL` input with live preview, dietary/brand tags, and instant search/category filtering[cite: 14].
* **Recipe Manager:** Manage all **100 store recipes** with search, diet category filters, and an interactive modal editor to modify ingredient quantities or add/remove ingredients[cite: 14].
* **Manage Orders:** Visual order cards with item thumbnails and live status dropdowns synced to SQLite and `knowledge_base/orders.csv`[cite: 14].
* **Customer Reviews & Low-Stock Alerts:** View verified feedback (`knowledge_base/reviews.csv`) and restock individual low-stock items (`< 15` units) or bulk-restock all items in one click[cite: 14].

---

## 📁 Project Structure

```text
Kifaya Assistant/
├── app.py                                      # Main Streamlit Customer & Admin UI (Light & Dark Theme)
├── agent_tools.py                              # Groq LLM multi-step tool calling, RAG bridge & cart/recipe tools
├── rag_engine.py                               # Hybrid Search (BM25 + Embeddings), RRF & CrossEncoder Reranker
├── config.py                                   # Paths, model names & RAG hyperparameters
├── database.py                                 # SQLite & CSV persistence, auto-seeding, CRUD & restock helpers
├── kifayah_store.db                            # Auto-generated SQLite store database
├── kifayah_vector.sqlite3                      # Auto-generated SQLite vector index
├── company_docs/
│   ├── kifayah_supermart_inventory_552.csv     # Balanced 552-product branded Pakistani supermart catalog
│   ├── recipes_master_100.csv                  # 100 Pakistani & dietary recipes mapped to product IDs
│   ├── historical_sales_logs_650.csv           # Historical sales dataset
│   ├── supplier_vendor_directory_40.csv        # Vendor directory
│   └── *.pdf / *.txt                           # Company SOPs, shipping/refund policies & hub hours
├── knowledge_base/
│   ├── orders.csv                              # Live synced customer orders
│   └── reviews.csv                             # Live synced customer reviews
├── .env                                        # API keys (GROQ_API_KEY)
└── README.md
```

---

## 🚀 Setup & Running Instructions

1. **Install Dependencies:**

   ```bash
   pip install streamlit pandas groq python-dotenv sentence-transformers rank-bm25 pypdf numpy
   ```

2. **Configure Environment Variables (`.env`):**
   Create a `.env` file in the project root[cite: 14]:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=openai/gpt-oss-120b
   ```

3. **Run the Application:**

   ```bash
   python -m streamlit run app.py
   ```

   *(Note: If replacing the inventory CSV inside `company_docs/`, delete `kifayah_store.db` once before starting the app so SQLite re-seeds from the updated CSV[cite: 14].)*

---

## 🔐 Admin Portal Credentials

* **Email:** `admin@kifayah.pk`[cite: 14]
* **Password:** `admin123`[cite: 14]
