#!/usr/bin/env python3
"""Catch structural HTML defects that browsers silently absorb.

Currently checked:
  - duplicate id attributes in one document (`getElementById` returns only the
    first, so later elements quietly stop working)
  - in-page links (`href="#x"`) with no matching element

Script and style bodies are stripped before scanning: an id inside a JavaScript
string is not an element, and counting it produced false positives (e.g. a page
that rebuilds its <defs> via innerHTML).

Archived mirror pages are skipped by default; pass --include-snapshot to audit
them too.

    python3 scripts/check-html.py [--include-snapshot]

Exit code 0 = clean, 1 = defects found.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

ID_ATTR = re.compile(r'\bid="([^"]+)"')
ANCHOR = re.compile(r'href="#([^"]+)"')
SCRIPT_OR_STYLE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.S | re.I)


def mirrored(root: Path) -> set[str]:
    manifest = root / "ixpansion" / "LIVE-SNAPSHOT.sha256"
    if not manifest.is_file():
        return set()
    return {
        f"ixpansion/{line.split(maxsplit=1)[1].strip()}"
        for line in manifest.read_text().splitlines()
        if line.strip()
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--include-snapshot", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    skip = set() if args.include_snapshot else mirrored(root)

    problems: list[str] = []
    scanned = 0
    for page in sorted(root.rglob("*.html")):
        if ".git" in page.parts or ".cline-home" in page.parts:
            continue
        rel = page.relative_to(root).as_posix()
        if rel in skip:
            continue
        scanned += 1

        raw = page.read_text(errors="ignore")
        markup = SCRIPT_OR_STYLE.sub("", raw)

        ids = ID_ATTR.findall(markup)
        for value, count in Counter(ids).items():
            if count > 1:
                problems.append(f"{rel}: duplicate id '{value}' ({count} times)")

        known = set(ids)
        for anchor in sorted(set(ANCHOR.findall(markup))):
            if anchor and anchor not in known:
                problems.append(f"{rel}: href=\"#{anchor}\" has no matching id")

    if problems:
        print("html defects:")
        for problem in problems:
            print(f"  {problem}")
        print(f"\n{len(problems)} problem(s) across {scanned} page(s)")
        return 1

    print(f"{scanned} page(s): no duplicate ids, no dead anchors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
