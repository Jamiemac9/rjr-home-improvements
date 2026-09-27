# RJR Home Improvements — website

Static site for RJR Home Improvements (R.J.R Home Improvements Ltd), emergency roofers in Birmingham & the West Midlands.
Website by [APX Digital](https://apxdigital.io).

- 95 indexable pages: home, contact, 12 roofing service pages, 3 grouped trade pages, 10 area pages, 60 area × service pages, before/after, reviews, about, privacy policy, cookie policy, sitemap (plus a 404).
- Plain HTML + one CSS file + two small scripts (cookie consent, quote form). No framework, no build tooling beyond Python.
- Quote form on every page (and at `/contact/`): dropdowns for service, urgency, area, property type, reply method and time, plus name, postcode and details. It opens WhatsApp with the answers written in; the website never sends or stores them. Each page pre-selects its own service/area (and "Emergency" on emergency pages). Options live in `build.py` (`URGENCY`, `PROPERTY`, `REPLY`, `WHEN`); services and areas come from `content.py`.
- Every internal link is relative, so the `site/` folder works on any host, in a sub-folder, or opened straight from disk.

**Deploying?** See [DEPLOY.md](DEPLOY.md): Cursor setup, a demo on Netlify or Cloudflare before the domain is bought, and the launch checklist.

## Quick start

```bash
pip install -r requirements.txt
python3 serve.py
```

`serve.py` rebuilds the site, finds a free port, prints the address (e.g. `http://127.0.0.1:8000/`) and opens it in your browser. **Use the address it prints.** Other apps on this Mac use common ports: Hermes runs on 8080, so `localhost:8080` gives `ERR_EMPTY_RESPONSE`.

**Preview through a server, not by double-clicking files.** Opening `site/index.html` straight from disk loads that page, but folder links like `services/` then show a folder listing instead of the page. In Cursor, either run `python3 serve.py`, or use the Live Server extension: the included `.vscode/settings.json` points it at `site/` on port 5500.

Troubleshooting:
- **"Error response 404"**: a preview server is pointing at the wrong or an old folder. Stop it and run `python3 serve.py`.
- **"ERR_EMPTY_RESPONSE"**: you're on a port another app owns (e.g. 8080 = Hermes). Use the address `serve.py` prints.

`build.py` deletes and regenerates `site/` every run, so never edit files inside `site/` by hand.

## Project layout

```
build.py                   page templates + generator
serve.py                   build + preview (auto-picks a free port, prints the address)
.vscode/settings.json      points Cursor's Live Server at site/
content.py                 ALL words, reviews, services, areas, images: edit here
tools/optimise_images.py   makes WebP sizes, thumbnails, blurred hero backgrounds, OG images
images/                    original photos (source of truth)
static/                    copied into site/ as-is
  assets/site.css          the whole design system
  assets/consent.js        cookie consent (analytics only run after "Accept")
  assets/quote.js          quote form -> pre-filled WhatsApp message (nothing sent to a server)
  assets/favicon.svg
  _headers                 cache + security headers for Netlify / Cloudflare Pages
site/                      GENERATED output: deploy this folder
netlify.toml               build settings if deploying on Netlify
handover/                  case study notes, marketing content, client handover
```

## Before launch: fill these in `content.py` → `SITE`

| Key | Why |
|---|---|
| `url` | Live domain, set to `https://rjrhomeimprovements.com`. Canonicals, sitemaps, Open Graph and schema all use it. |
| `company_number` | Shown in the footer and privacy policy. |
| `registered_office` | Shown in the privacy policy. |
| `email` (optional) | Adds email to footer, privacy policy and schema. |
| `ico_number` (optional) | Adds ICO registration to the privacy policy. |
| `home_hero` | Image key for the blurred home page hero background (currently the gable house photo). |

Then run `python3 build.py` again. Get the privacy policy checked by the business before launch.

## Content rules (keep these)

Only use facts the business supplied. No invented prices, response times, "24/7", guarantees, accreditations, insurance claims, job counts or reviews. Reviews in `REVIEWS` and `QUOTES` are verbatim. The photo pairings in `PROJECTS` are verified jobs (same building before and after), so don't re-pair them.

## How the local pages stay unique

Each area lists its housing `features` (e.g. `slate`, `outriggers`, `garages`, `conservation`). Area × service pages are built from `FEATURE_NOTES[service][feature]` Q&As, so a roof leak page for Moseley (slate, tall stacks, trees, conservation) says different things from Shirley (concrete tiles, garages, dry-fix). To strengthen a page, add a feature to an area or a note to `FEATURE_NOTES`. Real job photos per area would be the next big win.

## Adding a page

- **New service:** add a dict to `SERVICES` (copy an existing one). Set `"matrix": True` to also generate it for every area, then add matching `FEATURE_NOTES`.
- **New area:** add to `AREAS` and its slug to `ORDER` in `build.py`.
- **New photo:** drop it in `images/`, add it to `IMG` with alt text and a focal point, and use its key in `PROJECTS` or as a `hero`.

## Analytics (optional)

Nothing tracks by default. To add analytics, set `SITE["analytics_html"]` in `content.py` to the provider's `<script>` tags. `build.py` rewrites them to `type="text/plain" data-consent="analytics"`, and `consent.js` only runs them after the visitor clicks **Accept analytics**. Update the cookie policy text in `build.py` (`build_legal`) to name the provider and its cookies.

## Performance notes

- Images: responsive WebP (480/720/960) with `srcset`; hero backgrounds are pre-blurred 720px WebPs (~10 KB) so there's no CSS blur cost. Width/height are set on every image.
- Fonts: Google Fonts loaded non-blocking (`preload` + `onload`). For full GDPR comfort and one less connection, self-host Archivo, IBM Plex Sans and IBM Plex Mono as WOFF2 in `static/assets/fonts/`, then replace the font `<link>` in `build.py`'s `page()` with `@font-face` rules in `site.css`, and remove the Google Fonts paragraph from the privacy and cookie policies.
- CSS/JS are cache-busted with a content hash (`?v=`), so `_headers` can cache `/assets/*` for a year.

## Deploy

Domain: rjrhomeimprovements.com (the site is built for the non-www version; `netlify.toml` redirects www to it). Any static host. Netlify: connect the repo; `netlify.toml` runs the build and publishes `site/`. Cloudflare Pages: build command `pip install -r requirements.txt && python3 build.py`, output directory `site`. Or upload the `site/` folder directly.
