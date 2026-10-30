#!/usr/bin/env python3
"""Scaffold a new skill directory under skills/.

    python3 scripts/new-skill.py my-skill --description "What it does and when to use it."

Creates skills/<slug>/SKILL.md with valid frontmatter and refuses to overwrite an
existing skill. Run scripts/check-skills.py afterwards (or check-all.sh, which
includes it) to confirm the result is well-formed.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

TEMPLATE = """---
name: {slug}
description: {description}
---

# {title}

State what this skill is for in one or two sentences, then the procedure.

## When to use

- Trigger situations, phrased the way a user would ask.

## Procedure

1. First concrete step.
2. Second concrete step.
3. Verify the result and report what changed.

## Notes

- Constraints, failure modes, or things that must never be done.
"""


def title_from(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", help="lowercase-hyphenated skill name")
    ap.add_argument("--description", required=True,
                    help="one sentence: what it does and when to use it")
    args = ap.parse_args()

    if not SLUG.match(args.slug) or len(args.slug) > 64:
        print(f"invalid slug {args.slug!r}: use lowercase letters, digits, and single "
              "hyphens (max 64 chars), e.g. 'pdf-report'", file=sys.stderr)
        return 1

    description = " ".join(args.description.split())
    if not 20 <= len(description) <= 1024:
        print(f"description must be 20-1024 characters (got {len(description)})", file=sys.stderr)
        return 1

    root = Path(__file__).resolve().parents[1]
    target = root / "skills" / args.slug / "SKILL.md"
    if target.exists():
        print(f"{target.relative_to(root)} already exists; edit it instead", file=sys.stderr)
        return 1

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        TEMPLATE.format(
            slug=args.slug,
            description=description,
            title=title_from(args.slug),
        )
    )
    print(f"created {target.relative_to(root)}")
    print("next: fill in the procedure, then run python3 scripts/check-skills.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
