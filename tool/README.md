# Qlik Knowledge Retrieval Tool

This directory turns the skill's reference corpus into a semantic search tool that
Claude can call, so it pulls only the passages it needs (~1,500 tokens) instead of
loading whole reference files (7k–14k tokens each).

**Everything runs locally and free.** Embeddings use Chroma's bundled model
(ONNX `all-MiniLM-L6-v2`, 384-dim) on CPU — no API key, no network at query time,
no per-query cost. The model downloads once (~90MB) on the first build.

## What's here

| File | Purpose |
|------|---------|
| `setup.py` | **One-command bootstrap** — creates the venv, installs deps, builds the index, prints the MCP registration command. Run with any Python 3.10+. |
| `qlik_index.py` | Shared search core (Chroma/pgvector). Used by both the server and the CLI so they behave identically. |
| `qlik_mcp_server.py` | The MCP server exposing `qlik_knowledge_search` / `qlik_knowledge_domains` to Claude. |
| `qlik_search.py` | Command-line search — same engine, callable from the shell. Lets the skill retrieve in the current session without an MCP restart. |
| `build_chunks.py` | Parses `../references/*.md` into `chunks.jsonl` (one retrievable passage per heading). No dependencies. |
| `build_index.py` | Builds the search index. Backends: `chroma` (default) and `pgvector`. |
| `chunks.jsonl` | Pre-built chunks (498). Regenerate after editing references. |
| `requirements.txt` | Python dependencies. |

## Quick start

One command builds everything (venv + dependencies + index when the local
filesystem permits Chroma SQLite writes):

```bash
# Windows           macOS/Linux
py setup.py         python3 setup.py
```

Then register the MCP server with the `claude mcp add ...` command `setup.py`
prints, and restart Claude Code. You can search immediately, without waiting for
the restart, via the CLI:

```bash
.venv/Scripts/python.exe qlik_search.py "incremental reload upsert" --domain advanced   # Windows
./.venv/bin/python      qlik_search.py "incremental reload upsert" --domain advanced     # macOS/Linux
./.venv/bin/python      qlik_search.py --domains                                         # list filters
```

The default Chroma index path is the user cache directory
(`%LOCALAPPDATA%\qlik-ai-skill\index` on Windows, or `$XDG_CACHE_HOME` on
Unix-like systems when set). Set `QLIK_INDEX_DIR` or pass `--outdir` to use a
custom index directory.

If Chroma cannot write to the available filesystem, `setup.py` exits
successfully in fallback mode. CLI and MCP search still work through the bundled
`chunks.jsonl` lexical fallback, and `build_index.py` can be rerun later with a
writable `--outdir`.

The sections below cover the same steps manually, plus the pgvector team backend.

## Which backend?

- **chroma** (default) — persists a `chroma_db/` folder in the user cache by
  default, or in the directory supplied by `QLIK_INDEX_DIR`/`--outdir`. No database, no
  server beyond the MCP server itself. Embeds locally with the bundled model.
  **Recommended for Claude Code on individual machines.**
- **pgvector** — stores chunks and embeddings in PostgreSQL with the `pgvector`
  extension, for a whole team sharing one centrally hosted index. Embeds locally
  with the same MiniLM model (via `sentence-transformers`), so still no API key.

## Setup

Use an isolated virtual environment so these dependencies do not collide with
other Python projects. The MCP server must later be launched with *this venv's*
Python interpreter, so note its path.

### 1. Install dependencies

```bash
# Windows (the "py" launcher ships with python.org installs)
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# macOS/Linux
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

For the pgvector backend, also uncomment its lines in `requirements.txt` before
installing (adds `sentence-transformers`, `psycopg[binary]`, `pgvector`).

Verified working on Python 3.14 with `chromadb` 1.5.x and `mcp` 1.28.x. Python
3.10+ is fine. Substitute `.\.venv\Scripts\python.exe` (Windows) or
`./.venv/bin/python` (macOS/Linux) for `python` in every command below.

### 2. Build the index

```bash
# Regenerate chunks — only needed if you edited files in ../references/
python build_chunks.py ../references chunks.jsonl

# Chroma backend (default) — writes to the user cache unless --outdir is supplied
python build_index.py --backend chroma

# OR pgvector backend
export DATABASE_URL="postgresql://user:pass@host:5432/qlik"
python build_index.py --backend pgvector
```

First run downloads the embedding model once (~90MB), then works offline.
`build_index.py` prints the collection count (498 with the shipped corpus) when done.

### 3. Register the MCP server

**Claude Code (recommended).** Register at user scope so it is available in every
project and is not committed to any repo. Point the command at the **venv** Python
(a bare `python3`/`python` will not have the dependencies):

```bash
claude mcp add qlik-knowledge --scope user \
  --env QLIK_BACKEND=chroma \
  --env QLIK_INDEX_DIR="/absolute/path/to/index" \
  -- "/absolute/path/to/tool/.venv/bin/python" "/absolute/path/to/tool/qlik_mcp_server.py"
```

On Windows the interpreter path is `...\tool\.venv\Scripts\python.exe`. Verify with
`claude mcp get qlik-knowledge` — it should report **✔ Connected**.

**Other MCP hosts (or manual config).** Add an equivalent stdio entry to your host's
MCP config (`~/.claude.json`, a project `.mcp.json`, or your host's equivalent),
again using the venv Python:

```json
{
  "mcpServers": {
    "qlik-knowledge": {
      "command": "/absolute/path/to/tool/.venv/bin/python",
      "args": ["/absolute/path/to/tool/qlik_mcp_server.py"],
      "env": {
        "QLIK_BACKEND": "chroma",
        "QLIK_INDEX_DIR": "/absolute/path/to/index"
      }
    }
  }
}
```

For pgvector, set `"QLIK_BACKEND": "pgvector"` and `"DATABASE_URL": "..."` instead
of `QLIK_INDEX_DIR`. No API key in either case.

Restart Claude Code (MCP tools load at startup). The tools `qlik_knowledge_search`
and `qlik_knowledge_domains` then appear, and SKILL.md instructs Claude to prefer
them over reading whole files.

## Maintenance

After editing any file in `../references/`, rerun both commands in step 2. Chunk IDs
derive from headings, so stable headings mean stable IDs.

## How it stays cheap

- 498 chunks, median ~98 tokens each.
- A typical search returns 5 chunks ≈ 500–1,500 tokens.
- The old monolithic `functions_reference.md` was ~14k tokens per load. The tool
  replaces that with a targeted lookup — roughly a 90% reduction per query — and
  the embedding cost is zero because it all runs locally.
