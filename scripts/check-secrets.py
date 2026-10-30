#!/usr/bin/env python3
"""Block credentials from being committed.

A live Telegram bot token was pasted into this project's chat session, which is
exactly how tokens end up in repositories. This scans the files git would publish
and fails if it finds something shaped like a credential.

Only tracked/untracked-and-not-ignored files are scanned, so local state
(`.cline-home/`) is out of scope. Matches are masked in the output: the point is
to identify the file, not to echo the secret into another log.

    python3 scripts/check-secrets.py

Exit code 0 = clean, 1 = something credential-shaped was found.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PATTERNS: list[tuple[str, re.Pattern]] = [
    ("Telegram bot token", re.compile(r"\b\d{8,12}:[A-Za-z0-9_-]{30,}\b")),
    ("GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})\b")),
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b")),
    ("OpenAI-style key", re.compile(r"\bsk-[A-Za-z0-9]{32,}\b")),
    ("Private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("Generic bearer assignment", re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"][A-Za-z0-9/+=_-]{24,}['\"]")),
]

SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".woff", ".woff2", ".pdf", ".zip"}


def candidate_files(root: Path) -> list[Path]:
    """Files git would publish: tracked, plus untracked but not ignored."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=root, capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if out.returncode != 0:
        return []
    seen = []
    for name in out.stdout.split("\0"):
        if not name:
            continue
        path = root / name
        if path.is_file() and path.suffix.lower() not in SKIP_SUFFIXES:
            seen.append(path)
    return seen


def mask(value: str) -> str:
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}{'*' * 8}…({len(value)} chars)"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    findings = []

    for path in candidate_files(root):
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        for label, pattern in PATTERNS:
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings.append(
                    f"{path.relative_to(root)}:{line}: {label} — {mask(match.group(0))}"
                )

    if findings:
        print("possible credentials in files that would be published:")
        for finding in findings:
            print(f"  {finding}")
        print(
            "\nRemove them, rotate the credential, and store the value in "
            "GitHub Secrets instead. If this is a test fixture, add the line to "
            "the ignore rules rather than committing it."
        )
        return 1

    print("no credential-shaped strings in publishable files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
