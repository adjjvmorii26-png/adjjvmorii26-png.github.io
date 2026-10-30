#!/usr/bin/env python3
"""Check relative href/src targets in the site's HTML actually exist.

Pages mirrored by scripts/snapshot-live-pages.sh are verbatim copies of the live
site and are skipped by default (pass --include-snapshot to audit them too, which
reports pre-existing breakage that was never caused by this repository).

Exit code 0 = clean, 1 = broken references found.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

REF = re.compile(r'(?:href|src)="([^"#?]+)"')
SKIP = re.compile(r"^(https?:|mailto:|data:|//)")
EXT = re.compile(r"\.(html|css|js|png|jpe?g|svg|webp|ico|json|txt|woff2?)$")


def snapshot_names(root: Path) -> set[str]:
    manifest = root / "ixpansion" / "LIVE-SNAPSHOT.sha256"
    if not manifest.is_file():
        return set()
    return {
        line.split(maxsplit=1)[1].strip()
        for line in manifest.read_text().splitlines()
        if line.strip()
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="site root (default: .)")
    ap.add_argument("--include-snapshot", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    mirrored = (
        set() if args.include_snapshot
        else {f"ixpansion/{name}" for name in snapshot_names(root)}
    )

    broken: dict[Path, list[str]] = defaultdict(list)
    scanned = 0
    for page in sorted(root.rglob("*.html")):
        if ".git" in page.parts or ".cline-home" in page.parts:
            continue
        rel = page.relative_to(root).as_posix()
        if rel in mirrored:
            continue
        scanned += 1
        text = page.read_text(errors="ignore")
        # Commented-out references are not fetched by the browser; ignore them.
        text = re.sub(r"<!--(?:(?!-->).)*-->", "", text, flags=re.S)
        for match in REF.finditer(text):
            target = match.group(1)
            if SKIP.match(target) or not EXT.search(target):
                continue
            # Root-absolute paths resolve against the repository root, which is
            # the site root for this user-pages repo. They are NOT relative to
            # the page, and silently 404 when the file is absent.
            base = root if target.startswith("/") else page.parent
            if not (base / target.lstrip("/")).exists():
                broken[page].append(target)

    for page, refs in sorted(broken.items()):
        print(f"{page.relative_to(root)}")
        for ref in sorted(set(refs)):
            print(f"  missing: {ref}")
    print(f"\nscanned {scanned} page(s); {len(broken)} with broken relative refs")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
