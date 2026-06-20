#!/usr/bin/env python3
"""
setup.py — One-command bootstrap for the Qlik retrieval tool.

Run with any Python 3.10+ (it only uses the standard library to bootstrap):
  Windows:      py tool\\setup.py
  macOS/Linux:  python3 tool/setup.py

It will, idempotently:
  1. Create a virtual environment at tool/.venv (if absent).
  2. Install tool/requirements.txt into that venv.
  3. Build the Chroma index (downloads a ~90MB embedding model once, then offline).
It is safe to re-run; existing steps are skipped or refreshed.

When done it prints the venv Python path and the exact `claude mcp add` command
to register the MCP server (optional — the CLI qlik_search.py already works
without it). No API key is ever required.
"""

import os
import subprocess
import sys
import venv
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENV = HERE / ".venv"


def venv_python(v: Path) -> Path:
    if os.name == "nt":
        return v / "Scripts" / "python.exe"
    return v / "bin" / "python"


def run(cmd, **kw):
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, check=True, **kw)


def main():
    print(f"Qlik retrieval tool setup — {HERE}")

    # 1. venv
    py = venv_python(VENV)
    if py.exists():
        print(f"[1/3] venv exists: {VENV}")
    else:
        print(f"[1/3] creating venv: {VENV}")
        venv.create(str(VENV), with_pip=True)
    if not py.exists():
        sys.exit(f"ERROR: venv python not found at {py}")

    # 2. dependencies
    print("[2/3] installing dependencies (chromadb + mcp) ...")
    run([str(py), "-m", "pip", "install", "--upgrade", "pip", "--quiet"])
    run([str(py), "-m", "pip", "install", "-r", str(HERE / "requirements.txt"), "--quiet"])

    # 3. index — regenerate chunks if missing, then build
    chunks = HERE / "chunks.jsonl"
    if not chunks.exists():
        print("[3/3] chunks.jsonl missing — regenerating from ../references ...")
        run([str(py), str(HERE / "build_chunks.py"), str(HERE.parent / "references"), str(chunks)])
    print("[3/3] building Chroma index (first run downloads ~90MB model) ...")
    run([str(py), str(HERE / "build_index.py"), "--backend", "chroma"], cwd=str(HERE))

    # Done — print next steps
    idx = str(HERE)
    server = str(HERE / "qlik_mcp_server.py")
    print("\n" + "=" * 70)
    print("DONE. The retrieval tool is built and ready.")
    print("=" * 70)
    print(f"\nVenv Python : {py}")
    print(f"Search CLI  : \"{py}\" \"{HERE / 'qlik_search.py'}\" \"your query\"")
    print("\nOptional — register the MCP server with Claude Code (then restart it):")
    print(f'  claude mcp add qlik-knowledge --scope user \\\n'
          f'    --env QLIK_BACKEND=chroma \\\n'
          f'    --env "QLIK_INDEX_DIR={idx}" \\\n'
          f'    -- "{py}" "{server}"')
    print("\nVerify: claude mcp get qlik-knowledge   (should report Connected)")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(f"\nSetup failed at: {' '.join(str(c) for c in e.cmd)}\n(exit {e.returncode})")
