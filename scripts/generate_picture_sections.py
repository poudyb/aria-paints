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
DISPLAY_NAMES = {"christmasTree": "Christmas Tree", "seaworld": "Sea World"}
# Some line art has hairline gaps in its outlines that would leak shapes into
# the background; close them by thickening the lines this many pixels during
# region detection (display art is untouched).
GAP_CLOSE = {"turtle": 5, "seaworld": 5}
# Pictures where the image edge acts as an invisible boundary: open regions
# that run off the edge (sky, ground, mountains) become paintable instead of
# being treated as background.
BORDER_FENCE = {"giraffe"}
# Pictures that also split open background into horizontal bands using
# invisible dividers placed in white gaps between horizon lines. (The current
# giraffe scene has no horizon lines, so its open background stays one region.)
BACKGROUND_DIVIDERS: set[str] = set()
# Line art on a pre-colored background (seaworld waves): enclosed interiors
# are not white, so flood-fill them to white in the overlay PNG, then trace
# as usual. Open background stays unpaintable.
WHITE_FILL_ENCLOSED = {"seaworld"}
INK_THRESH = {"seaworld": 55}
# Extra local-contrast ink: navy outlines on blue water are not always < thresh.
LOCAL_INK = {"seaworld"}
# Static object boxes (art-pixel coords). Related patches merge into one
# paint-section at generate time — no runtime proximity neighbor picking.
CLUSTER_DILATE = {"seaworld": 21}
HOUSE_SUN_BOX = (70, 10, 220, 160)
HOUSE_BOW_BOX = (370, 0, 540, 140)
HOUSE_FLOWER_BOX = (0, 280, 230, 574)
HOUSE_BUILDING_BOX = (250, 140, 680, 574)
HOUSE_PALM_BOX = (700, 0, 1024, 574)
GIRAFFE_SUN_BOX = (90, 20, 230, 170)
GIRAFFE_FLOWER_BOX = (0, 300, 230, 618)
GIRAFFE_ANIMAL_BOX = (300, 0, 650, 618)
GIRAFFE_PALM_BOX = (650, 0, 1024, 618)
# Sea World: each animal is one paint-section. Boxes are in art-pixel coords
# (794x794) so nearby creatures (octopus/fish, two whales/dolphins) stay apart.
SEAWORLD_OBJECT_BOXES = (
    (1, (0, 0, 300, 290)),       # leaping dolphin + splash (top-left)
    (2, (300, 0, 794, 290)),     # large whale + spout (top-right)
    (3, (0, 300, 185, 510)),     # octopus (mid-left)
    (4, (185, 300, 380, 510)),   # angelfish (left-center)
    (5, (400, 300, 660, 520)),   # small whale + spout (center-right)
    (6, (660, 300, 794, 540)),   # small leaping dolphin (right)
    (7, (180, 520, 450, 730)),   # angelfish (lower-left)
    (8, (555, 560, 760, 740)),   # crab (body/claws/legs; not coral water)
)
SEAWORLD_MIN_REGION_AREA = 80
SEAWORLD_CRAB_CLUSTER = 8


def contour_path(contour: np.ndarray) -> str:
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, max(0.5, 0.0004 * peri), True)
    pts = [(float(p[0][0]), float(p[0][1])) for p in approx]
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def ink_mask(arr: np.ndarray, thresh: int, picture: str = "") -> np.ndarray:
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    ink = gray < thresh
    if picture in LOCAL_INK:
        blur = cv2.GaussianBlur(gray, (21, 21), 0)
        local = ((blur.astype(np.int16) - gray.astype(np.int16)) > 18) & (gray < 130)
        ink = ink | local
    return ink.astype(np.uint8) * 255


def enclosed_interiors(ink: np.ndarray, gap: int) -> np.ndarray:
    """Pixels inside closed outlines, not connected to the image border."""
    thick = ink
    if gap > 1:
        thick = cv2.dilate(ink, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (gap, gap)))
    pad = cv2.copyMakeBorder(thick, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    ph, pw = pad.shape
    mask = np.zeros((ph + 2, pw + 2), np.uint8)
    cv2.floodFill(pad, mask, (0, 0), 128)
    background = pad[1:-1, 1:-1] == 128
    return (thick == 0) & (~background)


def white_fill_enclosed(
    arr: np.ndarray, thresh: int, gap: int, picture: str = ""
) -> tuple[np.ndarray, np.ndarray]:
    """Paint enclosed interiors white so multiply-blend overlays work like giraffe."""
    ink = ink_mask(arr, thresh, picture)
    interiors = enclosed_interiors(ink, gap)
    # Grow white up to the real ink, not into the colored background.
    grown = cv2.dilate(
        interiors.astype(np.uint8) * 255,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)),
    )
    fill = (grown > 0) & (ink == 0)
    out = arr.copy()
    out[fill] = (255, 255, 255)
    waves = (~fill) & (ink == 0)
    return out, waves


