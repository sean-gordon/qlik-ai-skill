#!/usr/bin/env python3
"""
qlik_mcp_server.py — MCP server exposing Qlik knowledge retrieval to Claude.

Embeddings are LOCAL and FREE (Chroma's bundled model). No API key, no network.
The actual search lives in qlik_index.py and is shared with the CLI
(qlik_search.py), so MCP and shell retrieval behave identically.

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
  python qlik_mcp_server.py

Register in Claude Code (~/.claude.json via `claude mcp add`, or a project
.mcp.json) using the tool's venv Python — see tool/README.md. No key needed.
"""

from mcp.server.fastmcp import FastMCP

import qlik_index

mcp = FastMCP("qlik-knowledge")


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
    dom = domain.strip() or None
    try:
        hits = qlik_index.search(query, top_k=top_k, domain=dom)
    except qlik_index.ToolNotReady as e:
        return (f"Retrieval index not ready: {e}\n"
                "Run setup.py in the tool/ folder to install dependencies and build the index.")
    return qlik_index.format_hits(query, hits, domain=dom)


@mcp.tool()
def qlik_knowledge_domains() -> str:
    """List the available domain filters and what each covers, to help target a search."""
    lines = ["Available domains for qlik_knowledge_search:"]
    for name, desc in qlik_index.DOMAINS.items():
        lines.append(f"- {name}: {desc}")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
