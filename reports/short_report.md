# Short Report: Kifayah AI Shopping Assistant

## 1. Business Use Case
Kifayah is a modern e-commerce and retail platform offering diverse products, transaction processing, and customer support. Customers and support staff frequently inquire about ordering workflows, product details, specific transaction statuses (e.g., TX-9921), delivery terms, return policies, and cooking recipe/ingredient mappings. To eliminate hallucinations, prevent support bottlenecks, and ensure strict evidence traceability, this project implements an enterprise-grade **Advanced RAG (Retrieval-Augmented Generation)** assistant.

## 2. Pipeline Architecture
The system incorporates a robust 7-stage Advanced RAG pipeline inspired by Module 09 coursework:
1. **Document Ingestion & Chunking:** Parses structured CSV files (product catalogs, transaction logs, recipe mappings) and unstructured policy documents from `knowledge_base/`, segmenting text into semantic chunks with controlled overlap.
2. **Query Rewriting:** Normalizes colloquial Roman Urdu expressions, typos, and shorthand ecommerce terms into clean English search queries.
3. **Hybrid Search:** Combines dense vector semantic search (`sentence-transformers/all-MiniLM-L6-v2`) with sparse keyword matching (`BM25Okapi`) to ensure exact keyword and ID lookups (e.g., product IDs, transaction codes) never fail.
4. **Reciprocal Rank Fusion (RRF):** Merges semantic and keyword ranking lists into a unified score.
5. **Cross-Encoder Reranking:** Reranks top candidates using `ms-marco-MiniLM-L-6-v2` to prioritize the most relevant context blocks.
6. **Context Neighbour Expansion & Packing:** Automatically appends adjacent chunks from the same file to prevent rule or recipe fragmentation and packs the context window efficiently.
7. **LLM Generation:** Queries the Groq LLM (`llama-3.3-70b-versatile`) under strict system prompt constraints requiring evidence-based answers, source filename citations in brackets, and precise fallback messaging when evidence is missing.

## 3. Retrieval Investigation & Experiments
We evaluated retrieval performance across $k=1$, $k=3$, and $k=5$ using core e-commerce queries:
* **$k=1$:** Highly efficient for exact ID lookups (e.g., transaction logs), but occasionally missed supporting context when queries spanned multiple policy or recipe files.
* **$k=3$ to $k=5$:** Established the optimal operational range, ensuring necessary evidence was captured across CSV tables and policy text.
* **Chunk Size & Overlap Tuning:** Reducing chunk size to 600 with an 80 overlap improved retrieval granularity for tabular transaction rows, while neighbour expansion successfully resolved row-boundary truncation issues.

## 4. Failures, Limitations & Production Readiness
* **Dynamic Inventory & Live Status:** Real-time stock counts and live order shipping updates change dynamically and require direct database integration rather than static CSV snapshots.
* **Tabular Formatting:** Structured CSV data requires careful string conversion during ingestion to maintain column-row alignment for the embedding model.