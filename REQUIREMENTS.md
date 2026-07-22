# Aria Paints Requirements

## Product Vision

Aria Paints is a toddler-friendly "paint by sections" web app. Instead of freehand drawing or paint-by-number labels, Aria chooses a concrete color from a fixed palette and taps outlined sections of a picture to fill them. The experience should be fast, playful, simple, and visually similar in spirit to Arias-playground.

The primary user is Aria. There is no parent-facing mode or controls.

The long-term vision still includes two themed worlds (Land and Sea) where Aria paints characters inside a scene that already looks alive with natural, pre-colored scenery. Shipping today focuses on a growing set of **standalone coloring pictures** on the home screen; House, Fish, Land World, and Sea World remain visible as "Coming soon" while their assets and app scaffolding stay in the repo for later unlock.

## How The Project Evolved

This document started as the Version 1 product brief (standalone butterfly / giraffe / house / fish plus Land and Sea worlds). As the app was built, the product and art process shifted in a few important ways:

1. **Butterfly-first launch.** The first shipped build opened with a single live butterfly page and "Coming soon" tiles for everything else.
2. **Line-art overlay coloring.** Instead of purely hand-drawn SVG cartoons, most real coloring pages are now based on uploaded PNG line art. Paintable SVG regions sit underneath the PNG; the art is composited with a multiply blend so black outlines stay black over fills.
3. **Butterfly wing tracing.** Early wing fills used coarse quadrant cuts and left gaps / bleed. Wings are now detected as connected white regions in the artwork, expanded halfway under the black outline, and clipped against neighboring wings and the exterior background.
4. **General picture tracer.** Adding giraffe, Christmas tree, and turtle led to `scripts/generate_picture_sections.py`: a reusable pipeline that turns every enclosed white region of a line-art PNG into a paintable section and updates `data/catalog.js`.
5. **Richer pictures.** Traced scenes have many more sections than the original "about 7–10" brief (for example, giraffe ~51, Christmas tree ~24, turtle ~23), because every enclosed spot, ornament, shell plate, etc. becomes colorable.
6. **Worlds deferred, not abandoned.** Land World and Sea World scenery, thumbs, and component wiring still exist in the app, but home currently shows them (along with House and Fish) as Coming soon. Live home pictures today are Butterfly, Giraffe, Christmas Tree, and Turtle.
7. **Device hardening.** Later work focused on iPad / Safari: absolute SVG image URLs after `DOMParser`, touch + click pairing, PNG export fallbacks, and explicit SVG sizing so WebKit does not collapse the paint canvas to 0×0.
8. **Static hosting.** The app is deployed from `main` to GitHub Pages with no build step.

## Project Requirements

- Project/repo name: `aria-paints`.
- Displayed app title: `Aria Paints`.
- This is a completely separate git project from Arias-playground.
- Use a simple static web app structure, similar to Arias-playground: plain HTML, CSS, and JavaScript.
- Avoid frameworks and heavy dependencies.
- Prefer no build step. The app should work from a simple static server (and from GitHub Pages).
- All art must be checked into the repo as deterministic SVG/PNG/data. Do not generate images at runtime in the browser.
- Dev-only Python scripts may regenerate checked-in SVG/catalog data from PNG line art; those scripts are not part of the shipped app and are not required to run or host it.
- No backend, login, accounts, analytics, tracking, cloud save, or external image generation.
- Prioritize responsiveness on iPad, iPhone, laptop, and desktop.

## Target Devices And Input

- Support iPad/tablet touch, iPhone/mobile touch, laptop mouse, desktop mouse, and laptop touchpad.
- Do not require keyboard input.
- Use large toddler-friendly touch targets.
- Prevent accidental pinch/zoom/browser gestures similar to Arias-playground.
- Layout must be responsive across phone, tablet, and desktop.
- Painting and PNG download must remain usable on iPad Safari (including older WebKit quirks around SVG `<image>` loading, flex sizing, and `download` links).

## Core Painting Behavior

- A picture is made of several paintable SVG sections (elements with class `paint-section` and stable IDs).
- Each paintable section starts blank/white.
- Aria selects a color from a fixed palette, then taps/clicks a section to fill it.
- If a section is blank, tapping fills it with the selected color.
- If a section already has a different color, tapping replaces it with the selected color.
- If a section already has the selected color, tapping the section again clears it back to blank/white.
- Use solid fills only. No brush texture, gradients, freehand drawing, or drag-to-paint.
- A picture is complete when every paintable section currently has a color.
- On completion, show celebration emojis, but do not lock the picture. Aria can keep editing.
- No sounds for now.
- Choosing a standalone picture always starts fresh. Paint state lives in memory only and does not survive navigating home or reloading the page.

