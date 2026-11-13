from pathlib import Path
import os
from dotenv import load_dotenv
import re
import hashlib
import json
import sqlite3
from typing import List, Dict, Any

import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
from groq import Groq

from config import (
    KNOWLEDGE_DIR, VECTOR_DB_PATH, EMBEDDING_MODEL, RERANKER_MODEL,
    CHUNK_SIZE, CHUNK_OVERLAP, GROQ_MODEL
)

INSUFFICIENT = "I am sorry, but I couldn't find that information in the Kifayah company records."

# Lazy-loaded singleton models
_embedder = None
_reranker = None

def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder

def _get_reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(RERANKER_MODEL)
    return _reranker

def _read_documents() -> List[Dict[str, Any]]:
    """Loads all PDFs, CSVs, and TXT files from the knowledge directory."""
    records = []
    if not KNOWLEDGE_DIR.exists():
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        return records

    # Read PDFs
    for path in sorted(KNOWLEDGE_DIR.rglob("*.pdf")):
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            text = ""
            for page_num, page in enumerate(reader.pages):
                extracted = page.extract_text()
                if extracted:
                    text += f"\n[Page {page_num + 1}]\n" + extracted + "\n"
            text = text.strip()
            if text:
                records.append({
                    "filename": path.name, "text": text,
                    "document_type": "pdf_document", "status": "current"
                })
        except Exception as e:
            print(f"Error reading PDF {path.name}: {e}")

    # Read CSVs (crucial for inventory, transactions, and recipe mappings)
    for path in sorted(KNOWLEDGE_DIR.rglob("*.csv")):
        try:
            text = path.read_text(encoding="utf-8").strip()
            if text:
                records.append({
                    "filename": path.name, "text": text,
                    "document_type": "csv_data", "status": "current"
                })
        except Exception as e:
            print(f"Error reading CSV {path.name}: {e}")

    # Read TXTs
    for path in sorted(KNOWLEDGE_DIR.rglob("*.txt")):
        try:
            text = path.read_text(encoding="utf-8").strip()
            if text:
                records.append({
                    "filename": path.name, "text": text,
                    "document_type": "text_document", "status": "current"
                })
        except Exception as e:
            print(f"Error reading TXT {path.name}: {e}")

    return records

def _split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Chunk size must be positive and overlap must be smaller than chunk size.")
    chunks, start = [], 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            boundary = max(text.rfind("\n", start, end), text.rfind(". ", start, end), text.rfind(" ", start, end))
            if boundary > start + int(chunk_size * 0.60):
                end = boundary + 1
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks

def rebuild_index(chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> int:
    raw_docs = _read_documents()
    chunks = []
    for doc in raw_docs:
        for i, text in enumerate(_split_text(doc["text"], chunk_size, overlap)):
            chunk_id = len(chunks)
            stable_hash = hashlib.sha1(f'{doc["filename"]}:{i}:{text}'.encode()).hexdigest()
            metadata = {
                "id": chunk_id, "filename": doc["filename"],
                "position": i, "status": doc["status"], "document_type": doc["document_type"]
            }
            chunks.append({"stable_id": stable_hash, "text": text, "metadata": metadata})

    if not chunks:
        raise RuntimeError(f"No documents found in {KNOWLEDGE_DIR}. Please place your company documents inside.")

    model = _get_embedder()
    embeddings = model.encode(
        [c["text"] for c in chunks], normalize_embeddings=True, convert_to_numpy=True
    )

    VECTOR_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(VECTOR_DB_PATH) as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY, text TEXT NOT NULL, metadata TEXT NOT NULL, embedding BLOB NOT NULL
            )"""
        )
        connection.execute("DELETE FROM chunks")
        connection.executemany(
            "INSERT INTO chunks (id, text, metadata, embedding) VALUES (?, ?, ?, ?)",
            [
                (c["stable_id"], c["text"], json.dumps(c["metadata"]), embedding.astype(np.float32).tobytes())
                for c, embedding in zip(chunks, embeddings)
            ],
        )
    return len(chunks)


# ==========================================
# ADVANCED RAG PIPELINE (Module 09 Techniques)
# ==========================================

COMMERCE_SYNONYMS = {
    "aaj": "today", "rate": "price", "kitna": "how much", "kaise": "how",
    "order": "order", "delivery": "delivery", "policy": "policy",
    "return": "return", "refund": "refund", "aloo": "potato", "gosht": "meat",
    "recipe": "recipe", "ingredients": "ingredients", "product": "product", "transaction": "transaction"
}

def _words(text: str) -> List[str]:
    clean = "".join(ch.lower() if ch.isalnum() or ch == "-" else " " for ch in text)
    return clean.split()

def rewrite_query(question: str) -> str:
    """Query Rewriting: Expands and cleans user queries for optimal matching."""
    words = [COMMERCE_SYNONYMS.get(w, w) for w in _words(question)]
    return " ".join(w for w in words if w)

def semantic_search(question: str, k: int = 8) -> List[Dict[str, Any]]:
    model = _get_embedder()
    q_vec = model.encode([question], normalize_embeddings=True)[0]
    
    with sqlite3.connect(VECTOR_DB_PATH) as connection:
        rows = connection.execute("SELECT text, metadata, embedding FROM chunks").fetchall()
    if not rows: return []
        
    texts, metadatas, embeddings = [], [], []
    for text, meta_json, emb_blob in rows:
        texts.append(text)
        metadatas.append(json.loads(meta_json))
        embeddings.append(np.frombuffer(emb_blob, dtype=np.float32))
        
    doc_vecs = np.array(embeddings)
    scores = doc_vecs @ q_vec
    best = np.argsort(-scores)[:k]
    
    return [dict(metadatas[idx], text=texts[idx], score=round(float(scores[idx]), 3)) for idx in best]

def keyword_search(question: str, k: int = 8) -> List[Dict[str, Any]]:
    with sqlite3.connect(VECTOR_DB_PATH) as connection:
        rows = connection.execute("SELECT text, metadata FROM chunks").fetchall()
    if not rows: return []
        
    texts, metadatas = [], []
    for text, meta_json in rows:
        texts.append(text)
        metadatas.append(json.loads(meta_json))
        
    bm25 = BM25Okapi([_words(t) for t in texts])
    scores = bm25.get_scores(_words(question))
    best = np.argsort(-scores)[:k]
    
    return [dict(metadatas[idx], text=texts[idx], score=round(float(scores[idx]), 3)) for idx in best]

def rrf_merge(result_lists: List[List[Dict[str, Any]]], k: int = 60, limit: int = 8) -> List[Dict[str, Any]]:
    """Reciprocal Rank Fusion (RRF) combining semantic meaning and keyword precision."""
    points, keep = {}, {}
    for results in result_lists:
        for rank, piece in enumerate(results, start=1):
            new_points = 1 / (k + rank)
            pid = piece["id"]
            points[pid] = points.get(pid, 0) + new_points
            keep[pid] = piece
    order = sorted(points, key=points.get, reverse=True)[:limit]
    return [dict(keep[i], score=round(points[i], 4)) for i in order]

def hybrid_search(question: str, k: int = 8) -> List[Dict[str, Any]]:
    rewritten = rewrite_query(question)
    return rrf_merge([semantic_search(rewritten, k=k), keyword_search(rewritten, k=k)], limit=k)

def rerank(question: str, found: List[Dict[str, Any]], top_n: int = 4) -> List[Dict[str, Any]]:
    """Cross-Encoder Reranking: Precision scoring of retrieved candidate chunks."""
    if not found: return []
    reranker = _get_reranker()
    scores = reranker.predict([(question, p["text"]) for p in found])
    ranked = sorted(zip(found, scores), key=lambda x: x[1], reverse=True)
    return [dict(p, score=round(float(s), 2)) for p, s in ranked[:top_n]]

def smart_search(question: str, top_n: int = 4) -> List[Dict[str, Any]]:
    return rerank(question, hybrid_search(question, k=10), top_n=top_n)

def multi_search(parts: List[str], k_per_part: int = 2) -> List[Dict[str, Any]]:
    """Multi-Document Search: Handles compound queries across different files."""
    evidence = []
    for part in parts:
        for piece in smart_search(part, top_n=k_per_part):
            if piece["id"] not in [e["id"] for e in evidence]:
                evidence.append(piece)
    return evidence

def add_neighbours(found: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Long Context: Brings adjacent chunks from the same file to prevent chopped information."""
    with sqlite3.connect(VECTOR_DB_PATH) as connection:
        rows = connection.execute("SELECT text, metadata FROM chunks").fetchall()
    all_chunks = [dict(json.loads(meta), text=txt) for txt, meta in rows]

    out, seen = [], set()
    for piece in found:
        for c in all_chunks:
            if c["filename"] == piece["filename"] and c["position"] in (piece["position"], piece["position"] + 1):
                if c["id"] not in seen:
                    seen.add(c["id"])
                    out.append(c)
    return out

def pack_context(found: List[Dict[str, Any]], max_words: int = 1200) -> tuple:
    picked, used = [], 0
    for piece in found:
        n = len(piece["text"].split())
        if used + n > max_words: continue
        picked.append(piece)
        used += n
    return "\n".join(f"[{p['filename']}] {p['text']}" for p in picked), used

RULES = """You are Kifayah AI, an expert retail and customer support assistant.
Answer user inquiries strictly using the provided context from company documents.
Guidelines:
1. Use ONLY facts present in the retrieved context below. Do not guess or hallucinate.
2. If the answer cannot be found in the context, reply exactly: "{INSUFFICIENT}"
3. Cite source filenames in brackets (e.g., [recipe_ingredient_mapping.csv]) for every fact."""

def ask_llm(question: str, found: List[Dict[str, Any]]) -> str:
    if not VECTOR_DB_PATH.exists():
        return "Please rebuild the local vector index from the sidebar first."
    
    context, _ = pack_context(found)
    if not context.strip(): return INSUFFICIENT

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        return "GROQ_API_KEY is missing in your .env file."

    client = Groq(api_key=api_key)
    prompt = f"{RULES}\n\nCONTEXT:\n{context}\n\nQUESTION: {question}\nANSWER:"
    
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL, temperature=0,
            messages=[
                {"role": "system", "content": "You are a precise, evidence-bound RAG assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as exc:
        return f"Error communicating with Groq API: {exc}"