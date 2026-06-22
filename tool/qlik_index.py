#!/usr/bin/env python3
"""
qlik_index.py — Shared retrieval core for the Qlik knowledge corpus.

Both the MCP server (qlik_mcp_server.py) and the CLI (qlik_search.py) call
into this module, so the search behaviour is identical no matter how it is
invoked. Embeddings are LOCAL and FREE (Chroma's bundled model). No API key.

Public API:
  search(query, top_k=5, domain=None, backend=None, index_dir=None)
      -> list[(score: float, {"source", "heading_path", "text"})]
  format_hits(query, hits, domain=None) -> str   # human/LLM-readable block

Backend is chosen by the QLIK_BACKEND env var (default "chroma"). The Chroma
index directory defaults to the user cache when an index exists there, with the
bundled chunks.jsonl as a lexical fallback when Chroma is unavailable.
"""

import os
import json
import queue
import re
import threading
from pathlib import Path

EMBED_MODEL = "all-MiniLM-L6-v2"
COLLECTION = "qlik_knowledge"
QUERY_SYNONYMS = {
    "upsert": ["insert", "update", "updated", "primarykey", "modificationtime", "exists"],
}
DEFAULT_SEARCH_TIMEOUT_SECONDS = 8.0

# Domain filters advertised to callers. Kept here so the MCP server, the CLI
# and the docs all describe the same set.
DOMAINS = {
    "backend": "load scripts, ETL, LOAD variants, ApplyMap, joins",
    "frontend": "chart expressions, Set Analysis, Aggr, TOTAL",
    "functions": "exact function signatures, parameters, return types",
    "advanced": "incremental loads, link tables, SCD, cookbook recipes",
    "debugging": "script errors, data model diagnostics, performance",
    "visualisation": "chart selection, KPI design, styling",
    "komment": "Komment write-back extension setup and configuration",
    "set-analysis": "Set Analysis syntax and patterns (cross-cutting)",
    "qvd": "QVD load/store and optimisation (cross-cutting)",
    "section-access": "row-level security (cross-cutting)",
    "performance": "optimisation (cross-cutting)",
}


def _model_ready(model_dir: Path) -> bool:
    onnx_dir = model_dir / "onnx"
    required = (
        "config.json",
        "model.onnx",
        "special_tokens_map.json",
        "tokenizer_config.json",
        "tokenizer.json",
        "vocab.txt",
    )
    return all((onnx_dir / name).exists() for name in required)


class ToolNotReady(RuntimeError):
    """Raised when the index or its dependencies are not available yet.
    Callers should treat this as 'run setup.py', not as a hard failure."""


def _backend() -> str:
    return os.environ.get("QLIK_BACKEND", "chroma")


def _search_timeout_seconds() -> float:
    raw = os.environ.get("QLIK_SEARCH_TIMEOUT_SECONDS", str(DEFAULT_SEARCH_TIMEOUT_SECONDS))
    try:
        return max(0.0, float(raw))
    except ValueError:
        return DEFAULT_SEARCH_TIMEOUT_SECONDS


def default_index_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_CACHE_HOME")
    if base:
        return Path(base) / "qlik-ai-skill" / "index"
    return Path(__file__).parent


def _index_dir(index_dir=None) -> Path:
    if index_dir:
        return Path(index_dir)
    env = os.environ.get("QLIK_INDEX_DIR")
    if env:
        return Path(env)
    cache_dir = default_index_dir()
    if (cache_dir / "chroma_db").exists():
        return cache_dir
    return Path(__file__).parent


_state: dict = {}


# ---- Chroma backend --------------------------------------------------------
class LocalONNXEmbeddingFunction:
    _model = None

    def __init__(self, model_dir: Path):
        self.model_dir = model_dir

    def __call__(self, input):
        if LocalONNXEmbeddingFunction._model is None:
            from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2
            ONNXMiniLM_L6_V2.DOWNLOAD_PATH = self.model_dir
            model = ONNXMiniLM_L6_V2()
            model.DOWNLOAD_PATH = self.model_dir
            LocalONNXEmbeddingFunction._model = model
        return LocalONNXEmbeddingFunction._model(input)

    def embed_query(self, input):
        return self(input)

    def name(self) -> str:
        return "onnx_mini_lm_l6_v2"