def assign_clusters(masks: list[np.ndarray], dilate_px: int) -> list[int]:
    """Group region masks that belong to the same object (one animal)."""
    if not masks:
        return []
    height, width = masks[0].shape
    union = np.zeros((height, width), np.uint8)
    for mask in masks:
        union = np.maximum(union, (mask > 0).astype(np.uint8) * 255)
    dilated = cv2.dilate(
        union, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dilate_px, dilate_px))
    )
    _, labels = cv2.connectedComponents(dilated)
    clusters: list[int] = []
    for mask in masks:
        labs, counts = np.unique(labels[mask > 0], return_counts=True)
        best = 0
        best_count = -1
        for lab, count in zip(labs, counts):
            if lab == 0:
                continue
            if int(count) > best_count:
                best = int(lab)
                best_count = int(count)
        clusters.append(best)
    return clusters


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


def _centroid(mask: np.ndarray) -> tuple[float, float]:
    ys, xs = np.nonzero(mask)
    return float(xs.mean()), float(ys.mean())


def _in_box(cx: float, cy: float, box: tuple[int, int, int, int]) -> bool:
    x0, y0, x1, y1 = box
    return x0 <= cx <= x1 and y0 <= cy <= y1


def seaworld_cluster(cx: float, cy: float) -> int:
    for cluster, box in SEAWORLD_OBJECT_BOXES:
        if _in_box(cx, cy, box):
            return cluster
    return 0


def erase_house_sun_box(arr: np.ndarray) -> np.ndarray:
    """Whiten the square frame around the house sun so it is not visible."""
    is_white = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(is_white.astype(np.uint8))
    height, width = is_white.shape
    box_cx = (HOUSE_SUN_BOX[0] + HOUSE_SUN_BOX[2]) / 2.0
    box_cy = (HOUSE_SUN_BOX[1] + HOUSE_SUN_BOX[3]) / 2.0

    sun_protect = np.zeros((height, width), bool)
    interiors: list[tuple[float, np.ndarray]] = []
    for i in range(1, n):
        x, y, bw, bh, area = stats[i]
        border = x == 0 or y == 0 or x + bw >= width or y + bh >= height
        if border or area < MIN_REGION_AREA:
            continue
        mask = labels == i
        ys, xs = np.nonzero(mask)
        cx, cy = float(xs.mean()), float(ys.mean())
        if not _in_box(cx, cy, HOUSE_SUN_BOX):
            continue
        if area > 1500:
            dist = float(np.hypot(cx - box_cx, cy - box_cy))
            interiors.append((dist, mask))
        else:
            sun_protect |= mask

    interiors.sort(key=lambda item: item[0])
    dropped = np.zeros((height, width), bool)
    if interiors:
        sun_protect |= interiors[0][1]
        for _, mask in interiors[1:]:
            dropped |= mask
    if not dropped.any():
        return arr

    ring = cv2.dilate(
        dropped.astype(np.uint8) * 255,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)),
    )
    sun_grown = cv2.dilate(
        sun_protect.astype(np.uint8) * 255,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)),
    )
    erase = (ring > 0) & (sun_grown == 0) & (~is_white)
    out = arr.copy()
    out[erase] = (255, 255, 255)
    return out


def _named_groups(
    groups: dict[str, list[np.ndarray]],
    dropped: list[np.ndarray],
) -> tuple[list[tuple[int, np.ndarray | list[np.ndarray]]], list[np.ndarray]]:
    merged: list[tuple[int, np.ndarray | list[np.ndarray]]] = []
    for masks in groups.values():
        if not masks:
            continue
        total = int(sum(int((mask > 0).sum()) for mask in masks))
        merged.append((total, masks if len(masks) > 1 else masks[0]))
    merged.sort(key=lambda item: -item[0])
    return merged, dropped


