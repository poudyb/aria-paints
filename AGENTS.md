# AGENTS.md

## Cursor Cloud specific instructions

Aria Paints is a **framework-free static web app** (vanilla HTML/CSS/JS). There is no
package manager, no build step, no lockfile, and no backend/database — the checked-in
files in the repo root are the deliverable (deployed to GitHub Pages from `main`).

### Run the app (dev)
Serve the repo root as static files and open the URL in a browser:

```bash
python3 -m http.server 8080   # from repo root, then open http://localhost:8080
```

There is no hot-reload; refresh the browser after editing files.

### Tests / lint / build
- **Build:** none by design (see `REQUIREMENTS.md`).
- **Lint:** no linter is configured.
- **Tests:** the only automated check is `scripts/verify_catalog.py`, which verifies that
  `paint-section` IDs in `assets/pictures/*.svg` match `data/catalog.js`. Run it with
  `python3 scripts/verify_catalog.py` (stdlib only, no deps; exits non-zero on mismatch).
  Pass picture names as args to check specific pictures, e.g. `python3 scripts/verify_catalog.py butterfly giraffe`.

### Asset-generation scripts (rarely needed, dev-only)
`scripts/generate_picture_sections.py` and `scripts/generate_butterfly_wings.py` regenerate
SVG art from PNG line-art and require `opencv-python`, `numpy`, and `Pillow`. These are NOT
needed to run or test the app — only to regenerate art assets — so they are intentionally
left out of the standard environment setup.

### Notes
- The Google Fonts (Fredoka) CDN link in `index.html` is cosmetic; the app renders fine
  offline with fallback fonts.
