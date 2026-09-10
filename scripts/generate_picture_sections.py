#!/usr/bin/env python3
"""Generate paint-section paths for a picture from its line-art PNG.

Every white region fully enclosed by the black line art becomes a paintable
section. Open regions (sky, ground, anything connected to the image border)
stay unpaintable. The PNG is composited on top of the fills with a multiply
blend, so outlines stay black over painted sections.

Usage: generate_picture_sections.py [picture]   (default: giraffe)

Writes assets/pictures/<picture>.svg and updates the picture's viewBox and
sections list in data/catalog.js.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MIN_REGION_AREA = 100
DISPLAY_NAMES = {"christmasTree": "Christmas Tree"}
# Some line art has hairline gaps in its outlines that would leak shapes into
# the background; close them by thickening the lines this many pixels during
# region detection (display art is untouched).
GAP_CLOSE = {"turtle": 5}
# Pictures where the image edge acts as an invisible boundary: open regions
# that run off the edge (sky, ground, mountains) become paintable instead of
# being treated as background.
BORDER_FENCE = {"giraffe"}
# Pictures that also split open background into horizontal bands using
# invisible dividers placed in white gaps between horizon lines. (The current
# giraffe scene has no horizon lines, so its open background stays one region.)
BACKGROUND_DIVIDERS: set[str] = set()
# Pictures that get a child-friendly `neighbors` map in the catalog: tapping a
# section also paints its neighbors, so imprecise taps color 2-3 patches.
NEIGHBOR_PICTURES = {"giraffe"}
MAX_NEIGHBORS = 2
# Neighbors must be reasonably close (fraction of the image diagonal) and,
# preferably, of similar size (spots pair with spots, fronds with fronds).
NEIGHBOR_DISTANCE_FRAC = 0.15
NEIGHBOR_AREA_RATIO = 8.0


def contour_path(contour: np.ndarray) -> str:
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, max(0.5, 0.0004 * peri), True)
    pts = [(float(p[0][0]), float(p[0][1])) for p in approx]
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def expand_under_outline(
    region: np.ndarray, is_white: np.ndarray, forbidden: np.ndarray
) -> np.ndarray:
    """Extend a region halfway under the black outline so fills reach it with
    no white sliver, clipped so it never covers background or other regions."""
    outline = (~is_white).astype(np.uint8) * 255
    dilated = cv2.dilate(region, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
    expanded = cv2.bitwise_or(region, cv2.bitwise_and(dilated, outline))
    expanded = cv2.dilate(expanded, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    # Clear a 1px buffer around forbidden pixels: traced polygons can stray
    # about a pixel outside the raster mask when rasterized again.
    forbidden_grown = cv2.dilate(
        forbidden.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    )
    expanded[forbidden_grown > 0] = 0
    return expanded


def foreground_mask(is_white: np.ndarray) -> np.ndarray:
    """Enclosed white regions in the original art (not connected to the border)."""
    n, labels, stats, _ = cv2.connectedComponentsWithStats(is_white.astype(np.uint8))
    h, w = is_white.shape
    mask = np.zeros((h, w), bool)
    for i in range(1, n):
        x, y, bw, bh, area = stats[i]
        border = x == 0 or y == 0 or x + bw >= w or y + bh >= h
        if not border and area >= MIN_REGION_AREA:
            mask |= labels == i
    return mask


def horizon_divider_rows(is_white: np.ndarray) -> list[int]:
    """Pick y-rows in white gaps between strong horizontal black lines."""
    h = is_white.shape[0]
    black = ~is_white
    bands: list[tuple[int, int]] = []
    start = None
    for y in range(h):
        if black[y, :].mean() > 0.25:
            if start is None:
                start = y
        elif start is not None:
            bands.append((start, y - 1))
            start = None
    if start is not None:
        bands.append((start, h - 1))

    dividers: list[int] = []
    edges = [0] + [e for _, e in bands] + [h - 1]
    for lo, hi in zip(edges, edges[1:]):
        gap_start = lo + 1
        gap_end = hi - 1
        if gap_end - gap_start >= 40:
            dividers.append((gap_start + gap_end) // 2)
    return dividers


def horizon_band_bounds(is_white: np.ndarray) -> list[tuple[int, int]]:
    """Horizontal y-ranges that split open background at horizon gaps."""
    h = is_white.shape[0]
    dividers = horizon_divider_rows(is_white)
    bounds = [0, *dividers, h]
    return [(bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1)]


def collect_regions(
    picture: str,
    detect_white: np.ndarray,
    is_white: np.ndarray,
    foreground: np.ndarray | None,
) -> list[tuple[int, np.ndarray]]:
    """Return paintable regions as (area, mask) pairs, largest first."""
    height, width = is_white.shape
    regions: list[tuple[int, np.ndarray]] = []

    if picture in BACKGROUND_DIVIDERS and foreground is not None:
        # Foreground shapes (giraffe, sun, cloud, spots) stay as-is.
        n, labels, stats, _ = cv2.connectedComponentsWithStats(is_white.astype(np.uint8))
        for i in range(1, n):
            x, y, bw, bh, area = stats[i]
            border = x == 0 or y == 0 or x + bw >= width or y + bh >= height
            if not border and area >= MIN_REGION_AREA:
                mask = (labels == i).astype(np.uint8) * 255
                regions.append((int(area), mask))

        # Open background is split into horizontal bands at horizon gaps.
        background = detect_white & ~foreground
        for y0, y1 in horizon_band_bounds(is_white):
            band = background[y0:y1, :].astype(np.uint8)
            n, labels, stats, _ = cv2.connectedComponentsWithStats(band)
            for i in range(1, n):
                area = stats[i, cv2.CC_STAT_AREA]
                if area < MIN_REGION_AREA:
                    continue
                full = np.zeros((height, width), np.uint8)
                band_mask = (labels == i).astype(np.uint8) * 255
                full[y0:y1, :] = np.maximum(full[y0:y1, :], band_mask)
                regions.append((int(area), full))
    else:
        n, labels, stats, _ = cv2.connectedComponentsWithStats(detect_white.astype(np.uint8))
        for i in range(1, n):
            x, y, bw, bh, area = stats[i]
            border = x == 0 or y == 0 or x + bw >= width or y + bh >= height
            if not border and area >= MIN_REGION_AREA:
                mask = (labels == i).astype(np.uint8) * 255
                regions.append((int(area), mask))

    regions.sort(key=lambda item: -item[0])
    return regions


def compute_neighbors(
    kept: list[tuple[str, int, float, float, bool]], width: int, height: int
) -> dict[str, list[str]]:
    """Map each section to up to MAX_NEIGHBORS nearby sections to co-paint.

    kept holds (section_id, area, cx, cy, is_background). Background sections
    (open sky/ground bands) neither get nor become neighbors. Same-scale
    sections are preferred so spots group with spots and fronds with fronds;
    if a section has no similar-sized peer nearby (e.g. the sun disc, the
    giraffe body), it falls back to its nearest small neighbors.
    """
    max_dist = NEIGHBOR_DISTANCE_FRAC * float(np.hypot(width, height))
    neighbors: dict[str, list[str]] = {}
    for sid, area, cx, cy, is_bg in kept:
        if is_bg:
            continue
        near: list[tuple[float, float, str]] = []
        for osid, oarea, ocx, ocy, ois_bg in kept:
            if ois_bg or osid == sid:
                continue
            dist = float(np.hypot(cx - ocx, cy - ocy))
            if dist > max_dist:
                continue
            ratio = max(area, oarea) / min(area, oarea)
            near.append((dist, ratio, osid))
        similar = sorted(t for t in near if t[1] <= NEIGHBOR_AREA_RATIO)
        picks = similar[:MAX_NEIGHBORS] or sorted(near)[:MAX_NEIGHBORS]
        if picks:
            neighbors[sid] = [osid for _, _, osid in picks]
    return neighbors


def main() -> None:
    picture = sys.argv[1] if len(sys.argv) > 1 else "giraffe"
    png = ROOT / "assets" / "pictures" / f"{picture}-art.png"
    svg_path = ROOT / "assets" / "pictures" / f"{picture}.svg"
    catalog_path = ROOT / "data" / "catalog.js"

    arr = np.array(Image.open(png).convert("RGB"))
    height, width = arr.shape[:2]
    is_white = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)

    gap = GAP_CLOSE.get(picture, 1)
    if gap > 1:
        thick = cv2.dilate(
            (~is_white).astype(np.uint8),
            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (gap, gap)),
        )
        detect_white = thick == 0
    else:
        detect_white = is_white.copy()

    if picture in BORDER_FENCE:
        detect_white[0, :] = detect_white[-1, :] = False
        detect_white[:, 0] = detect_white[:, -1] = False

    needs_foreground = picture in BACKGROUND_DIVIDERS or picture in NEIGHBOR_PICTURES
    foreground = foreground_mask(is_white) if needs_foreground else None

    regions = collect_regions(picture, detect_white, is_white, foreground)

    section_ids: list[str] = []
    paths: list[str] = []
    kept: list[tuple[str, int, float, float, bool]] = []
    region_masks = [mask for _, mask in regions]
    for order, (area, mask) in enumerate(regions, start=1):
        # Prefix with the picture id: several pictures can be in the DOM at
        # once (home previews), and ids must be document-unique.
        section_id = f"{picture}-shape{order:02d}"
        forbidden = np.zeros((height, width), bool)
        for other in region_masks:
            if other is not mask:
                forbidden |= other > 0
        expanded = expand_under_outline(mask, is_white, forbidden)
        contours, _ = cv2.findContours(expanded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        keep = [c for c in contours if cv2.contourArea(c) >= 25]
        if not keep:
            continue
        d = " ".join(contour_path(c) for c in keep)
        section_ids.append(section_id)
        paths.append(f'  <path id="{section_id}" class="paint-section" fill="#fff" d="{d}"/>')
        ys, xs = np.nonzero(mask)
        is_bg = foreground is not None and not bool(foreground[mask > 0].any())
        kept.append((section_id, area, float(xs.mean()), float(ys.mean()), is_bg))

    display_name = DISPLAY_NAMES.get(picture, picture.capitalize())
    art_href = f"assets/pictures/{picture}-art.png"
    svg = "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {width} {height}" aria-label="{display_name}">',
            *paths,
            f'  <image class="{picture}-art" href="{art_href}" xlink:href="{art_href}"',
            f'    x="0" y="0" width="{width}" height="{height}" pointer-events="none"/>',
            "</svg>",
            "",
        ]
    )
    svg_path.write_text(svg)

    catalog = catalog_path.read_text()
    sections_js = ",\n      ".join(
        ", ".join(f"'{s}'" for s in section_ids[i : i + 8])
        for i in range(0, len(section_ids), 8)
    )
    neighbors_js = ""
    if picture in NEIGHBOR_PICTURES:
        neighbor_map = compute_neighbors(kept, width, height)
        entries = ",\n      ".join(
            f"'{sid}': [{', '.join(chr(39) + n + chr(39) for n in ids)}]"
            for sid, ids in neighbor_map.items()
        )
        neighbors_js = f",\n    neighbors: {{\n      {entries}\n    }}"
    replacement = (
        f"{picture}: {{\n"
        f"    name: '{display_name}',\n"
        f"    viewBox: '0 0 {width} {height}',\n"
        f"    sections: [\n      {sections_js}\n    ]{neighbors_js}\n"
        f"  }}"
    )
    pattern = re.compile(rf"{picture}: \{{.*?\n  \}}", re.S)
    if not pattern.search(catalog):
        raise SystemExit(f"Could not find {picture!r} entry in {catalog_path}")
    catalog_path.write_text(pattern.sub(replacement.replace("\\", "\\\\"), catalog, count=1))

    print(f"Wrote {svg_path.relative_to(ROOT)} with {len(section_ids)} sections")
    print(f"Updated {catalog_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
