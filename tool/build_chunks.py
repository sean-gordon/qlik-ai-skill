#!/usr/bin/env python3
"""
build_chunks.py — Parse the Qlik reference markdown files into retrievable chunks.

Each chunk is a self-contained unit of knowledge anchored on a heading
(## or ### or ####). Chunks carry metadata (source file, heading path, topic
tags) so the retrieval tool can return precise, well-attributed context
instead of whole files.

Output: chunks.jsonl — one JSON object per line, ready for embedding.

This script has NO third-party dependencies. It is safe to run anywhere
Python 3.9+ is available.
"""

import json
import re
import sys
from pathlib import Path

# Heading levels we split on. We treat #### as the finest grain because the
# reference files use #### for individual functions (Sum, Count, makedate...).
SPLIT_LEVELS = (2, 3, 4)  # ##, ###, ####

# Sections that are navigation/boilerplate, not knowledge. Skipped.
SKIP_TITLES = {
    "table of contents",
    "companion references",
}

# Soft cap on chunk size in characters. Chunks larger than this are split
# on paragraph boundaries so no single chunk dominates a retrieval result.
MAX_CHARS = 1800


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def derive_tags(source: str, heading_path: list[str], body: str) -> list[str]:
    """Lightweight tagging so retrieval can boost by domain when needed."""
    tags = set()
    stem = source.replace(".md", "")
    # Domain tag from the source file. The v4.0 split produced many functions_*
    # and advanced_* files; they all roll up to the "functions"/"advanced"
    # domains advertised in SKILL.md and qlik_mcp_server.py. The explicit map
    # also covers the pre-split monolithic names for backward compatibility.
    explicit = {
        "scripting_knowledgebase": "backend",
        "expression_knowledgebase": "frontend",
        "functions_reference": "functions",
        "advanced_patterns": "advanced",
        "debugging_guide": "debugging",
        "visualization_guide": "visualisation",
        "komment_guide": "komment",
    }
    if stem in explicit:
        domain = explicit[stem]
    elif stem.startswith("functions_"):
        domain = "functions"
    elif stem.startswith("advanced_"):
        domain = "advanced"
    else:
        domain = stem
    tags.add(domain)
    hay = (" ".join(heading_path) + " " + body[:400]).lower()
    keyword_map = {
        "set analysis": "set-analysis",
        "aggr": "aggr",
        "section access": "section-access",
        "incremental": "incremental",
        "qvd": "qvd",
        "applymap": "applymap",
        "synthetic key": "data-model",
        "link table": "data-model",
        "preceding load": "preceding-load",
        "intervalmatch": "intervalmatch",
        "crosstable": "crosstable",
        "performance": "performance",
        "kpi": "kpi",
        "colour": "colour",
        "color": "colour",
    }
    for needle, tag in keyword_map.items():
        if needle in hay:
            tags.add(tag)
    return sorted(tags)


def split_long(body: str) -> list[str]:
    """Split an oversized body on blank lines, keeping code fences intact."""
    if len(body) <= MAX_CHARS:
        return [body]
    parts, current, in_fence = [], [], False
    for line in body.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        current.append(line)
        if not in_fence and sum(len(x) for x in current) >= MAX_CHARS and line.strip() == "":
            parts.append("".join(current).strip())
            current = []
    if current:
        parts.append("".join(current).strip())
    return [p for p in parts if p]


def parse_file(path: Path) -> list[dict]:
    source = path.name
    lines = path.read_text(encoding="utf-8").splitlines()
    chunks = []
    heading_stack: list[tuple[int, str]] = []  # (level, title)
    buf: list[str] = []

    def flush():
        if not heading_stack:
            return
        title = heading_stack[-1][1]
        if title.lower().strip() in SKIP_TITLES:
            buf.clear()
            return
        body = "\n".join(buf).strip()
        if not body:
            buf.clear()
            return
        heading_path = [t for _, t in heading_stack]
        for i, piece in enumerate(split_long(body)):
            cid = f"{source.replace('.md','')}::{slugify('-'.join(heading_path))}"
            if i:
                cid += f"::p{i}"
            chunks.append({
                "id": cid,
                "source": source,
                "heading_path": heading_path,
                "title": title,
                "tags": derive_tags(source, heading_path, piece),
                "text": f"{' > '.join(heading_path)}\n\n{piece}",
            })
        buf.clear()

    for line in lines:
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            if level in SPLIT_LEVELS:
                flush()
                while heading_stack and heading_stack[-1][0] >= level:
                    heading_stack.pop()
                heading_stack.append((level, title))
                continue
            elif level == 1:
                flush()
                heading_stack = [(1, title)]
                continue
        buf.append(line)
    flush()
    return chunks


def main():
    ref_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("../references")
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("chunks.jsonl")
    all_chunks = []
    for md in sorted(ref_dir.glob("*.md")):
        fc = parse_file(md)
        all_chunks.extend(fc)
        print(f"  {md.name}: {len(fc)} chunks")
    with out.open("w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    total_chars = sum(len(c["text"]) for c in all_chunks)
    print(f"\nTotal: {len(all_chunks)} chunks, ~{total_chars // 4} tokens across corpus")
    print(f"Median chunk: ~{sorted(len(c['text']) for c in all_chunks)[len(all_chunks)//2] // 4} tokens")
    print(f"Written to {out}")


if __name__ == "__main__":
    main()
