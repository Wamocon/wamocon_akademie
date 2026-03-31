#!/usr/bin/env python3
"""
Convert root-absolute links (/page123.html, /) to relative paths so the site works
when opened via file:// (double-click index.html) as well as via a local HTTP server.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def depth_prefix(file_path: Path) -> str:
    rel = file_path.relative_to(ROOT)
    n = len(rel.parent.parts)
    return "../" * n if n else ""


def transform(content: str, px: str) -> str:
    out = content

    # href="/pageNNNNNNNN.html" or with #anchor
    out = re.sub(
        r'href="/(page\d+\.html(?:#[^"\s<>]*)?)"',
        lambda m: f'href="{px}{m.group(1)}"',
        out,
    )
    out = re.sub(
        r"href='/(page\d+\.html(?:#[^'\s<>]*)?)'",
        lambda m: f"href='{px}{m.group(1)}'",
        out,
    )

    # Home: href="/"  → index.html in same relative tree
    out = re.sub(r'href="/"', f'href="{px}index.html"', out)

    # Rare: explicit /index.html
    out = re.sub(r'href="/index\.html"', f'href="{px}index.html"', out)

    # Meta refresh, canonical, og:url
    out = re.sub(r"url=/(page\d+\.html)", rf"url={px}\1", out)
    out = re.sub(
        r'(<link[^>]+rel="canonical"[^>]+href=")/(page\d+\.html)"',
        rf"\1{px}\2",
        out,
    )
    out = re.sub(
        r'(<meta[^>]+property="og:url"[^>]+content=")/(page\d+\.html)"',
        rf"\1{px}\2",
        out,
    )

    # window.location.replace("/page....html")
    out = re.sub(
        r'window\.location\.replace\("/(page\d+\.html)"\)',
        rf'window.location.replace("{px}\1")',
        out,
    )

    # data-success-url, data-field-formmsgurl-value, og:url content, etc.: ="/page....html"
    out = re.sub(r'="/(page\d+\.html)', rf'="{px}\1', out)
    out = re.sub(r"='/(page\d+\.html)", rf"='{px}\1", out)

    return out


def process_file(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8", errors="surrogateescape")
    px = depth_prefix(path)
    out = transform(raw, px)
    if out != raw:
        path.write_text(out, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = []
    for path in ROOT.rglob("*.html"):
        if "node_modules" in path.parts:
            continue
        try:
            if process_file(path):
                changed.append(str(path.relative_to(ROOT)))
        except OSError as e:
            print(f"skip {path}: {e}")
    print(f"Updated {len(changed)} file(s) for relative linking.")


if __name__ == "__main__":
    main()