def _chroma_collection(index_dir: Path):
    if "coll" not in _state:
        try:
            import chromadb  # type: ignore
        except ImportError as e:
            raise ToolNotReady(f"chromadb not installed: {e}") from e
        db = index_dir / "chroma_db"
        if not db.exists():
            raise ToolNotReady(f"index not built (missing {db})")
        from chromadb.config import Settings
        client = chromadb.PersistentClient(
            path=str(db),
            settings=Settings(anonymized_telemetry=False)
        )
        try:
            model_dir = index_dir / "model"
            if not _model_ready(model_dir):
                model_dir = Path(__file__).parent / "model"
            _state["coll"] = client.get_collection(
                name=COLLECTION,
                embedding_function=LocalONNXEmbeddingFunction(model_dir)
            )
        except Exception as e:  # collection absent / corrupt
            raise ToolNotReady(f"collection '{COLLECTION}' unavailable: {e}") from e
    return _state["coll"]


def _search_chroma(query, top_k, domain, index_dir):
    coll = _chroma_collection(index_dir)
    res = coll.query(query_texts=[query], n_results=max(top_k * 3, top_k))
    docs, metas, dists = res["documents"][0], res["metadatas"][0], res["distances"][0]
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


def _run_with_timeout(fn, args, timeout_seconds):
    if timeout_seconds <= 0:
        return fn(*args)
    result_queue: queue.Queue = queue.Queue(maxsize=1)

    def target():
        try:
            result_queue.put((True, fn(*args)))
        except BaseException as e:
            result_queue.put((False, e))

    worker = threading.Thread(target=target, daemon=True)
    worker.start()
    worker.join(timeout_seconds)
    if worker.is_alive():
        raise TimeoutError(f"search backend timed out after {timeout_seconds:g}s")
    ok, value = result_queue.get()
    if ok:
        return value
    raise value


# ---- pgvector backend ------------------------------------------------------
def _embed_query(text):
    if "embedder" not in _state:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except ImportError as e:
            raise ToolNotReady(f"sentence-transformers not installed: {e}") from e
        _state["embedder"] = SentenceTransformer(f"sentence-transformers/{EMBED_MODEL}")
    return _state["embedder"].encode([text], normalize_embeddings=True)[0].tolist()


def _search_pgvector(query, top_k, domain, index_dir):
    try:
        import psycopg  # type: ignore
        from pgvector.psycopg import register_vector  # type: ignore
    except ImportError as e:
        raise ToolNotReady(f"psycopg/pgvector not installed: {e}") from e
    if "DATABASE_URL" not in os.environ:
        raise ToolNotReady("DATABASE_URL not set for pgvector backend")
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


def _search_jsonl(query, top_k, domain):
    chunks_path = Path(__file__).parent / "chunks.jsonl"
    if not chunks_path.exists():
        raise ToolNotReady(f"fallback chunks missing: {chunks_path}")
    terms = []
    for term in re.findall(r"[a-z0-9]+", query.lower()):
        if len(term) <= 2:
            continue
        terms.append(term)
        terms.extend(QUERY_SYNONYMS.get(term, []))
    scored = []
    for line in chunks_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        chunk = json.loads(line)
        tags = chunk.get("tags", [])
        if domain and domain not in tags:
            continue
        hay = (chunk.get("title", "") + " " + chunk.get("text", "")).lower()
        score = sum(hay.count(term) for term in terms)
        if score:
            scored.append((float(score), {
                "source": chunk.get("source", "?"),
                "heading_path": chunk.get("heading_path", []),
                "text": chunk.get("text", ""),
            }))
    scored.sort(key=lambda item: item[0], reverse=True)
    if not scored:
        return []
    best = scored[0][0] or 1.0
    return [(score / best, chunk) for score, chunk in scored[:top_k]]


# ---- Public API ------------------------------------------------------------
def search(query, top_k=5, domain=None, backend=None, index_dir=None):
    """Return [(score, {source, heading_path, text})] best matches for query.
    Raises ToolNotReady if the index or dependencies are not available."""
    top_k = max(1, min(int(top_k), 10))
    dom = (domain or "").strip() or None
    be = backend or _backend()
    idx = _index_dir(index_dir)
    timeout = _search_timeout_seconds()
    if be == "pgvector":
        return _run_with_timeout(_search_pgvector, (query, top_k, dom, idx), timeout)
    try:
        return _run_with_timeout(_search_chroma, (query, top_k, dom, idx), timeout)
    except Exception:
        return _search_jsonl(query, top_k, dom)


def format_hits(query, hits, domain=None):
    if not hits:
        return f"No passages found for query: {query!r}" + (f" (domain={domain})" if domain else "")
    out = [f"Found {len(hits)} passage(s) for: {query!r}\n"]
    for score, c in hits:
        path = c["heading_path"]
        path = " > ".join(path) if isinstance(path, list) else path
        out.append(f"--- [{c['source']}] {path}  (relevance {score:.2f}) ---\n{c['text']}\n")
    return "\n".join(out)