## Color Palette

- Use a fixed palette of 12 concrete crayon-style color buttons (visual crayons, not plain squares).
- No visible text labels on the color buttons (use `aria-label` for accessibility).
- Do not include white in the palette because blank sections are white.
- Colors:
  - Red `#e53935`
  - Orange `#fb8c00`
  - Yellow `#fdd835`
  - Green `#43a047`
  - Blue `#1e88e5`
  - Light blue `#4fc3f7`
  - Purple `#8e24aa`
  - Pink `#f06292`
  - Brown `#8d6e63`
  - Black `#212121`
  - Gray `#757575`
  - Teal `#00897b`
- The selected crayon must have a clear visual outline/ring and feel obviously active.

## Home And Navigation Flow

- On launch, show a single home screen with **picture cards**, not category tiles (no Animals, Vehicles, etc.).
- Each live card shows a visual preview of the artwork Aria can color.
- Current home content:
  - **Live standalone pictures** (open directly into painting):
    - Butterfly
    - Giraffe
    - Christmas Tree
    - Turtle
  - **Coming soon** (visible but not openable yet):
    - House
    - Fish
    - Land World
    - Sea World
- Flow for a standalone picture:
  - Home → tap picture card → paint picture → back to home.
- Aria should be able to go back to home and pick something else at any time.
- Planned world flow (when worlds are unlocked):
  - Home → tap world card → full scene → tap a paintable character/object → paint it → return to full scene → back to home when done exploring.

## Standalone Picture Content

Use a fixed checked-in set. Do not generate or swap images on each load.

### Live standalone pictures

| Picture | Source style | Approx. sections | Notes |
|---|---|---|---|
| Butterfly | PNG line art + traced wings + hand-placed accent spots | ~22 | Wings from `generate_butterfly_wings.py`; inner spots remain authored SVG accents |
| Giraffe | PNG line art fully traced | ~51 | Body, spots, scenery regions enclosed by the drawing |
| Christmas Tree | PNG line art fully traced | ~24 | Tree, ornaments, and enclosed details |
| Turtle | PNG line art fully traced | ~23 | Shell plates and body regions; generator uses gap-closing for hairline outline breaks |

### Prepared but not yet live on home

These assets / catalog entries exist for the planned House card and Sea / Land worlds, but home currently marks House and Fish as Coming soon:

- House (hand-authored SVG sections)
- Fish, Dolphin, Crab, Whale (hand-authored SVG sections for Sea World / fish card)

### Picture complexity guidance

- Hand-authored cartoon SVGs can stay around a modest number of named parts (body, roof, fin, etc.).
- Traced line-art pictures will naturally have more sections: every closed white region above a minimum area becomes paintable.
- Keep drawings toddler-friendly and coloring-book-like, with clear dark outlines.
- Section IDs must be unique across pictures that can appear together in the DOM (home previews). Traced pictures use a `{picture}-shapeNN` prefix for that reason.

## Art Pipeline: Turning An Uploaded Picture Into A Colorable Page

This is the process used whenever a new coloring picture is added from user-provided line art.

### 1. Provide the line art

- Drop a clean black-on-white PNG into `assets/pictures/<picture>-art.png`.
- Prefer closed outlines. Regions open to the image border (sky, ground, outer background) stay **unpaintable** by design.
- If outlines have hairline gaps that leak into the background, the generator can thicken lines during detection only (for example turtle uses a gap-close of 5px). Display art itself is left untouched.

### 2. Generate paint sections

For most new pictures, run:

```bash
python3 scripts/generate_picture_sections.py <picture>
```

What the script does:

1. Loads `<picture>-art.png`.
2. Treats near-white pixels as candidates for regions.
3. Finds connected white components.
4. Marks border-touching components as background (not paintable).
5. Keeps interior components above a minimum area as paint sections.
6. Expands each section halfway under the black outline so fills meet the line with no white sliver, without bleeding into neighbors or background.
7. Writes `assets/pictures/<picture>.svg` containing:
   - one `<path class="paint-section">` per region, starting `fill="#fff"`
   - an `<image>` overlay of the PNG art with `pointer-events="none"`
