# Audit correction — 2026-10-30

Reconciliation of the "system scan and audit" report against the actual substrate.
The report's verdict was **"All active routes, security assertions, and runtime
configurations match defined system invariants. No state drift."** That verdict is
not supported. This file records what was checked, how, and what was found.

Scope of this checkout: `adjjvmorii26-png/adjjvmorii26-png.github.io` @ `master`
(12 files ever tracked). Claims about the `ixpansion` repository were checked
against that repo separately via the GitHub API. External HTTP was probed live;
those results are strong evidence but pass through a proxy, so treat them as
observations rather than forensic proof.

## Contradicted

| Claim | Observation | Evidence |
|---|---|---|
| Vercel `/api/edge` "receiving gossip, forge, and time vector feeds returning heartbeat chords" (status STABLE) | Every route 404s: `/`, `/health`, `/cons`, `/confluence`, `/api/edge`, `/forge`, `/gossip`. `/api/edge` returns Vercel's own `NOT_FOUND` JSON. | `curl -s -o /dev/null -w '%{http_code}' https://ixpansion-live.vercel.app/health` → `404` |
| `alexalex.info` hosts a live apex landing site, with isolated `mesh.` / `api.` records | No DNS at all. | `socket.gethostbyname_ex('alexalex.info')` → `gaierror: No address associated with hostname`; `mesh.`/`api.` → `Name or service not known` |
| "No state drift … across local or remote telemetry channels" | Live `/ixpansion/` served a *different* dashboard than `master`, linking to `648-ambient-sensor.html` … `667-mycelial-network.html` — pages that have **never existed** in this repo's history — while all six committed organ pages returned 404 live. Root `index.html` was byte-identical to live. | `git log --all --diff-filter=A --name-only`; `curl` status per page |
| FreeDNS updater "integrated directly into `server.py` bootstrap runtime path" | No `server.py` in `ixpansion` (root or anywhere). Repo code search: `FreeDNS` = 0, `freedns` = 0. Control queries prove search works: `api_server` = 28, `HMAC` = 11. | `gh api 'search/code?q=FreeDNS+repo:adjjvmorii26-png/ixpansion'` |
| Workspace assets: SVG glyph generator, Transformer backprop stubs, `.ics` Chronos parser | `transformer` 0, `backprop` 0, `chronos` 0, `glyph` 0 across all HTML and the whole 12-file history. | `grep -rioE` over tracked files |
| "41+ modules" | Internally inconsistent: this site hardcodes 744, the repo's `api/index.py` says 352, `ixpansion` actually contains 1254 `api/*.py` (2854 `.py` total). | `grep -cE '^api/[^/]+\.py$'` on the repo tree |

## Corroborated

- Identity and sibling repos exist: `ixpansion`, `pan-copilot`, `PlayGround`,
  `solid-organism`, `nexus-observatory`, and ~20 others.
- `ixpansion` is genuinely substantial: 4564 tracked paths, `vercel.json` routing
  `^/health$` → `/api/index.py`, a documented WSGI dispatcher, `Dockerfile`,
  `.devcontainer`, `SECURITY.md`, `aegis/`, 11 `HMAC` references.
- The Pages site itself serves 200 at `/` with `https_enforced: true`.

## Not verifiable from here

macOS/Unix runtime, port 4000 sandboxing, 3000–9090 port sweeps, and the four
`user:*` skills. Nothing observed attests to them; that is absence of evidence,
not evidence of absence.

## Diagnosis

1. **Vercel project is unlinked or failing to build.** Route config and
   `api/index.py` are intact in git, so this is deployment state, not code.
2. **Pages publishes a tree that does not match `master`.** Live contained 206
   pages absent from git; git contained 6 pages absent from live. Root page
   matched exactly, so the drift is confined to `ixpansion/`.

## Actions taken in this branch

- **Archived the live-only content before anything could overwrite it.**
  `scripts/snapshot-live-pages.sh` mirrors the 206 referenced pages into
  `ixpansion/`, with `ixpansion/LIVE-SNAPSHOT.sha256` for integrity. The live
  dashboard is preserved as `ixpansion/dashboard-live.html`.
- **Fixed the module-count contradiction** in `index.html`: one `FALLBACK`
  constant, `r.ok` guard, `no-store`, numeric validation, and a single animation
  pass. Previously two competing routines meant the animation timer overwrote the
  live value on every tick.
- **Surfaced API health in the UI** (`#api-status`) so a dead origin is visible
  instead of silently displaying stale figures.
- **Removed 9 dead dashboard links** (`census`, `connections`,
  `consciousness-field`, `consciousness-stream`, `constitution`,
  `entropy-weather`, `lucid-experiments`, `lucid-prototype`, `lucid_game`) —
  these 404 live *and* are absent from git. Rendered as inert "Not yet shipped"
  cards rather than 404s.
- **Added `scripts/check-links.py`** — authored pages are clean. With
  `--include-snapshot` all 215 pages are now clean (see below).

## Second pass — remaining defects found and fixed

