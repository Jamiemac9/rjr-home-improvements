# RJR Home Improvements website

Static site for R.J.R Home Improvements Ltd (Companies House 13349077), emergency roofers in Birmingham. Built by APX Digital. Read `HANDOFF.md` for full history, current state and open items.

## Commands

```bash
python3 -m pip install -r requirements.txt   # Pillow, once
python3 serve.py                             # build (DEMO mode) + preview; use the URL it prints
python3 build.py && python3 tools/check_site.py   # LIVE-mode build + full link/form/canonical check
DEMO=1 python3 build.py                      # demo build (noindex) without serving
```

Always run `tools/check_site.py` after a change and before committing. It must print `OK`.

## Layout

- `content.py`: all words, reviews, services, areas, photos, housing-feature notes, and `SITE` config. Most edits go here.
- `build.py`: page templates and generator. Writes `site/`.
- `static/assets/`: `site.css` (whole design system), `consent.js` (cookie consent + sticky header/menu), `quote.js` (quote form → WhatsApp), `favicon.svg`.
- `tools/optimise_images.py`: photos in `images/` → WebP sizes, thumbnails, blurred heroes, OG JPEGs.
- `handover/`: client handover, case study notes, marketing content. Keep them in sync with changes.
- `site/`: generated, git-ignored. Never edit by hand.

## Hard rules

- **Facts only.** Never invent prices, response times, "24/7", guarantees, accreditations, insurance, job counts, staff names (only "Ryan", from reviews) or reviews. Reviews and `QUOTES` are verbatim.
- **Photo pairs in `PROJECTS` are verified jobs.** Don't re-pair or relabel them.
- **Design system:** colours only `--ink`, `--light`/`--light-2`, `--orange`, `--neon`. No border-radius, box-shadow, gradients or background highlights behind text. Font sizes only via `--step-*` clamp tokens; spacing only via `--s-*` and `gap`. Body text max 65ch. Must work at 360px with no horizontal scroll.
- **Quote form sends nothing to a server.** Inputs have no `name` attributes; `quote.js` only builds a wa.me link. If that changes, update the privacy policy in `build_legal()`.
- **Python 3.8+ compatible** `build.py`: no nested same-type quotes in f-strings (the file uses `%` formatting).
- Internal URLs in templates are root-relative (`/services/...`); `relativise()` converts them per page. Don't hard-code `../`.
- British English, no em dashes in customer-facing copy, plain words.

## Git

- The **repo root is the parent folder** (`~/Desktop/RJR Home Improvements`); the site lives in `rjr-site/`. Netlify/Cloudflare need base/root directory `rjr-site`.
- Remote: https://github.com/Jamiemac9/rjr-home-improvements (private). Work on a branch, open a PR into `main`.
- Commit messages: imperative summary + why. Don't commit `site/`, zips or `.DS_Store`.

## Gotchas

- **Port 8080 on this Mac belongs to Hermes** (and an old test server), so `localhost:8080` gives `ERR_EMPTY_RESPONSE`. `serve.py` picks a free port; use what it prints.
- `serve.py` builds in **DEMO** mode (noindex). Live deploys need a build without `DEMO=1`; `netlify.toml` currently sets `DEMO=1` for the preview.
- The Netlify drag-and-drop demo (super-gingersnap-d2d52f.netlify.app) is a stale, live-mode build; see `HANDOFF.md` → Open items.

## After any change, keep these in sync

1. `handover/1-case-study-changes.md`: add a round (feedback → changes → checks).
2. `handover/3-client-handover.md` if anything client-visible changed.
3. Obsidian vault `~/Documents/Obsidian Vault/Web Dev Clients/RJR Home Improvements/`: hub note `RJR Home Improvements — Website Project.md` (edit by hand) plus mirrored copies of the handover docs (`python3 tools/sync_obsidian.py`). The vault is its own git repo (private remote `Jamiemac9/obsidian-vault`) with other people's pending work; commit only RJR files unless told otherwise.