def group_house_regions(
    regions: list[tuple[int, np.ndarray]],
) -> tuple[list[tuple[int, np.ndarray | list[np.ndarray]]], list[np.ndarray]]:
    """Merge each house object into one static paint-section."""
    box_cx = (HOUSE_SUN_BOX[0] + HOUSE_SUN_BOX[2]) / 2.0
    box_cy = (HOUSE_SUN_BOX[1] + HOUSE_SUN_BOX[3]) / 2.0
    groups: dict[str, list[np.ndarray]] = {
        "sun": [],
        "bow": [],
        "flower-head": [],
        "flower-stem": [],
        "wall": [],
        "roof": [],
        "door": [],
        "chimney": [],
        "windows": [],
        "palm-fronds": [],
        "palm-trunk": [],
    }
    dropped: list[np.ndarray] = []
    sun_large: list[tuple[float, np.ndarray]] = []
    sun_rays: list[np.ndarray] = []
    building: list[tuple[int, np.ndarray, float, float]] = []

    for area, mask in regions:
        cx, cy = _centroid(mask)
        if _in_box(cx, cy, HOUSE_SUN_BOX):
            if area > 1500:
                dist = float(np.hypot(cx - box_cx, cy - box_cy))
                sun_large.append((dist, mask))
            else:
                sun_rays.append(mask)
        elif _in_box(cx, cy, HOUSE_BOW_BOX):
            groups["bow"].append(mask)
        elif _in_box(cx, cy, HOUSE_FLOWER_BOX):
            if cy > 430:
                groups["flower-stem"].append(mask)
            else:
                groups["flower-head"].append(mask)
        elif _in_box(cx, cy, HOUSE_BUILDING_BOX):
            building.append((area, mask, cx, cy))
        elif _in_box(cx, cy, HOUSE_PALM_BOX):
            if 855 <= cx <= 910 and cy > 250:
                groups["palm-trunk"].append(mask)
            else:
                groups["palm-fronds"].append(mask)
        else:
            dropped.append(mask)

    sun_large.sort(key=lambda item: item[0])
    if sun_large:
        groups["sun"].append(sun_large[0][1])
        for _, extra in sun_large[1:]:
            dropped.append(extra)
    groups["sun"].extend(sun_rays)

    if building:
        building.sort(key=lambda item: -item[0])
        groups["wall"].append(building[0][1])
        for area, mask, cx, cy in building[1:]:
            if cx > 555 and cy < 285:
                groups["chimney"].append(mask)
            elif area > 5000 and cy < 350:
                groups["roof"].append(mask)
            elif area > 5000:
                groups["door"].append(mask)
            else:
                groups["windows"].append(mask)

    return _named_groups(groups, dropped)


def group_giraffe_regions(
    regions: list[tuple[int, np.ndarray]],
) -> tuple[list[tuple[int, np.ndarray | list[np.ndarray]]], list[np.ndarray]]:
    """Merge each giraffe-scene object into one static paint-section."""
    groups: dict[str, list[np.ndarray]] = {
        "sky": [],
        "sun": [],
        "flower-head": [],
        "flower-stem": [],
        "body": [],
        "spots": [],
        "palm-fronds": [],
        "palm-trunk": [],
    }
    dropped: list[np.ndarray] = []
    animal: list[tuple[int, np.ndarray, float, float]] = []
    height = width = None

    for area, mask in regions:
        if height is None:
            height, width = mask.shape
        cx, cy = _centroid(mask)
        ys, xs = np.nonzero(mask)
        span_w = int(xs.max() - xs.min())
        span_h = int(ys.max() - ys.min())
        if span_w > 0.8 * width and span_h > 0.8 * height:
            groups["sky"].append(mask)
        elif _in_box(cx, cy, GIRAFFE_SUN_BOX):
            groups["sun"].append(mask)
        elif _in_box(cx, cy, GIRAFFE_FLOWER_BOX):
            if cy > 460:
                groups["flower-stem"].append(mask)
            else:
                groups["flower-head"].append(mask)
        elif _in_box(cx, cy, GIRAFFE_PALM_BOX):
            if 800 <= cx <= 860 and cy > 240:
                groups["palm-trunk"].append(mask)
            else:
                groups["palm-fronds"].append(mask)
        elif _in_box(cx, cy, GIRAFFE_ANIMAL_BOX):
            animal.append((area, mask, cx, cy))
        else:
            dropped.append(mask)

    if animal:
        animal.sort(key=lambda item: -item[0])
        groups["body"].append(animal[0][1])
        for area, mask, _cx, cy in animal[1:]:
            if area > 1500 or cy > 555 or cy < 90:
                groups["body"].append(mask)
            else:
                groups["spots"].append(mask)

    return _named_groups(groups, dropped)