- **`portal.html` was entirely dead.** It used 36 root-absolute links
  (`/room`, `/census`, …) which, in a user-pages repo, resolve to the domain root
  where nothing exists. Rewrote 26 to real targets (including 10 unambiguous
  aliases: `/room` → `room-bridge.html`, `/census` → `organism_census.html`,
  `/genome` → `genome-map.html`, `/soul` → `module-soul.html`, `/timeline` →
  `wave-timeline.html`, `/waves364-367` → `waves364_367.html`, and similar).
  10 targets exist nowhere and are now inert cards. Its "Command Center" card
  pointed at a missing `organism.html`; `organism_hq.html` is titled
  *"IXPANSION Organism HQ"*, so that link was repointed. "Entropy Weather" has no
  counterpart (only the unrelated `entropy-heatmap.html`) and was made inert.
- **57 dead tag references across 52 archived pages removed.** `/shared.js` (48
  references), `/_vercel/insights` and `/speed-insights` analytics, and a pyvis
  `lib/bindings/utils.js`. Every one of these 404s on the live site too, so no
  page has ever executed them — removing them cannot change behaviour, it only
  stops shipping 404 requests. The archive is therefore *content-faithful*, not
  byte-verbatim; `LIVE-SNAPSHOT.sha256` was regenerated to match.
- **The link checker was hiding this whole class of bug.** It skipped
  root-absolute paths and scanned HTML comments. It now resolves `/x` against the
  repository root (correct for a user-pages site) and ignores commented-out
  references. This is what surfaced `portal.html` and the 48 `/shared.js` hits.
- **CI gate prepared but not applied.** The intended change is two lines in
  `.github/workflows/deploy.yml`:

  ```yaml
      - name: Check internal links
        run: python3 scripts/check-links.py
  ```

  It could not be pushed: the GitHub App credential is not permitted to create or
  update files under `.github/workflows/`. Add it manually, or grant the app
  `workflows` permission. The checker itself is committed and passes today.
- **`README.md.bak` replaced with a real `README.md`** documenting the layout, the
  archive, and the known Vercel outage.
- **Structural HTML defects found and fixed.** `garden_live.html` concatenates two
  pyvis exports: both graphs built into the *same* `#mynetwork` container, so the
  second canvas stacked onto the first and the second card stayed empty. The
  second graph now has its own container (`#mynetwork-2`) and its script uses it.
  `genealogy.html` was a false positive — its `<defs>` is replaced via
  `innerHTML`, so only one exists at runtime.
- **`scripts/check-html.py`** now flags duplicate ids and dead `#anchors`, with
  script/style bodies stripped so ids inside JS strings are not miscounted.
  Authored pages: clean. `--include-snapshot` reports one deliberate exception
  (below).

## Known archive defect, left alone on purpose

`ixpansion/communion.html` is five separate mini-apps concatenated into one file
(5 `<html>`, 5 `<body>`, 5 `<script>`). Its ids collide — 3 references to
`#statsContainer` for 2 elements, 4 to `#total` for 3 — so each pane's script
updates whichever element matched first. Every one of those scripts also calls
root-absolute `/api/...` endpoints that do not exist on GitHub Pages.

Splitting and re-wiring it would mean inventing behaviour for archived code that
cannot run here anyway. It is recorded instead: `check-html.py --include-snapshot`
reports exactly this one page, by design.
- **Figures centralised.** `data/figures.json` holds every number the site quotes
  (with provenance and a `verified` flag), and `scripts/check-claims.py` fails
  when the HTML disagrees — including a "Showing N of M" invariant that checks the
  repo grid really renders N cards. Verified by injecting drift into a copy:
  `modules=999`, `repos stat=31`, `version=v9.9.9` were each caught with
  file:line, and `--github` caught a repo count that disagreed with the API.
  This closes the failure mode behind the 41+/352/744/1254 discrepancy.
- **Two markup defects repaired** in archived pages: `portal.html` had an
  unescaped `?module=<name>` placeholder in body text (browsers consume `<name>`
  as a tag, so the word silently vanished); `lucid-3d.html` never closed the
  `<span>` holding `#undText`, so every subsequent HUD row nested inside it and
  inherited that element's styling. All 215 pages now parse with balanced tags.

## Not done deliberately

- **No Pages rebuild was triggered.** A rebuild would replace the live tree; the
  snapshot above was taken first so nothing is lost, but publishing is a
  production action left to the owner.
- **No Vercel changes.** The project must be re-linked or its build inspected in
  the Vercel dashboard; nothing in this repo can do that.

## Verification performed

- Hydration logic executed under Node against four stubbed API states: live
  payload → `999/500` "API live"; 404 → `744/470` "API offline — cached figures";
  network throw → same fallback; junk payload → fallback with "figures cached".
  All four pass.
- `scripts/check-links.py` on authored pages: `scanned 9 page(s); 0 with broken
  relative refs`, exit 0. With `--include-snapshot`: `scanned 215 page(s); 0 with
  broken relative refs`, exit 0.
- `sha256sum -c LIVE-SNAPSHOT.sha256` — 206/206 OK after the archive repairs.
- `portal.html` and both edited dashboards parse with balanced tags (verified with
  Python's `html.parser`).
- `.github/workflows/deploy.yml` parses as valid YAML after adding the link gate.
