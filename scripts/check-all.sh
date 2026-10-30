#!/usr/bin/env bash
# Run every consistency check this repository has. Exits non-zero on the first
# failing check so it can be used as a pre-push hook or a CI step.
set -uo pipefail

cd "$(dirname "$0")/.." || exit 1

fail=0
run() {
  local label="$1"; shift
  printf '== %s\n' "$label"
  if "$@"; then
    printf '   ok\n'
  else
    printf '   FAILED\n'
    fail=1
  fi
}

run "internal links (authored pages)" python3 scripts/check-links.py
run "internal links (incl. archive)" python3 scripts/check-links.py --include-snapshot
run "figure claims" python3 scripts/check-claims.py
run "no credentials in publishable files" python3 scripts/check-secrets.py

printf '== archive checksums\n'
if (cd ixpansion && sha256sum -c LIVE-SNAPSHOT.sha256 --quiet); then
  printf '   ok\n'
else
  printf '   FAILED\n'
  fail=1
fi

printf '== html tag balance\n'
if python3 - <<'PY'
import pathlib, sys
from html.parser import HTMLParser

VOID = {"meta", "link", "br", "img", "hr", "input", "source", "area", "base",
        "col", "embed", "track", "wbr"}


class Balance(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            self.errors.append(tag)


bad = []
for page in sorted(pathlib.Path(".").rglob("*.html")):
    if ".git" in page.parts:
        continue
    parser = Balance()
    parser.feed(page.read_text(errors="ignore"))
    parser.close()
    if parser.stack or parser.errors:
        bad.append(str(page))

print("   unbalanced: " + (", ".join(bad) if bad else "none"))
sys.exit(1 if bad else 0)
PY
then
  :
else
  fail=1
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "all checks passed"
else
  echo "one or more checks failed"
fi
exit "$fail"
