#!/usr/bin/env python3
"""Regenerate sitemap.xml for the authored pages.

Pages listed in ixpansion/LIVE-SNAPSHOT.sha256 are archived mirror copies of the
live site. They stay reachable but are excluded from the sitemap so they do not
compete with the landing page and dashboard in search results.

    python3 scripts/make-sitemap.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape

BASE = "https://adjjvmorii26-png.github.io"
EXCLUDE = {"404.html"}


def archived(root: Path) -> set[str]:
    manifest = root / "ixpansion" / "LIVE-SNAPSHOT.sha256"
    if not manifest.is_file():
        return set()
    return {
        f"ixpansion/{line.split(maxsplit=1)[1].strip()}"
        for line in manifest.read_text().splitlines()
        if line.strip()
    }


def last_commit_date(root: Path, rel: str) -> str:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ad", "--date=short", "--", rel],
            cwd=root, capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    skip = archived(root) | EXCLUDE

    pages = [
        p.relative_to(root).as_posix()
        for p in sorted(root.rglob("*.html"))
        if ".git" not in p.parts
        and ".cline-home" not in p.parts
        and p.relative_to(root).as_posix() not in skip
    ]

    if not pages:
        print("no pages found", file=sys.stderr)
        return 1

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for rel in pages:
        loc = f"{BASE}/" if rel == "index.html" else f"{BASE}/{quote(rel)}"
        modified = last_commit_date(root, rel)
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(loc)}</loc>")
        if modified:
            lines.append(f"    <lastmod>{modified}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")

    (root / "sitemap.xml").write_text("\n".join(lines) + "\n")
    print(f"wrote sitemap.xml with {len(pages)} url(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
