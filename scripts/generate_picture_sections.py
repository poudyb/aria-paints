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
        detect_white = is_white

    n, labels, stats, _ = cv2.connectedComponentsWithStats(detect_white.astype(np.uint8))
    regions = []
    background = np.zeros((height, width), bool)
    for i in range(1, n):
        x, y, bw, bh, area = stats[i]
        if x == 0 or y == 0 or x + bw >= width or y + bh >= height:
            background |= labels == i
        elif area >= MIN_REGION_AREA:
            regions.append((int(area), i))
    regions.sort(reverse=True)  # big regions first so small ones draw on top

    section_ids: list[str] = []
    paths: list[str] = []
    for order, (_, comp) in enumerate(regions, start=1):
        # Prefix with the picture id: several pictures can be in the DOM at
        # once (home previews), and ids must be document-unique.
        section_id = f"{picture}-shape{order:02d}"
        mask = (labels == comp).astype(np.uint8) * 255
        # A section may only expand over outline pixels: every white pixel
        # that isn't its own (background, other sections, sub-threshold
        # slivers) is off limits.
        forbidden = detect_white & (labels != comp)
        expanded = expand_under_outline(mask, is_white, forbidden)
        contours, _ = cv2.findContours(expanded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        keep = [c for c in contours if cv2.contourArea(c) >= 25]
        if not keep:
            continue
        d = " ".join(contour_path(c) for c in keep)
        section_ids.append(section_id)
        paths.append(f'  <path id="{section_id}" class="paint-section" fill="#fff" d="{d}"/>')

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
    replacement = (
        f"{picture}: {{\n"
        f"    name: '{display_name}',\n"
        f"    viewBox: '0 0 {width} {height}',\n"
        f"    sections: [\n      {sections_js}\n    ]\n"
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