def group_seaworld_regions(
    regions: list[tuple[int, np.ndarray]],
) -> tuple[list[tuple[int, np.ndarray | list[np.ndarray]]], list[np.ndarray]]:
    """Merge every patch of each animal into one paint-section.

    Water, coral, bubbles, and seaweed are open background (or leftover
    pockets outside the animal boxes) and stay unpaintable.
    """
    groups: dict[int, list[np.ndarray]] = {}
    dropped: list[np.ndarray] = []
    for area, mask in regions:
        if area < SEAWORLD_MIN_REGION_AREA:
            dropped.append(mask)
            continue
        cx, cy = _centroid(mask)
        cluster = seaworld_cluster(cx, cy)
        if not cluster:
            dropped.append(mask)
            continue
        groups.setdefault(cluster, []).append(mask)

    # Crab sits on coral: keep only the animal's connected parts, not
    # leftover water pockets whose centroids still fall in the box.
    if SEAWORLD_CRAB_CLUSTER in groups:
        masks = groups[SEAWORLD_CRAB_CLUSTER]
        labs = assign_clusters(masks, CLUSTER_DILATE["seaworld"])
        by_lab: dict[int, list[np.ndarray]] = {}
        for mask, lab in zip(masks, labs):
            by_lab.setdefault(lab, []).append(mask)
        best = max(
            by_lab,
            key=lambda lab: sum(int((m > 0).sum()) for m in by_lab[lab]),
        )
        for lab, extra in by_lab.items():
            if lab != best:
                dropped.extend(extra)
        groups[SEAWORLD_CRAB_CLUSTER] = by_lab[best]

    merged: list[tuple[int, np.ndarray | list[np.ndarray]]] = []
    for cluster in sorted(groups):
        masks = groups[cluster]
        total = int(sum(int((m > 0).sum()) for m in masks))
        merged.append((total, masks if len(masks) > 1 else masks[0]))
    merged.sort(key=lambda item: -item[0])
    return merged, dropped


def _region_union(mask_or_masks: np.ndarray | list[np.ndarray]) -> np.ndarray:
    masks = mask_or_masks if isinstance(mask_or_masks, list) else [mask_or_masks]
    union = masks[0].copy()
    for mask in masks[1:]:
        union = np.maximum(union, mask)
    return union


def main() -> None:
    picture = sys.argv[1] if len(sys.argv) > 1 else "giraffe"
    png = ROOT / "assets" / "pictures" / f"{picture}-art.png"
    svg_path = ROOT / "assets" / "pictures" / f"{picture}.svg"
    catalog_path = ROOT / "data" / "catalog.js"

    arr = np.array(Image.open(png).convert("RGB"))
    if picture == "house":
        arr = erase_house_sun_box(arr)
        Image.fromarray(arr).save(png)
    height, width = arr.shape[:2]
    gap = GAP_CLOSE.get(picture, 1)
    wave_forbidden = np.zeros((height, width), bool)
    interiors_detect: np.ndarray | None = None
    if picture in WHITE_FILL_ENCLOSED:
        # Trace enclosed interiors before painting a white halo. The halo
        # can bridge an animal (octopus) to border-connected wave highlights,
        # which would drop the whole body as background.
        interiors_detect = enclosed_interiors(
            ink_mask(arr, INK_THRESH[picture], picture), gap
        )
        arr, wave_forbidden = white_fill_enclosed(
            arr, INK_THRESH[picture], gap, picture
        )
        Image.fromarray(arr).save(png)

    is_white = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)

    if interiors_detect is not None:
        detect_white = interiors_detect
    elif gap > 1:
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

    needs_foreground = picture in BACKGROUND_DIVIDERS
    foreground = foreground_mask(is_white) if needs_foreground else None

    regions = collect_regions(picture, detect_white, is_white, foreground)
    dropped_masks: list[np.ndarray] = []
    if picture == "house":
        regions, dropped_masks = group_house_regions(regions)
    elif picture == "giraffe":
        regions, dropped_masks = group_giraffe_regions(regions)
    elif picture == "seaworld":
        regions, dropped_masks = group_seaworld_regions(regions)

    section_ids: list[str] = []
    paths: list[str] = []
    region_unions = [_region_union(mask) for _, mask in regions]
    for order, ((_area, mask), union) in enumerate(zip(regions, region_unions), start=1):
        # Prefix with the picture id: several pictures can be in the DOM at
        # once (home previews), and ids must be document-unique.
        section_id = f"{picture}-shape{order:02d}"
        forbidden = np.zeros((height, width), bool)
        for other in region_unions:
            if other is not union:
                forbidden |= other > 0
        for extra in dropped_masks:
            forbidden |= extra > 0
        # Never expand paint fills into the pre-colored background (waves).
        forbidden |= wave_forbidden
        submasks = mask if isinstance(mask, list) else [mask]
        path_parts: list[str] = []
        for sub in submasks:
            expanded = expand_under_outline(sub, is_white, forbidden)
            contours, _ = cv2.findContours(expanded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            path_parts.extend(contour_path(c) for c in contours if cv2.contourArea(c) >= 25)
        if not path_parts:
            continue
        d = " ".join(path_parts)
        section_ids.append(section_id)
        paths.append(f'  <path id="{section_id}" class="paint-section" fill="#fff" d="{d}"/>')

    display_name = DISPLAY_NAMES.get(picture, picture.capitalize())
    art_href = f"{picture}-art.png"
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
