#!/usr/bin/env python3
"""
qlik_mcp_server.py — MCP server exposing Qlik knowledge retrieval to Claude.

Embeddings are LOCAL and FREE (fastembed / bge-small). No API key, no network.

Exposes:
  qlik_knowledge_search(query, top_k=5, domain="")
      Semantic search over the Qlik reference corpus. Returns the most relevant
      passages with heading path and source file, so Claude pulls only the
      ~1,500 tokens it needs instead of a whole reference file.
  qlik_knowledge_domains()
      Lists domain filters.

Backend by environment:
  QLIK_BACKEND=chroma    (default) reads ./chroma_db/ from QLIK_INDEX_DIR
  QLIK_BACKEND=pgvector  queries PostgreSQL via DATABASE_URL

Run (stdio transport):
  pip install -r requirements.txt
  python3 qlik_mcp_server.py

Register in Claude Code (~/.claude/mcp.json or project .mcp.json):
  {
    "mcpServers": {
      "qlik-knowledge": {
        "command": "python3",
        "args": ["/abs/path/to/tool/qlik_mcp_server.py"],
        "env": { "QLIK_BACKEND": "chroma",
                 "QLIK_INDEX_DIR": "/abs/path/to/tool" }
      }
    }
  }
No key needed. For pgvector set QLIK_BACKEND=pgvector and DATABASE_URL.
"""

import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

EMBED_MODEL = "all-MiniLM-L6-v2"
COLLECTION = "qlik_knowledge"
BACKEND = os.environ.get("QLIK_BACKEND", "chroma")
INDEX_DIR = Path(os.environ.get("QLIK_INDEX_DIR", Path(__file__).parent))

mcp = FastMCP("qlik-knowledge")
_state: dict = {}


# ---- Chroma backend --------------------------------------------------------
def _chroma_collection():
    if "coll" not in _state:
        import chromadb  # type: ignore
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
        client = chromadb.PersistentClient(path=str(INDEX_DIR / "chroma_db"))
        _state["coll"] = client.get_collection(
            name=COLLECTION, embedding_function=DefaultEmbeddingFunction()
        )
    return _state["coll"]


def _search_chroma(query: str, top_k: int, domain: str | None):
    coll = _chroma_collection()
    where = {"tags": {"$contains": domain}} if domain else None
    # Chroma's contains is substring on the joined tag string; we post-filter to be safe.
    res = coll.query(query_texts=[query], n_results=max(top_k * 3, top_k))
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    dists = res["distances"][0]
    out = []
    for doc, meta, dist in zip(docs, metas, dists):
        if domain and domain not in (meta.get("tags", "").split(",")):
            continue
        out.append((1.0 - dist, {
            "source": meta.get("source", "?"),
            "heading_path": meta.get("heading_path", "").split(" > "),
            "text": doc,
        }))
        if len(out) >= top_k:
            break
    return out


# ---- pgvector backend (query embedding via sentence-transformers MiniLM) ---
def _embed_query(text: str):
    if "embedder" not in _state:
        from sentence_transformers import SentenceTransformer  # type: ignore
        _state["embedder"] = SentenceTransformer(f"sentence-transformers/{EMBED_MODEL}")
    return _state["embedder"].encode([text], normalize_embeddings=True)[0].tolist()


def _search_pgvector(query: str, top_k: int, domain: str | None):
    import psycopg  # type: ignore
    from pgvector.psycopg import register_vector  # type: ignore
    q = _embed_query(query)
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        register_vector(conn)
        if domain:
            rows = conn.execute(
                "SELECT 1 - (embedding <=> %s::vector) AS score, source, heading_path, text "
                "FROM qlik_chunks WHERE %s = ANY(tags) ORDER BY embedding <=> %s::vector LIMIT %s",
                (q, domain, q, top_k),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT 1 - (embedding <=> %s::vector) AS score, source, heading_path, text "
                "FROM qlik_chunks ORDER BY embedding <=> %s::vector LIMIT %s",
                (q, q, top_k),
            ).fetchall()
    return [(r[0], {"source": r[1], "heading_path": r[2].split(" > "), "text": r[3]}) for r in rows]


@mcp.tool()
def qlik_knowledge_search(query: str, top_k: int = 5, domain: str = "") -> str:
    """Search the Qlik Sense reference corpus for the most relevant passages.

    Use this for any Qlik Sense question — scripting, Set Analysis, functions,
    data modelling, visualisation, debugging, Section Access, or Komment write-back.
    Returns only the matching passages, not whole files.

    Args:
        query: A specific question or concept, e.g. "incremental reload upsert pattern"
               or "Sum with TOTAL qualifier syntax". Be specific for best results.
        top_k: Number of passages to return (default 5, max 10).
        domain: Optional filter. One of: backend, frontend, functions, advanced,
                debugging, visualisation, komment, set-analysis, qvd, section-access,
                performance. Leave empty to search everything.

    Returns:
        Formatted passages with source file and heading path for citation.
    """
    top_k = max(1, min(top_k, 10))
    dom = domain.strip() or None
    if BACKEND == "pgvector":
        hits = _search_pgvector(query, top_k, dom)
    else:
        hits = _search_chroma(query, top_k, dom)

    if not hits:
        return f"No passages found for query: {query!r}" + (f" (domain={dom})" if dom else "")

    out = [f"Found {len(hits)} passage(s) for: {query!r}\n"]
    for score, c in hits:
        path = " > ".join(c["heading_path"]) if isinstance(c["heading_path"], list) else c["heading_path"]
        out.append(f"--- [{c['source']}] {path}  (relevance {score:.2f}) ---\n{c['text']}\n")
    return "\n".join(out)


@mcp.tool()
def qlik_knowledge_domains() -> str:
    """List the available domain filters and what each covers, to help target a search."""
    return (
        "Available domains for qlik_knowledge_search:\n"
        "- backend: load scripts, ETL, LOAD variants, ApplyMap, joins\n"
        "- frontend: chart expressions, Set Analysis, Aggr, TOTAL\n"
        "- functions: exact function signatures, parameters, return types\n"
        "- advanced: incremental loads, link tables, SCD, cookbook recipes\n"
        "- debugging: script errors, data model diagnostics, performance\n"
        "- visualisation: chart selection, KPI design, styling\n"
        "- komment: Komment write-back extension setup and configuration\n"
        "- set-analysis / qvd / section-access / performance: cross-cutting topic tags"
    )


if __name__ == "__main__":
    mcp.run()
