# Aria Paints Requirements

## Product Vision

Aria Paints is a toddler-friendly "paint by sections" web app. Instead of freehand drawing or paint-by-number labels, Aria chooses a concrete color from a fixed palette and taps outlined sections of a picture to fill them. The experience should be fast, playful, simple, and visually similar in spirit to Arias-playground.

The primary user is Aria. Version 1 has no parent-facing mode or controls.

Version 1 is intentionally small: a few standalone coloring pictures on the home screen, plus two themed worlds (Land and Sea) where Aria paints characters inside a scene that already looks alive with natural, pre-colored scenery.

## Project Requirements

- Project/repo name: `aria-paints`.
- Displayed app title: `Aria Paints`.
- This is a completely separate git project from Arias-playground.
- Use a simple static web app structure, similar to Arias-playground: plain HTML, CSS, and JavaScript.
- Avoid frameworks and heavy dependencies for Version 1.
- Prefer no build step. The app should work from a simple static server.
- All art must be checked into the repo as deterministic SVG/data. Do not generate images at runtime.
- No backend, login, accounts, analytics, tracking, cloud save, or external image generation.
- Prioritize responsiveness on iPad, iPhone, laptop, and desktop.

## Target Devices And Input

- Support iPad/tablet touch, iPhone/mobile touch, laptop mouse, desktop mouse, and laptop touchpad.
- Do not require keyboard input.
- Use large toddler-friendly touch targets.
- Prevent accidental pinch/zoom/browser gestures similar to Arias-playground.
- Layout must be responsive across phone, tablet, and desktop.

## Core Painting Behavior

- A picture is made of several paintable SVG sections.
- Each paintable section starts blank/white with a clear outline.
- Aria selects a color from a fixed palette, then taps/clicks a section to fill it.
- If a section is blank, tapping fills it with the selected color.
- If a section already has a different color, tapping replaces it with the selected color.
- If a section already has the selected color, tapping the section again clears it back to blank/white.
- Use solid fills only. No brush texture, gradients, freehand drawing, or drag-to-paint for Version 1.
- A picture is complete when every paintable section currently has a color.
- On completion, show celebration emojis, but do not lock the picture. Aria can keep editing.
- No sounds in Version 1.

## Color Palette

- Use a fixed palette of 12 concrete square color buttons.
- No visible text labels on the color buttons.
- Do not include white in the palette because blank sections are white.
- Recommended colors:
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
- The selected color must have a clear visual outline/ring and feel obviously active.

## Home And Navigation Flow

- On launch, show a single home screen with **picture cards**, not category tiles (no Animals, Vehicles, etc.).
- Each card shows a visual preview of what Aria can color (the artwork thumbnail or a small scene preview), not a generic category label.
- Home content for Version 1:
  - **Standalone pictures** (open directly into painting):
    - Butterfly
    - Giraffe
    - House
    - Fish (one fish coloring page on the home screen)
  - **Worlds** (open into a full scene first; each card shows a **mini scene thumbnail** preview of that world):
    - Land World (thumbnail: sunny landscape preview)
    - Sea World (thumbnail: underwater preview)
- Flow for a standalone picture:
  - Home -> tap picture card -> paint picture -> back to home.
- Flow for a world:
  - Home -> tap world card -> full scene -> tap a paintable character/object -> paint it -> return to full scene -> back to home when done exploring.
- Aria should be able to go back to home and pick something else at any time.
- Choosing a standalone picture starts it fresh. No standalone progress needs to persist after navigating away.
- Worlds keep in-scene paint state only while Aria stays inside that world (see Worlds State below).

## Standalone Picture Content

Use a fixed starter set. Do not generate or swap images on each load.

### Version 1 standalone pictures

- Butterfly
- Giraffe
- House
- Fish

Butterfly, giraffe, and house are also reused as paintable characters inside Land World (same SVG assets and section IDs). The home fish uses the same fish asset as the paintable fish in Sea World.

### Picture complexity

- Each standalone picture should have about 7-10 paintable sections.
- Sections should map to recognizable parts (wings, body, roof, door, etc.).
- Keep drawings simple, toddler-friendly, and coloring-book/cartoon-like.
- Use clear dark outlines and blank white unpainted sections.

## Worlds (Land And Sea)

Worlds are interactive themed scenes: **pre-colored scenery** plus a few **paintable** characters or objects.

### Worlds concept

- A world is a single full-scene view (sky, ground, water, etc.) with fixed, natural-looking colors on background and decorative elements.
- Paintable items appear in the scene as white outlined shapes (same painting rules as standalone pictures).
- Aria taps a paintable item in the scene, paints its sections on a dedicated painting screen, then returns to the full scene.
- In the full scene, painted items show Aria's chosen colors.
- Items with at least one colored section may use simple CSS/SVG animation (walk, bob, flutter, etc.) when back in the scene.
- Pre-colored scenery and decorations are **not** tappable for painting—they are visual context only.
- The scene should not become a complex game or physics simulation.

### Worlds flow