8. Updates that picture's `viewBox` and `sections` list in `data/catalog.js`.

Butterfly is a special case:

- Wing regions are regenerated with `scripts/generate_butterfly_wings.py` from `butterfly-art.png`.
- Inner accent spots / ovals remain hand-authored SVG on top of the art overlay.
- Same multiply-blend idea: fills live under the black line art.

Hand-authored pictures (house / sea creatures) skip the tracer and keep manually named SVG sections.

### 3. Wire the picture into the app

- Ensure the picture exists in `PICTURE_CATALOG` in `data/catalog.js` (the generator updates an existing entry).
- Add the picture id to `STANDALONE_PICTURE_IDS` when it should appear as a live home card.
- Keep it out of `COMING_SOON_ITEMS` once unlocked.
- Add any picture-specific CSS only if needed (art overlay multiply blend is shared; layout aspect rules may be needed for unusual viewBoxes).

### 4. Verify catalog ↔ SVG IDs

```bash
python3 scripts/verify_catalog.py
# or for specific pictures:
python3 scripts/verify_catalog.py butterfly giraffe christmasTree turtle
```

This checks that every `.paint-section` id in the SVG matches the `sections` list in `data/catalog.js`.

### 5. Runtime rendering

At runtime the app:

1. Fetches the checked-in SVG.
2. Absolutizes any nested `<image href="...">` URLs (important for Safari / iPad after `DOMParser`).
3. Clones the template, applies in-memory fills, and binds tap handlers to `.paint-section` nodes.
4. Composites the PNG line art over fills with CSS `mix-blend-mode: multiply`, so outlines stay black on top of color.

No network image generation and no on-the-fly tracing happen in the browser.

### Dev-only script dependencies

`generate_picture_sections.py` and `generate_butterfly_wings.py` need `opencv-python`, `numpy`, and `Pillow`. They are intentionally not part of the normal run/test environment. The shipped site only needs the checked-in HTML/CSS/JS/SVG/PNG files.

## Worlds (Land And Sea) — Planned

Worlds remain part of the product direction. Scene scaffolding, thumbnails, and component placement already exist in `scripts/app.js`, but home currently shows Land World and Sea World as Coming soon rather than launching them.

### Worlds concept

- A world is a single full-scene view with fixed, natural-looking colors on background and decorative elements.
- Paintable items appear in the scene as white outlined shapes (same painting rules as standalone pictures).
- Aria taps a paintable item in the scene, paints its sections on a dedicated painting screen, then returns to the full scene.
- In the full scene, painted items show Aria's chosen colors.
- Items with at least one colored section may use simple CSS/SVG animation (walk, bob, flutter, swim, etc.) when back in the scene.
- Pre-colored scenery and decorations are **not** tappable for painting—they are visual context only.
- The scene should not become a complex game or physics simulation.

### Planned worlds flow

- Home → tap Land World or Sea World → full scene.
- Tap a paintable item → item painting screen (same palette and fill/toggle behavior).
- Tap the world/back control → return to full scene.
- The item appears colored in the scene and may animate if at least one section is colored.
- Aria can reselect any paintable item, including partially or fully colored items, and continue editing.
- If all sections of an item are cleared, it returns to uncolored/non-animated state in the scene.
- Back from the full scene returns to home.

### Worlds state

- Store world state only while Aria remains inside that selected world.
- If she leaves a world (back to home) and enters it again later, that world starts fresh.
- No state should survive page reloads or app restarts.

### Land World (planned contents)

Paintable (reuse shared SVGs where noted):

- Butterfly
- Giraffe
- House

Pre-colored:

- Sunny land scenery (sky, hills/grass, sun, etc.)
- A windy road (gray asphalt with simple lane markings)—already colored, not paintable

### Sea World (planned contents)

Paintable:

- Fish (same asset intended for the home fish card)
- Dolphin
- Crab
- Whale

Pre-colored:

- Ocean water, seaweed, coral, rocks/bubbles
- Small decorative creatures that are already colored and not meant to be edited

### Worlds complexity

- About 3–4 paintable items per world (Land: 3; Sea: 4).
- Unpainted items in the scene should read clearly as tappable white outlined shapes.

## Pre-Colored Vs Paintable Art

