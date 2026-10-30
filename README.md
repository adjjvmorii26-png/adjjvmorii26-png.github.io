# adjjvmorii26-png.github.io

Landing site and dashboard for **IXPANSION** — served by GitHub Pages at
<https://adjjvmorii26-png.github.io/>.

## Layout

| Path | Purpose |
|---|---|
| `index.html` | Apex landing page. Hydrates module/wave figures from the organism API and shows API health. |
| `ixpansion/index.html` | Organism dashboard index (organs, helix experiments, constellation). |
| `ixpansion/*.html` | Individual organ pages plus ~206 archived module pages (see below). |
| `ixpansion/LIVE-SNAPSHOT.sha256` | Checksums for every archived page. |
| `scripts/snapshot-live-pages.sh` | Rebuilds the archive from the live site (idempotent). |
| `scripts/check-links.py` | Fails on broken internal links. Not yet wired into CI — see `AUDIT-CORRECTION.md`. |
| `scripts/check-claims.py` | Fails when a number in the HTML disagrees with `data/figures.json` (module/wave/repo/route counts, version, "Showing N of M"). |
| `data/figures.json` | The single source of truth for every figure the site quotes, with provenance and whether it is verified. |
| `scripts/make-icons.py` | Renders `assets/icon.svg` geometry to `favicon-32.png`, `apple-touch-icon.png`, `assets/og-card.png`. |
| `scripts/make-sitemap.py` | Regenerates `sitemap.xml` from authored pages (excludes the archive). |
| `robots.txt`, `sitemap.xml`, `404.html` | Crawler directives, indexable URL list, and the custom not-found page. |
| `AUDIT-CORRECTION.md` | What an external audit claimed versus what the substrate actually shows. |
| `PORTFOLIO.md` | Evaluation of all 24 repositories: licensing, backlog, CI, naming, hosted surfaces. |

## Archived pages

The live site once served a dashboard linking to 206 module pages that were never
committed here. They are now mirrored under `ixpansion/` so a Pages rebuild cannot
destroy them. References to scripts that never resolved anywhere (`/shared.js`,
Vercel-only analytics, a pyvis helper) were dropped from the mirrors: they 404'd on
the live site too, so no page ever executed them and removing them changes nothing.
`ixpansion/dashboard-live.html` is the dashboard as it was served.

## Known external breakage

`https://ixpansion-live.vercel.app` currently returns 404 on every route
(`/`, `/health`, `/cons`, `/api/edge`). Until that Vercel project is re-linked or its
build fixed, the landing page shows cached figures with an "API offline" badge, and
the live-telemetry organ pages stay in their retry/empty states. Nothing in this
repository can repair the origin.

## Local checks

```bash
python3 scripts/check-links.py                    # authored pages
python3 scripts/check-links.py --include-snapshot # includes archived pages
python3 scripts/check-claims.py                   # figures match data/figures.json
python3 scripts/check-claims.py --github          # ...and the repo count is still live
```
