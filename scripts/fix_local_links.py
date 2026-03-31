#!/usr/bin/env python3
"""
Rewrite Tilda-style /slug URLs to root page*.html files (see htaccess) so navigation
works with `python -m http.server` and similar static hosts without mod_rewrite.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Longest slugs first (e.g. en/... before en)
SLUG_TO_FILE: list[tuple[str, str]] = [
    ("bildungsprogramme-fr-softwaretester", "page54047195.html"),
    ("ber-die-akademie", "page54152991.html"),
    ("istqb-zertifizierung", "page54160721.html"),
    ("danke", "page53938027.html"),
    ("fehler", "page53938503.html"),
    ("ditele-app", "page54260389.html"),
    ("bewertungen", "page54001083.html"),
    ("360-booster-system", "page54263521.html"),
    ("footer", "page54297621.html"),
    ("kontakt", "page54299165.html"),
    ("impressum", "page54299421.html"),
    ("datenschutz", "page53937561.html"),
    ("en/educational-programs", "page55494043.html"),
    ("en/about-us", "page55498733.html"),
    ("en/istqb-certification", "page55500201.html"),
    ("en/ditele-app", "page55502413.html"),
    ("en/reviews", "page55503825.html"),
    ("en/360-booster-system", "page55504631.html"),
    ("en/contacts", "page55505933.html"),
    ("thanks", "page55507893.html"),
    ("privacy-policy", "page55508025.html"),
    ("imprint", "page55508603.html"),
    ("en", "page55490499.html"),
]

SLUG_TO_FILE.sort(key=lambda x: len(x[0]), reverse=True)


def replace_slug_occurrences(text: str, slug: str, fname: str) -> str:
    """
    Replace /slug (optional /, optional #anchor) when it is a full path segment,
    i.e. followed by quote, whitespace, tag end — not /more/segments.
    """
    pat = re.compile(
        r"/"
        + re.escape(slug)
        + r"(?:/|)(#[^\"\'\s<>]*)?(?=[\"\'\s<>]|$)"
    )

    def repl(m: re.Match) -> str:
        anchor = m.group(1) or ""
        return "/" + fname + anchor

    return pat.sub(repl, text)


def process_file(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8", errors="surrogateescape")
    out = raw
    for slug, fname in SLUG_TO_FILE:
        out = replace_slug_occurrences(out, slug, fname)
    out = re.sub(r"/Impressum\b", "/page54299421.html", out)
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
                changed.append(path.relative_to(ROOT))
        except OSError as e:
            print(f"skip {path}: {e}")
    print(f"Updated {len(changed)} file(s).")
    for p in changed[:50]:
        print(f"  {p}")
    if len(changed) > 50:
        print(f"  ... and {len(changed) - 50} more")


if __name__ == "__main__":
    main()
