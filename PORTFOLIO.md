# Portfolio evaluation — 2026-10-30

Evidence-based pass over all 24 repositories under `adjjvmorii26-png`, produced
from the GitHub API (`/users/adjjvmorii26-png/repos`), repo contents endpoints,
and workflow runs. Regenerate the table with the same queries listed at the end.

## Inventory

| Repo | Lang | Size | Last push | License | Issues | Notes |
|---|---|---|---|---|---|---|
| `adjjvmorii26-png.github.io` | HTML | 37 KB | 0d ago | — | 1 | Pages |
| `ixpansion` | Python | 8272 KB | 0d ago | MIT | 10 | Pages, 10 issues |
| `PlayGround` | — | 805 KB | 2d ago | — | 14 | no description, 14 issues |
| `pan-copilot` | — | 3052 KB | 6d ago | — | 1 | — |
| `collaborative-canvas` | Python | 927 KB | 7d ago | MIT | 0 | — |
| `workforce-` | Python | 33 KB | 7d ago | — | 1 | no description |
| `solid-organism` | — | 115 KB | 10d ago | — | 0 | — |
| `pentaxis-5d-engine` | TypeScript | 518 KB | 12d ago | NOASSERTION | 1 | — |
| `nexus-observatory` | JavaScript | 150 KB | 12d ago | — | 0 | — |
| `echotide-engine` | JavaScript | 25 KB | 22d ago | — | 0 | — |
| `polychron-atlas` | JavaScript | 31 KB | 22d ago | — | 0 | — |
| `luminant-reliquary` | JavaScript | 22 KB | 22d ago | — | 0 | — |
| `antimemetic-architecton` | JavaScript | 16 KB | 22d ago | — | 0 | — |
| `phaseshift-manifold` | JavaScript | 15 KB | 22d ago | — | 0 | — |
| `interstice` | HTML | 33 KB | 24d ago | — | 0 | no description |
| `oracle-engine` | Python | 11 KB | 24d ago | — | 0 | — |
| `chronocrypt-orrery` | JavaScript | 31 KB | 24d ago | — | 0 | — |
| `aetherbloom` | — | 34 KB | 37d ago | — | 0 | — |
| `astral-forge` | JavaScript | 30 KB | 40d ago | — | 0 | — |
| `dev` | Python | 25 KB | 40d ago | — | 0 | — |
| `feature-1.5-vivarium-lattice` | Python | 45 KB | 40d ago | — | 0 | no description |
| `aegis-workspace` | Python | 9 KB | 40d ago | — | 0 | — |
| `capability-sandbox` | Python | 16 KB | 40d ago | Apache-2.0 | 0 | no description |
| `feature-1.3-mesh-hitl-si` | Python | 1 KB | 50d ago | — | 0 | — |

## Findings

**1. Licensing is the largest systemic gap — 21 of 24 repos have no recognised license.**
Only `ixpansion` and `collaborative-canvas` (MIT) and `capability-sandbox`
(Apache-2.0) are unambiguous; `pentaxis-5d-engine` reports `NOASSERTION`, which
GitHub treats as unresolved.
Without a license, the default is "all rights reserved": nobody can legally reuse,
fork, or build on any of the other 21 repos, including the nine sibling
"substrate" engines that read as intended-public art pieces. This is a
one-file fix per repo and the highest value per minute available here.

**2. Backlog is concentrated in two repos.** 24 of the 28 open issues sit in
`PlayGround` (14) and `ixpansion` (10); every other repo has 0 or 1. `PlayGround`
is also the only repo with a substantial backlog and *no description*, so a
visitor cannot tell what those 14 issues are about.

**3. Descriptions are missing on 5 repos** — `PlayGround`, `workforce-`,
`interstice`, `feature-1.5-vivarium-lattice`, `capability-sandbox`. Four of the
five are also among the lowest-traffic repos, which is likely the same cause.

**4. Naming and purpose are inconsistent.** `workforce-` ends in a stray hyphen.
`dev`, `aegis-workspace`, `capability-sandbox`, and the two `feature/*` repos are
scratch or work-in-progress work mixed into the same public namespace. The
landing page markets "24 Constellation Repos" — accurate as a count, but roughly
four of those 24 are scaffolding rather than constellation.

**5. Complexity is concentrated in `ixpansion`.** 8272 KB of the 14253 KB total
(58%), 4564 tracked paths, 2854 Python files with 1254 of them flat inside
`api/`. Flat module sprawl at that scale makes discovery and import boundaries
hard; the WSGI dispatcher also hardcodes "352 modules" in its docstring while the
landing page claims 744 and the audit claimed 41+.

