#!/usr/bin/env python3
"""
qlik_search.py — Command-line Qlik knowledge retrieval.

Same engine as the MCP tool, but callable directly from a shell. This is what
the skill uses when the MCP server is not yet loaded into the current session
(MCP tools only attach at startup), so retrieval still works on first run with
no restart.

Usage:
  python qlik_search.py "incremental reload upsert pattern"
  python qlik_search.py "Sum with TOTAL qualifier" --domain frontend --top-k 5
  python qlik_search.py --domains          # list domain filters

Exit codes:
  0  results printed
  3  tool not ready (deps or index missing) — caller should run setup.py.
     The line "QLIK_TOOL_NOT_READY: <reason>" is printed so callers can detect it.

Run this with the tool's venv Python so chromadb is importable, e.g.
  Windows:      tool\\.venv\\Scripts\\python.exe qlik_search.py "..."
  macOS/Linux:  tool/.venv/bin/python qlik_search.py "..."
"""

import argparse
import sys

import qlik_index


def main():
    ap = argparse.ArgumentParser(description="Search the Qlik Sense knowledge corpus.")
    ap.add_argument("query", nargs="?", help="A specific question or concept.")
    ap.add_argument("--domain", default="", help="Optional domain filter (see --domains).")
    ap.add_argument("--top-k", type=int, default=5, help="Number of passages (1-10, default 5).")
    ap.add_argument("--domains", action="store_true", help="List available domain filters and exit.")
    args = ap.parse_args()

    if args.domains:
        print("Available domains for --domain:")
        for name, desc in qlik_index.DOMAINS.items():
            print(f"  {name:15s} {desc}")
        return 0

    if not args.query:
        ap.error("a query is required (or use --domains)")

    try:
        hits = qlik_index.search(args.query, top_k=args.top_k, domain=args.domain or None)
    except qlik_index.ToolNotReady as e:
        print(f"QLIK_TOOL_NOT_READY: {e}", file=sys.stderr)
        print("Run setup.py to install dependencies and build the index, then retry.",
              file=sys.stderr)
        return 3

    print(qlik_index.format_hits(args.query, hits, domain=args.domain or None))
    return 0


if __name__ == "__main__":
    sys.exit(main())
