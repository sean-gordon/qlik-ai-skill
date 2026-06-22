#!/usr/bin/env python3
"""
build_index.py — Embed chunks.jsonl into a searchable index.

Embeddings are computed LOCALLY and FREE. No API key, no network, no per-query
cost. The corpus is tiny (~500 chunks) so indexing takes a few seconds on CPU.

Two backends, one interface:

  --backend chroma   (default)  Persists a Chroma collection to ./chroma_db/.
                                The MCP server reads it directly. Uses Chroma's
                                bundled default embedder (ONNX all-MiniLM-L6-v2,
                                384-dim) — runs on CPU, free, no API key, no extra
                                dependency. Best for Claude Code on individual machines.

  --backend pgvector            Stores chunks + embeddings in PostgreSQL with the
                                pgvector extension. Best for a shared, centrally
                                hosted index used by a whole team. Embeddings are
                                still computed locally with fastembed, so no API
                                key is needed here either.

Usage:
  pip install -r requirements.txt
  python3 build_index.py --backend chroma
  # shared team option:
  export DATABASE_URL="postgresql://user:pass@host:5432/qlik"
  python3 build_index.py --backend pgvector
"""

import argparse
import json
import os
from pathlib import Path

EMBED_MODEL = "all-MiniLM-L6-v2"  # Chroma's bundled default; local, free, 384-dim
EMBED_DIM = 384
COLLECTION = "qlik_knowledge"


def load_chunks(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def embed_local(texts: list[str]) -> list[list[float]]:
    """Local embeddings via sentence-transformers (all-MiniLM-L6-v2, 384-dim),
    matching Chroma's default model so the two backends are interchangeable.
    Downloads the model once (~90MB) then runs fully offline on CPU.
    Only used by the pgvector backend; the Chroma backend embeds internally."""
    from sentence_transformers import SentenceTransformer  # type: ignore
    model = SentenceTransformer(f"sentence-transformers/{EMBED_MODEL}")
    embs = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    return [e.tolist() for e in embs]


def build_chroma(chunks, outdir: Path):
    import chromadb  # type: ignore
    persist = outdir / "chroma_db"
    persist.mkdir(parents=True, exist_ok=True)
    from chromadb.config import Settings
    client = chromadb.PersistentClient(
        path=str(persist),
        settings=Settings(anonymized_telemetry=False)
    )
    # Reset cleanly so re-runs don't duplicate
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    # Use Chroma's built-in fastembed embedder so query-time embedding matches
    from qlik_index import LocalONNXEmbeddingFunction, _model_ready
    model_dir = outdir / "model"
    if not _model_ready(model_dir):
        model_dir = Path(__file__).parent / "model"
    coll = client.create_collection(
        name=COLLECTION,
        embedding_function=LocalONNXEmbeddingFunction(model_dir),
        metadata={"hnsw:space": "cosine"},
    )
    print(f"  embedding {len(chunks)} chunks locally (Chroma default: bge-small)...")
    # Chroma embeds documents itself; we just supply text + metadata
    coll.add(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[{
            "source": c["source"],
            "heading_path": " > ".join(c["heading_path"]),
            "title": c["title"],
            "tags": ",".join(c["tags"]),
        } for c in chunks],
    )
    print(f"  persisted Chroma collection '{COLLECTION}' to {persist}")
    print(f"  collection count: {coll.count()}")


def build_pgvector(chunks):
    import psycopg  # type: ignore
    from pgvector.psycopg import register_vector  # type: ignore
    dsn = os.environ["DATABASE_URL"]
    texts = [c["text"] for c in chunks]
    print(f"  embedding {len(texts)} chunks locally (fastembed: bge-small)...")
    embs = embed_local(texts)
    with psycopg.connect(dsn) as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(conn)
        conn.execute("DROP TABLE IF EXISTS qlik_chunks")
        conn.execute(f"""
            CREATE TABLE qlik_chunks (
                id text PRIMARY KEY,
                source text,
                heading_path text,
                title text,
                tags text[],
                text text,
                embedding vector({EMBED_DIM})
            )
        """)
        with conn.cursor() as cur:
            for c, e in zip(chunks, embs):
                cur.execute(
                    "INSERT INTO qlik_chunks (id,source,heading_path,title,tags,text,embedding) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (c["id"], c["source"], " > ".join(c["heading_path"]), c["title"],
                     c["tags"], c["text"], e),
                )
        conn.execute(
            "CREATE INDEX ON qlik_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50)"
        )
        conn.commit()
    print(f"  loaded {len(chunks)} rows into PostgreSQL table qlik_chunks")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["chroma", "pgvector"], default="chroma")
    ap.add_argument("--chunks", default="chunks.jsonl")
    ap.add_argument("--outdir", default="")
    args = ap.parse_args()

    chunks = load_chunks(Path(args.chunks))
    print(f"Loaded {len(chunks)} chunks")
    if args.backend == "chroma":
        from qlik_index import default_index_dir
        outdir = Path(args.outdir) if args.outdir else default_index_dir()
        build_chroma(chunks, outdir)
    else:
        build_pgvector(chunks)
    print("Done.")


if __name__ == "__main__":
    main()
