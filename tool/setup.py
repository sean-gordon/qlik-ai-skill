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


def run_shell(cmd, **kw):
    line = subprocess.list2cmdline([str(c) for c in cmd])
    print(f"  $ {line}")
    subprocess.run(line, check=True, shell=True, **kw)


def run_shell_captured(cmd, **kw):
    line = subprocess.list2cmdline([str(c) for c in cmd])
    print(f"  $ {line}")
    return subprocess.run(line, check=True, shell=True, capture_output=True, text=True, **kw)


def run_index_build(py: Path, idx: str) -> str:
    target = Path(idx)
    outdir_arg = str(target)
    if not is_writable_index_path(target):
        target = workspace_index_path()
        print(f"  default index path is not writable; using workspace-local path: {target}")
        outdir_arg = str(Path("tool") / target.name)
    try:
        res = run_shell_captured([
            str(py),
            str(HERE / "build_index.py"),
            "--backend", "chroma",
            "--chunks", str(Path("tool") / "chunks.jsonl"),
            "--outdir", outdir_arg,
        ], cwd=str(HERE.parent))
        if res.stdout:
            print(res.stdout.rstrip())
        return str(target)
    except subprocess.CalledProcessError:
        print("  Chroma index build failed; the bundled chunks.jsonl fallback remains usable.")
        return ""


def workspace_index_path() -> Path:
    for i in range(1, 1000):
        candidate = HERE / f"index_workspace_{i}"
        if not candidate.exists():
            return candidate
    return HERE / ".index"


def is_writable_index_path(path: Path) -> bool:
    try:
        if (path / "chroma_db").exists():
            return False
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write-test"
        probe.write_text("ok", encoding="utf-8")
        return True
    except OSError:
        return False


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
    print("[2/3] checking dependencies ...")
    deps_ok = False
    try:
        res = subprocess.run([str(py), "-c", "import chromadb, mcp"], capture_output=True, text=True)
        if res.returncode == 0:
            deps_ok = True
            print("  dependencies already installed and importable.")
    except Exception:
        pass

    if not deps_ok:
        print("  dependencies missing or incomplete; installing/upgrading ...")
        run([str(py), "-m", "pip", "install", "--upgrade", "pip"])
        run([str(py), "-m", "pip", "install", "-r", str(HERE / "requirements.txt")])

    # 3. index — regenerate chunks if missing, then build
    chunks = HERE / "chunks.jsonl"
    if not chunks.exists():
        print("[3/3] chunks.jsonl missing — regenerating from ../references ...")
        run([str(py), str(HERE / "build_chunks.py"), str(HERE.parent / "references"), str(chunks)])
    print("[3/3] building Chroma index (first run downloads ~90MB model) ...")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(HERE)
    idx = subprocess.check_output(
        [str(py), "-c", "import qlik_index; print(qlik_index.default_index_dir())"],
        cwd=str(HERE),
        env=env,
        text=True,
    ).strip()
    idx = run_index_build(py, idx)

    # Done — print next steps
    server = str(HERE / "qlik_mcp_server.py")
    print("\n" + "=" * 70)
    print("DONE. The retrieval tool is ready.")
    print("=" * 70)
    print(f"\nVenv Python : {py}")
    print(f"Search CLI  : \"{py}\" \"{HERE / 'qlik_search.py'}\" \"your query\"")
    print("\nOptional — register the MCP server with Claude Code (then restart it):")
    if idx:
        print(f'  claude mcp add qlik-knowledge --scope user \\\n'
              f'    --env QLIK_BACKEND=chroma \\\n'
              f'    --env "QLIK_INDEX_DIR={idx}" \\\n'
              f'    -- "{py}" "{server}"')
    else:
        print("  Chroma index build was blocked in this environment.")
        print("  CLI and MCP search still work through the bundled chunks.jsonl fallback.")
        print(f'  claude mcp add qlik-knowledge --scope user \\\n'
              f'    --env QLIK_BACKEND=chroma \\\n'
              f'    -- "{py}" "{server}"')
    print("\nVerify: claude mcp get qlik-knowledge   (should report Connected)")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(f"\nSetup failed at: {' '.join(str(c) for c in e.cmd)}\n(exit {e.returncode})")