- Home -> tap Land World or Sea World -> full scene.
- Tap a paintable item in the scene -> item painting screen (same palette and fill/toggle behavior).
- Tap a globe/world button -> return to full scene.
- The item appears colored in the scene and may animate if at least one section is colored.
- Aria can reselect any paintable item, including partially or fully colored items, and continue editing.
- If all sections of an item are cleared, it returns to uncolored/non-animated state in the scene.
- Back from the full scene returns to home.

### Worlds state

- Store world state only while Aria remains inside that selected world.
- If she leaves a world (back to home) and enters it again later, that world starts fresh.
- No state should survive page reloads or app restarts.

### Land World

A sunny land/outdoor scene.

**Paintable (reuse standalone SVGs where noted):**

- Butterfly (same asset as home)
- Giraffe (same asset as home)
- House (same asset as home)

**Pre-colored (fixed in SVG, natural colors, not paintable):**

- Background scenery: sky, clouds, hills or grass, sun, etc.
- A **windy road** (gray asphalt with simple lane markings, curved through the scene—already colored, not paintable)

Land World should feel like the standalone characters live in one place together. Layout positions them beside or on the windy road with scenery behind and around them.

### Sea World

An underwater scene.

**Paintable (dedicated sea creature SVGs, white sections):**

- Fish (one paintable fish—the same asset as the home coloring fish)
- Dolphin
- Crab
- Whale

**Pre-colored (fixed in SVG, natural colors, not paintable):**

- Ocean water (blues/teals)
- Seaweed, coral, rocks, or bubbles as scene dressing
- Small decorative creatures (e.g. tiny fish, starfish, jellyfish silhouettes) that are already colored and not meant to be edited

Sea World should read clearly as underwater: colored environment first, with a few large friendly creatures Aria can color.

### Worlds complexity

- Each world has about 4-6 paintable items (Land: 3; Sea: 4–5 if two fish).
- Each paintable item should have about 5-10 paintable sections.
- Unpainted items in the scene use clear white fills and dark outlines so Aria knows what she can tap.

## Pre-Colored Vs Paintable Art

- **Paintable** assets use `.paint-section` (or equivalent) with `fill="#fff"` and strokes; section IDs match catalog data.
- **Pre-colored** scene layers use fixed hex fills in the scene SVG (or separate non-interactive layers). They must not respond to the palette or appear in fill state.
- Reuse the same butterfly, giraffe, and house definitions for standalone mode and Land World component mode.

## Download / Export

- Provide a download button for the current artwork.
- Export as PNG.
- The PNG should include the artwork and the date on a white background.
- For standalone pictures, download is allowed once at least one section is colored.
- For worlds, download the **full scene** (pre-colored scenery + Aria's colors on paintable items) once at least one paintable section in that world is colored.
- If nothing is colored yet, hide or disable the download button.
- Download does not require the picture/world to be complete.

## Out Of Scope For Version 1 (removed from earlier draft)

- Category navigation (Animals, Vehicles, Shapes & Objects, Nature & Food).
- Large picture libraries (vehicles, food, stars, etc.) unless added in a future version.
- More than two worlds (no Jungle Safari, Busy Street, Farm Day, Space Trip, etc.).
- Parent dashboard, accounts, backend, analytics, cloud save, persistent progress.
- Runtime or network image generation.
- Freehand drawing, brush sizes, textures, sounds.
- Complex games/physics inside worlds.

## Implementation Guidance For Future Agents

- Use reusable drawing data/components instead of one-off implementations.
- Define paintable art as checked-in SVG with stable section IDs; define world scenes as composed SVG (or layered groups) with separate pre-colored and paintable layers.
- Keep painting state in memory.
- Share fill/toggle/recolor logic across standalone pictures and world items.
- Share palette rendering across all painting screens.
- Reuse butterfly, giraffe, and house SVGs on the home screen and inside Land World.
- Create dedicated SVGs for Sea World paintables (fish, dolphin, crab, whale) and for each world's pre-colored scene art.
- Keep rendering fast and deterministic.
- Avoid dependencies unless they materially simplify PNG export or SVG rendering.

## Acceptance Criteria

- The app opens to a home screen of **picture/world cards** (butterfly, giraffe, house, fish, Land World, Sea World)—no category tiles; Land World and Sea World cards show mini scene thumbnails.
- Each standalone picture can be painted section by section from its card.
- Selected color is visually obvious.
- Tapping same-color section clears it; tapping with a different selected color recolors it.
- Completion triggers celebration emojis and does not lock editing.
- Land World shows pre-colored land scenery and road; butterfly, giraffe, and house are paintable in the scene and match standalone art.
- Sea World shows pre-colored ocean/scenery and small pre-colored creatures; fish, dolphin, crab, and whale are paintable.
- Worlds support full scene, tap-to-paint item, globe return, in-world remembered state, and simple animation for colored items.
- Leaving a world and re-entering starts that world fresh.
- Download is disabled until at least one section is colored; PNG includes artwork and date on white background (world download captures the full scene).
- No network image generation or runtime art generation.
- App is responsive and usable on iPhone, iPad, laptop, and desktop.
