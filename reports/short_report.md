# Short Report: Kifayah Smart Mart & AI Grocery Copilot

## 1. Business Use Case
**Kifayah Smart Mart** is an AI-powered Pakistani online grocery platform offering a balanced catalog of **552 unique branded supermart products** across 6 core categories (*Staples & Grains, Dairy & Eggs, Meat & Seafood, Spices & Condiments, Bakery & Snacks, and Fresh Produce*), **100 Pakistani & dietary recipes**, real-time cart/order management, and a full store admin portal.

Customers frequently inquire about budget-constrained meal planning (e.g., weekly weight-loss groceries under Rs. 2,500), dish-specific recipe ingredients (*Chicken Biryani, Aloo Gosht, Chicken Karahi*), allergen-safe product filtering, live cart modifications, order tracking, and store policies. To prevent hallucinations, handle real-time inventory mutations, and maintain strict evidence traceability, the system combines **SQLite + CSV Dual Persistence**, **Multi-Step LLM Tool Calling**, and **Advanced RAG**.

## 2. Scaled System Architecture
The application has scaled from a static document-retrieval pipeline into a three-tier interactive architecture:

1. **Dual-Persistence Data Layer (`database.py` & `kifayah_store.db`):**
   * Auto-seeds SQLite from the deduplicated 552-product supermart catalog (`company_docs/kifayah_supermart_inventory_552.csv`) and 100-recipe dataset (`company_docs/recipes_master_100.csv`).
   * Maintains live synchronization between SQLite and CSV logs (`knowledge_base/orders.csv` and `knowledge_base/reviews.csv`), deducting stock automatically upon checkout.
2. **Multi-Step Agentic Tool Layer (`agent_tools.py`):**
   * Powered by Groq LLM (`openai/gpt-oss-120b`) with multi-step function calling (`tool_choice="auto"`), executing up to 4 chained tool steps per turn:
     * `search_products`: Filters live in-stock inventory by keyword (with singular/plural normalization), brand, max PKR budget, dietary goals, and allergen exclusions.
     * `plan_weekly_grocery`: Constructs prioritized, non-repeating budget meal plans (`Priority 1: Essential` $\rightarrow$ `Priority 3: Optional`).
     * `get_recipe_ingredients`: Maps dishes from the 100-recipe master dataset directly to live store SKUs and recommended quantities.
     * `manage_cart` & `checkout_cart`: Executes live cart additions, removals, quantity updates, single-table cost breakdowns, and instant order placement.
3. **Hybrid RAG & Policy Retrieval (`company_docs/`):**
   * Combines dense vector semantic search (`sentence-transformers/all-MiniLM-L6-v2`), sparse keyword matching (`BM25Okapi`), Reciprocal Rank Fusion (RRF), and Cross-Encoder reranking (`ms-marco-MiniLM-L-6-v2`) for unstructured store policies (shipping terms, return policies, food safety SOPs, and store hours).
4. **Full-Stack Customer & Admin UI (`app.py`):**
   * **Customer Portal:** Dashboard with Pakistani Household Favorites, faceted Shop catalog, AI Shopping Copilot with inline product cards and smooth auto-scroll, live cart steppers, real-time order tracking (`Pending` $\rightarrow$ `Packed` $\rightarrow$ `Handed Out for Delivery` $\rightarrow$ `Arrived`), and post-delivery verified reviews.
   * **Admin Portal:** Modal product CRUD (`@st.dialog`) with custom image URL previews, 100-recipe editor modal, visual order status management, customer review logs, and single/bulk low-stock restocking.

## 3. Retrieval & Agent Evaluation Findings
* **Retrieval Granularity ($k=3$ to $k=5$):** Setting top-$k$ between 3 and 5 with chunk size $600$ (overlap $80$) and neighbour expansion eliminated row-boundary truncation across tabular CSV records and policy PDFs.
* **Singular/Plural & Base-Name Deduplication:** Normalizing plural queries (e.g., *onions* $\rightarrow$ *onion*) and deduplicating base product names eliminated repeated pack variants in search results and ensured 100% alignment between AI text responses and inline visual product cards.
* **Multi-Step Tool Chaining:** Replacing single-turn tool execution with a bounded 4-step `tool_choice="auto"` loop resolved chained intent errors (such as removing one item and adding another in a single prompt).

## 4. Production Readiness & Limitations Resolved
* **Resolved — Live Stock & Order Synchronization:** Migrating active products, orders, and reviews from static CSV reads to SQLite with automatic CSV write-back solved the stale-inventory limitation, ensuring real-time stock deductions and live admin status updates.
* **Remaining Scope:** Integrating external payment gateways (JazzCash/EasyPaisa APIs) and role-based multi-user authentication will further prepare the platform for cloud deployment.