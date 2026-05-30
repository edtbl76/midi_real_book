# MIDI Real Book

MIDI Real Book is a static reference site for a bassist-centered ensemble pairing corpus. Each record presents one ensemble or style pairing with player roles, short context, timeline notes, gear notes, and idiomatic listening examples.

The site is generated from the Markdown ensemble records in `ensembles/` and published as static HTML from `public/`. The homepage provides navigation across the full collection, and each ensemble page includes an in-page sidebar for moving between the players and reference sections.

The site is hosted on Firebase Hosting:

https://midi-real-book.web.app/

## Progressive Web App

MIDI Real Book is a PWA. On Android, Chrome will prompt to add it to your home screen after a couple of visits. On iOS, tap Share → Add to Home Screen in Safari. Once installed it launches full-screen without browser chrome, and all 128 ensemble pages are available offline after the first visit.

**Cache update workflow:** When ensemble content changes, bump `CACHE_VERSION` in `public/sw.js` (e.g. `'v1'` → `'v2'`) before deploying. The browser will install the new service worker on the next visit and automatically clear the old cache.

## Project structure

```
public/          Static site served by Firebase Hosting
  ensembles/     One HTML page per ensemble
  icons/         PWA icons (180, 192, 512px)
  index.html     Homepage with search and ensemble grid
  manifest.json  PWA manifest (name, colors, icons)
  site.css       Styles
  site.js        Search filter and sidebar toggle
  sw.js          Service worker — pre-caches all pages on install
ensembles/       Source Markdown ensemble records
scripts/         Dev utilities
  generate_icons.py  Regenerate PWA icons (requires Pillow)
```
