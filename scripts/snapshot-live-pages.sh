#!/usr/bin/env bash
# snapshot-live-pages.sh — archive pages that exist on the live GitHub Pages site
# but are absent from this repository.
#
# Background: the deployed site at https://adjjvmorii26-png.github.io/ixpansion/
# serves a dashboard that links to module pages (648-ambient-sensor.html, ...)
# which have never been committed here. Rebuilding Pages from `master` would
# replace that tree, so we mirror the live content into git first.
#
# The snapshot is idempotent: existing files are skipped unless --force is given.
#
# Usage:
#   scripts/snapshot-live-pages.sh [--force] [base_url] [out_dir]
set -euo pipefail

FORCE=0
if [[ "${1:-}" == "--force" ]]; then FORCE=1; shift; fi

BASE="${1:-https://adjjvmorii26-png.github.io/ixpansion/}"
OUT="${2:-ixpansion}"
MANIFEST="${OUT}/LIVE-SNAPSHOT.sha256"
PARALLEL=4

command -v curl >/dev/null || { echo "curl is required" >&2; exit 1; }

mkdir -p "$OUT"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

echo "==> Fetching live index: ${BASE}"
curl -fsS -m 20 "$BASE" -o "$tmp/index.html"

# Relative targets only; skip off-site links.
grep -oE 'href="[^"]+"' "$tmp/index.html" \
  | sed 's/^href="//; s/"$//' \
  | grep -vE '^(https?:|#|mailto:)' \
  | sed 's/[?#].*$//' \
  | grep -E '\.html$' \
  | sort -u > "$tmp/links.txt"

total="$(wc -l < "$tmp/links.txt" | tr -d ' ')"
echo "==> ${total} relative page links found"

export BASE OUT FORCE
fetch_one() {
  local name="$1" dest
  dest="${OUT}/${name}"
  if [[ -s "$dest" && "${FORCE}" != "1" ]]; then return 0; fi
  mkdir -p "$(dirname "$dest")"
  if curl -fsS -m 20 "${BASE}${name}" -o "${dest}.part"; then
    mv "${dest}.part" "$dest"
  else
    rm -f "${dest}.part"
    echo "MISS  ${name}" >&2
  fi
}
export -f fetch_one

# Bounded parallelism keeps memory/network use predictable.
xargs -a "$tmp/links.txt" -I{} -P "$PARALLEL" bash -c 'fetch_one "$@"' _ {}

echo "==> Writing manifest ${MANIFEST}"
( cd "$OUT" && grep -E '\.html$' "$tmp/links.txt" | while read -r f; do
    [[ -f "$f" ]] && sha256sum "$f"
  done ) | sort -k2 > "$MANIFEST"

echo "==> Snapshot complete: $(wc -l < "$MANIFEST" | tr -d ' ') files checksummed"