- **Paintable** assets use `.paint-section` with default white fill; section IDs match catalog data.
- **Line-art overlay pictures** keep a non-interactive PNG/SVG `<image>` layer above fills (multiply blend).
- **Pre-colored** world scenery uses fixed hex fills (or non-interactive layers). They must not respond to the palette or appear in fill state.
- When worlds are unlocked, reuse the same butterfly / giraffe / house (and fish) definitions for standalone mode and world component mode.

## Download / Export

- Provide a download button for the current artwork.
- Export as PNG.
- The PNG should include the artwork and a title/date label on a white background.
- For standalone pictures, download is allowed once at least one section is colored.
- For worlds (when unlocked), download the **full scene** once at least one paintable section in that world is colored.
- If nothing is colored yet, disable the download button.
- Download does not require the picture/world to be complete.
- On iOS Safari, opening the PNG in a new tab is an acceptable fallback when `<a download>` is unreliable.

## Repository Layout (current)

- `index.html` — app shell
- `styles/app.css` — layout, home, palette crayons, multiply blend, celebrations, responsive rules
- `scripts/app.js` — navigation, painting, palette, download, world scaffolding
- `data/catalog.js` — picture metadata, live home ids, coming-soon ids
- `assets/pictures/*.svg` — colorable picture templates
- `assets/pictures/*-art.png` — source line art for traced pictures
- `assets/world-thumbs/` — Land / Sea home thumbnails (for upcoming unlock)
- `scripts/generate_picture_sections.py` — general PNG → SVG section tracer
- `scripts/generate_butterfly_wings.py` — butterfly wing tracer
- `scripts/verify_catalog.py` — catalog/SVG id consistency check
- Live site: GitHub Pages from `main` ([https://poudyb.github.io/aria-paints/](https://poudyb.github.io/aria-paints/))

## Out Of Scope (for now)

- Category navigation (Animals, Vehicles, Shapes & Objects, Nature & Food).
- Large picture libraries beyond the curated home set.
- Unlocking more than the two planned worlds (no Jungle Safari, Busy Street, Farm Day, Space Trip, etc.).
- Parent dashboard, accounts, backend, analytics, cloud save, persistent progress.
- Runtime or network image generation.
- Freehand drawing, brush sizes, textures, sounds.
- Complex games/physics inside worlds.

## Implementation Guidance For Future Agents

- Prefer extending the existing catalog + SVG template pattern over one-off painting screens.
- For new uploaded line art, use `generate_picture_sections.py`, then verify with `verify_catalog.py`, then add the id to `STANDALONE_PICTURE_IDS`.
- Keep painting state in memory only.
- Share fill/toggle/recolor logic across standalone pictures and (when unlocked) world items.
- Share palette rendering across all painting screens.
- Keep rendering fast and deterministic from checked-in assets.
- When touching SVG image loading, taps, layout, or PNG export, re-check iPad Safari behavior.
- Avoid adding dependencies unless they materially simplify PNG export or SVG rendering for the shipped static app.

## Acceptance Criteria

### Current shipped experience

- The app opens to a home screen of picture cards: Butterfly, Giraffe, Christmas Tree, Turtle, plus Coming soon cards for House, Fish, Land World, and Sea World.
- Each live standalone picture can be painted section by section from its card.
- Selected crayon color is visually obvious.
- Tapping same-color section clears it; tapping with a different selected color recolors it.
- Completion triggers celebration emojis and does not lock editing.
- Download is disabled until at least one section is colored; PNG includes artwork and date on a white background.
- Traced pictures show PNG line art over fills with black outlines preserved.
- No network image generation or runtime art generation in the browser.
- App is responsive and usable on iPhone, iPad, laptop, and desktop.
- `python3 scripts/verify_catalog.py butterfly giraffe christmasTree turtle` passes for live traced pictures.

### Planned when worlds / remaining cards unlock

- House and Fish become live standalone cards (or Fish is only reached through Sea World, if that product choice is made later).
- Land World shows pre-colored land scenery and road; butterfly, giraffe, and house are paintable in the scene.
- Sea World shows pre-colored ocean/scenery and small pre-colored creatures; fish, dolphin, crab, and whale are paintable.
- Worlds support full scene, tap-to-paint item, return to scene, in-world remembered state, and simple animation for colored items.
- Leaving a world and re-entering starts that world fresh.
- World download captures the full scene once something is colored.
