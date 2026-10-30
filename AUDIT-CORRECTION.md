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
  dashboard is preserved verbatim as `ixpansion/dashboard-live.html`.
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
- **Added `scripts/check-links.py`** — authored pages are clean (0 broken refs
  over 9 pages). With `--include-snapshot`, 215 pages surface 2 pre-existing
  breakages inherited from the live site (`portal.html` → `entropy-weather.html`,
  `organism.html`; `garden_live.html` → `../node_modules/vis/*`, `lib/bindings/utils.js`).
  These were left untouched because snapshots are verbatim.

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
  relative refs`, exit 0.
