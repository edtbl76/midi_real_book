# MIDI Real Book

MIDI Real Book is a static reference site for ensemble study. Each record covers the players, context, timeline, gear, and key recordings for a given ensemble or style grouping.

The site is hosted on Firebase Hosting:

https://midi-real-book.web.app/

## How it works

Source files live in `ensembles/` — one Markdown file per ensemble. A build step converts them to static HTML in `public/` using [Eleventy](https://www.11ty.dev/). The homepage is generated from the same build. You never edit the HTML files directly.

**Workflow for updating or adding an ensemble:**

1. Edit (or create) `ensembles/{Ensemble Name}/ensemble.md`
2. Run `npm run build`
3. Commit and push — Firebase Hosting deploys automatically via GitHub Actions

**Workflow for adding a new ensemble:**

1. Create `ensembles/{Ensemble Name}/ensemble.md` following the structure of an existing file
2. `npm run build` — the new page and index card are generated automatically
3. Bump `CACHE_VERSION` in `public/sw.js` before deploying (see PWA section below)

## Tech stack

| Layer | Tool |
|---|---|
| Static site generator | [Eleventy 3.x](https://www.11ty.dev/) |
| Markdown parser | [markdown-it](https://github.com/markdown-it/markdown-it) + [markdown-it-anchor](https://github.com/valeriangalliat/markdown-it-anchor) |
| Templating | [Nunjucks](https://mozilla.github.io/nunjucks/) |
| Hosting | [Firebase Hosting](https://firebase.google.com/docs/hosting) |
| CI/CD | GitHub Actions |
| Icon generation | Python + Pillow + CairoSVG (`scripts/generate_icons.py`) |

## Progressive Web App

MIDI Real Book is a PWA. On Android, Chrome will prompt to add it to your home screen after a couple of visits. On iOS, tap Share → Add to Home Screen in Safari. Once installed it launches full-screen without browser chrome, and all ensemble pages are available offline after the first visit.

**Cache update workflow:** Any time you rebuild and deploy, bump `CACHE_VERSION` in `public/sw.js` (e.g. `'v8'` → `'v9'`) so the service worker clears the old cache on next visit.

## Project structure

```
ensembles/                     Source Markdown — edit these
  {Ensemble Name}/
    ensemble.md                One file per ensemble
_includes/
  ensemble.njk                 Eleventy layout template for ensemble pages
index.njk                      Eleventy template for the homepage
.eleventy.js                   Eleventy build config
public/                        Generated output — do not edit by hand
  ensembles/                   One HTML page per ensemble (generated)
  icons/                       PWA icons (180, 192, 512px)
  index.html                   Homepage (generated)
  manifest.json                PWA manifest
  site.css                     Styles
  site.js                      Search filter and sidebar toggle
  sw.js                        Service worker — pre-caches all pages on install
scripts/
  generate_icons.py            Regenerate PWA icons (requires Pillow + CairoSVG)
  preview_material.py          Icon design preview tool
```
