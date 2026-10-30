#!/usr/bin/env python3
"""Validate every skill under skills/.

A skill is a directory containing SKILL.md with YAML frontmatter:

    ---
    name: pdf-report
    description: Build a PDF report from tabular data. Use when ...
    ---

Checks enforced:
  - the directory name is a valid lowercase-hyphenated slug and matches `name`
  - `description` is present, 20-1024 chars, and says when to use the skill
  - the body is substantive (not just a heading)
  - relative markdown links inside the skill resolve to real files

    python3 scripts/check-skills.py

Exit code 0 = all skills valid, 1 = problems found.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.S)
REQUIRED_KEYS = ("name", "description")
MIN_BODY = 120
DESCRIPTION_BOUNDS = (20, 1024)


def parse(path: Path):
    text = path.read_text()
    match = FRONTMATTER.match(text)
    if not match:
        return None, None, text
    raw_front, body = match.group(1), match.group(2)
    fields: dict[str, str] = {}
    for line in raw_front.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            fields.setdefault("__malformed__", line)
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip("'\"")
    return fields, body, text


def check_skill(skill_dir: Path, root: Path) -> list[str]:
    problems = []
    rel = skill_dir.relative_to(root)
    skill_file = skill_dir / "SKILL.md"

    if not skill_file.is_file():
        return [f"{rel}: missing SKILL.md"]

    if not SLUG.match(skill_dir.name):
        problems.append(
            f"{rel}: directory name must be lowercase-hyphenated, e.g. 'pdf-report'"
        )

    fields, body, _ = parse(skill_file)
    if fields is None:
        return [f"{rel}/SKILL.md: missing or malformed '---' frontmatter block"]

    if "__malformed__" in fields:
        problems.append(f"{rel}/SKILL.md: frontmatter line without a key: {fields['__malformed__']!r}")

    for key in REQUIRED_KEYS:
        if not fields.get(key):
            problems.append(f"{rel}/SKILL.md: frontmatter is missing '{key}'")

    name = fields.get("name", "")
    if name and name != skill_dir.name:
        problems.append(
            f"{rel}/SKILL.md: name '{name}' does not match directory '{skill_dir.name}'"
        )

    description = fields.get("description", "")
    low, high = DESCRIPTION_BOUNDS
    if description and not low <= len(description) <= high:
        problems.append(
            f"{rel}/SKILL.md: description is {len(description)} chars, expected {low}-{high}"
        )
    if description and len(description) >= low and not re.search(
        r"\b(use when|use this|when the user|when you)\b", description, re.I
    ):
        problems.append(
            f"{rel}/SKILL.md: description never says when to use it "
            "(e.g. 'Use when ...') — that is what makes a skill discoverable"
        )

    if body is not None and len(body.strip()) < MIN_BODY:
        problems.append(
            f"{rel}/SKILL.md: body is only {len(body.strip())} chars; "
            f"a skill needs at least {MIN_BODY} of procedure"
        )

    for link in LINK.findall(body or ""):
        if link.startswith(("http://", "https://", "mailto:", "#", "/")):
            continue
        if not (skill_dir / link).exists():
            problems.append(f"{rel}/SKILL.md: broken relative link '{link}'")

    return problems


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    skills_root = root / "skills"

    if not skills_root.is_dir():
        print("no skills/ directory; nothing to validate")
        return 0

    skill_dirs = sorted(p for p in skills_root.iterdir() if p.is_dir() and not p.name.startswith("."))
    if not skill_dirs:
        print("skills/ exists but contains no skill directories")
        return 0

    problems: list[str] = []
    seen: dict[str, str] = {}
    for skill_dir in skill_dirs:
        problems += check_skill(skill_dir, root)
        name = skill_dir.name
        if name in seen:
            problems.append(f"duplicate skill name '{name}' ({seen[name]} and {skill_dir})")
        seen[name] = str(skill_dir.relative_to(root))

    if problems:
        print("skill validation failed:")
        for problem in problems:
            print(f"  {problem}")
        print(f"\n{len(problems)} problem(s) across {len(skill_dirs)} skill(s)")
        return 1

    print(f"{len(skill_dirs)} skill(s) valid: {', '.join(d.name for d in skill_dirs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
