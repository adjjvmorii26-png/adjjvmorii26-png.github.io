#!/usr/bin/env python3
"""Fail when a number quoted in the HTML disagrees with data/figures.json.

This project's recurring failure is claims drifting from state: the landing page,
the dispatcher docstring, and an external audit have each quoted a different
module count. This checker gives the site one source of truth.

Each figure is matched only inside contexts where it is actually a claim (e.g.
"744 living modules", `modules:744`, the `Constellation Repos` stat), so unrelated
integers in the markup are not policed.

    python3 scripts/check-claims.py
    python3 scripts/check-claims.py --github    # also verify the repo count live

Exit code 0 = consistent, 1 = drift found.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# figure -> regexes whose first group is the claimed value
CLAIMS: dict[str, list[str]] = {
    "modules": [
        r"(\d+)\s+living modules",
        r"modules:(\d+)",
        r"Main organism — (\d+) modules",
        r"— (\d+) modules,",
    ],
    "waves": [
        r"wave:(\d+)",
        r'id="wave-num">(\d+)',
        r"WAVE\s+(\d+)",
        r"(\d+)\s+evolution waves",
    ],
    "repos": [
        r"(\d+)\s+repositories",
        r"(\d+)\s+[Cc]onstellation",
    ],
    "routes": [
        r"(\d+)\s+API [Rr]outes",
        r"routes:(\d+)",
    ],
}

# The label stat puts the number in a sibling element, so match it separately.
STAT_CLAIMS = {
    "repos": r'<div class="num">(\d+)</div><div class="label">Constellation Repos',
    "routes": r'<div class="num">(\d+)</div><div class="label">API Routes',
}

VERSION_CLAIM = re.compile(r"\bv\d+\.\d+\.\d+\b")


def load_figures(root: Path) -> dict:
    path = root / "data" / "figures.json"
    data = json.loads(path.read_text())
    return {name: spec["value"] for name, spec in data["figures"].items()}


def authored_pages(root: Path) -> list[Path]:
    manifest = root / "ixpansion" / "LIVE-SNAPSHOT.sha256"
    archived = set()
    if manifest.is_file():
        archived = {
            f"ixpansion/{line.split(maxsplit=1)[1].strip()}"
            for line in manifest.read_text().splitlines()
            if line.strip()
        }
    return [
        p for p in sorted(root.rglob("*.html"))
        if ".git" not in p.parts
        and ".cline-home" not in p.parts
        and p.relative_to(root).as_posix() not in archived
        and p.relative_to(root).as_posix() != "404.html"
    ]


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def check_pages(root: Path, figures: dict) -> list[str]:
    problems = []
    for page in authored_pages(root):
        text = page.read_text(errors="ignore")
        rel = page.relative_to(root)

        for figure, patterns in CLAIMS.items():
            expected = figures.get(figure)
            if expected is None:
                continue
            for pattern in patterns:
                for match in re.finditer(pattern, text):
                    raw = match.group(1)
                    if not raw.isdigit():
                        continue
                    if int(raw) != int(expected):
                        problems.append(
                            f"{rel}:{line_of(text, match.start())}: "
                            f"{figure} = {raw}, figures.json says {expected}"
                        )

        for figure, pattern in STAT_CLAIMS.items():
            expected = figures.get(figure)
            for match in re.finditer(pattern, text):
                if int(match.group(1)) != int(expected):
                    problems.append(
                        f"{rel}:{line_of(text, match.start())}: "
                        f"{figure} stat = {match.group(1)}, figures.json says {expected}"
                    )

        for match in VERSION_CLAIM.finditer(text):
            expected = figures.get("version")
            if expected and match.group(0) != expected:
                problems.append(
                    f"{rel}:{line_of(text, match.start())}: "
                    f"version = {match.group(0)}, figures.json says {expected}"
                )

        # "Showing N of M" must match both the cards actually rendered and the
        # canonical repo count.
        shown = re.search(r"Showing (\d+) of (\d+)", text)
        if shown:
            cards = len(re.findall(r'class="repo"', text))
            declared, total = int(shown.group(1)), int(shown.group(2))
            line = line_of(text, shown.start())
            if declared != cards:
                problems.append(
                    f"{rel}:{line}: says it shows {declared} repos but renders {cards} cards"
                )
            if figures.get("repos") is not None and total != int(figures["repos"]):
                problems.append(
                    f"{rel}:{line}: 'of {total}' disagrees with figures.json repos={figures['repos']}"
                )
    return problems


def check_github(figures: dict) -> list[str]:
    try:
        out = subprocess.run(
            ["gh", "api", "users/adjjvmorii26-png/repos?per_page=100", "--jq", "length"],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return [f"could not query GitHub for the repo count ({exc})"]
    if out.returncode != 0:
        return [f"gh api failed: {out.stderr.strip()[:120]}"]
    actual = out.stdout.strip()
    if actual.isdigit() and figures.get("repos") is not None and int(actual) != int(figures["repos"]):
        return [f"github: {actual} repos exist, figures.json says {figures['repos']}"]
    return []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="site root (default: .)")
    ap.add_argument("--github", action="store_true", help="also compare the repo count against the GitHub API")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    figures = load_figures(root)

    problems = check_pages(root, figures)
    if args.github:
        problems += check_github(figures)

    if problems:
        print("claim drift detected:")
        for problem in problems:
            print(f"  {problem}")
        print(f"\n{len(problems)} problem(s)")
        return 1

    checked = ", ".join(f"{k}={v}" for k, v in figures.items())
    print(f"claims consistent with data/figures.json ({checked})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