**6. CI coverage is partial but healthy where present.** 10 of 24 repos have a
`.github` directory. Sampled runs are all green: `ixpansion` (Vercel Deployment
Sentinel), `PlayGround` (OpenCode #14), `collaborative-canvas` (auto-evaluate),
`pentaxis-5d-engine` (Build and test). `pan-copilot` has a `.github` directory but
no runs recorded, so its workflow has either never triggered or never existed as
a workflow file.

**7. Activity is healthy.** Every repo was pushed within the last 49 days; two
were pushed today. Nothing is archived. This is not a graveyard — the problem is
presentation and legal clarity, not decay.

**8. Only 2 repos publish a hosted surface** (`github.io`, `ixpansion` Pages).
The other 22 have no live demo, which for visual/generative projects (the
`*-engine` / `*-atlas` family) hides the main thing they do.

## Recommendations, ranked by value per unit of effort

1. **Add a LICENSE to the 21 unlicensed repos.** MIT matches `ixpansion`; use
   Apache-2.0 only where a patent grant matters. Highest impact, minutes each.
2. **Write the 5 missing descriptions**, starting with `PlayGround` (it has the
   largest backlog and no explanation).
3. **Triage the 24 open issues in `PlayGround` + `ixpansion`**, or close what is
   stale — an open count of 14 with no description reads as abandoned.
4. **Rename or archive the scratch repos** (`workforce-` → `workforce`,
   `dev`/`aegis-workspace`/`feature-*` → archived or clearly marked). Then the
   landing page's "24 constellation repos" claim is honest.
5. **Add Pages to the visual engines.** Each `*-engine` repo already renders in a
   browser; publishing it converts a private repo into a demo.
6. **Centralise the module count.** One number, one source, referenced by the
   site, the dispatcher docstring, and any audit. Today there are four values.

   *Partially done in this repository:* `data/figures.json` is now the single
   source and `scripts/check-claims.py` fails the build when the HTML disagrees
   with it. The remaining work is on the `ixpansion` side, whose dispatcher still
   says 352 while the site says 744.

## Telegram handle — resolved, and the answer needed a second look

The site used three variants: `aleph_bot` (portal card text), `alpeh_bot`
(`ixpansion/portal.html`), and `alpeha_bot` (landing page CTA and footer). HTTP
status was useless here — `t.me` returns a generic 200 for every handle, existing
or not.

An authenticated `getChat` lookup settled existence:

| Handle | Result |
|---|---|
| `alpeh_bot` | **does not exist** (`chat not found`) |
| `alpeha_bot` | **does not exist** (`chat not found`) |
| `aleph_bot` | exists — ownership unverified |
| `adjjv_bot` | exists — the bot whose token was supplied |

The landing page's primary CTA was pointing at a bot that does not exist.

**Do not link the public CTA at `adjjv_bot`.** Its own registered commands are
`/threads`, `/newthread`, `/thread`, `/current`, `/history`, `/status`,
`/whoami`, `/start`, `/help` — a Cline thread bridge for private use, with no
organism commands at all. It is not "the organism's ambassador on Telegram".

All public references therefore point at `aleph_bot`, the only existing handle
the site's own copy claims. Ownership of `aleph_bot` could not be verified from
here: if it is not yours, tell me and the four references should be removed
rather than repointed.



7. **Split `ixpansion/api/`** into subpackages by domain (the docstring already
   names 8 entry points) to make 1254 flat modules tractable.

## What was changed in this repository during this pass

- `robots.txt` and a generated `sitemap.xml` (9 authored URLs; 206 archived
  module pages deliberately excluded so they do not outrank the landing page).
- `404.html`, styled to match, with no external dependencies.
- Icon set rendered from one SVG geometry with no third-party imaging library:
  `assets/icon.svg`, `favicon-32.png`, `apple-touch-icon.png`, and a 1200×630
  `assets/og-card.png` social preview.
- Canonical URL, Open Graph, and Twitter card metadata on the landing page and
  the dashboard; `theme-color` and `color-scheme`.
- Accessibility: visible `:focus-visible` outlines, `prefers-reduced-motion`
  honoured in both CSS and the module-counter JavaScript.
- Regenerators: `scripts/make-icons.py`, `scripts/make-sitemap.py`.

## Reproducing this evaluation

```bash
gh api 'users/adjjvmorii26-png/repos?per_page=100&sort=pushed'
gh api repos/adjjvmorii26-png/<repo>/contents          # README / .github presence
gh run list --repo adjjvmorii26-png/<repo> --limit 1   # CI health
```
