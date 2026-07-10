#!/usr/bin/env python3
"""Generate wing paint-section paths for butterfly.svg from butterfly-art.png."""

from __future__ import annotations

import re
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PNG = ROOT / "assets" / "pictures" / "butterfly-art.png"
SVG = ROOT / "assets" / "pictures" / "butterfly.svg"


def background_mask(is_white: np.ndarray) -> np.ndarray:
    """White pixels connected to the image border (everything outside the butterfly)."""
    labels = cv2.connectedComponents(is_white.astype(np.uint8))[1]
    border = set(labels[0, :]) | set(labels[-1, :]) | set(labels[:, 0]) | set(labels[:, -1])
    border.discard(0)
    return np.isin(labels, list(border)) & is_white


def expand_under_outline(
    wing: np.ndarray, is_white: np.ndarray, background: np.ndarray, others: np.ndarray
) -> np.ndarray:
    """Expand a wing region halfway under the black outline so fills reach the
    outline with no white sliver. Expansion is clipped to non-white (outline)
    pixels, then against the exterior background and the other wings'
    interiors, so color never bleeds outside the butterfly or into a
    neighboring wing. The art PNG is composited on top with multiply blend,
    keeping the outline black over the extended fill."""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
    dilated = cv2.dilate(wing, kernel)
    outline = (~is_white).astype(np.uint8) * 255
    expanded = cv2.bitwise_or(wing, cv2.bitwise_and(dilated, outline))
    expanded[background] = 0
    expanded[others > 0] = 0
    return expanded


def contour_path(contour: np.ndarray, x_off: int, y_off: int, epsilon: float = 0.0004) -> str:
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon * peri, True)
    pts = [(float(p[0][0] + x_off), float(p[0][1] + y_off)) for p in approx]
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def main() -> None:
    arr = np.array(Image.open(PNG))
    rgb = arr[:, :, :3]
    is_white = (rgb[:, :, 0] > 240) & (rgb[:, :, 1] > 240) & (rgb[:, :, 2] > 240)
    background = background_mask(is_white)
    mid_x, mid_y = arr.shape[1] // 2, arr.shape[0] // 2

    # Each wing is its own white region in the art, fully separated by the
    # black outlines, so the wing boundaries follow the drawing exactly
    # (no arbitrary quadrant cut lines). Components are assigned to wings by
    # centroid position relative to the image center.
    interior_all = (is_white & ~background).astype(np.uint8)
    n, labels, stats, centroids = cv2.connectedComponentsWithStats(interior_all)
    masks: dict[str, np.ndarray] = {}
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] < 25:
            continue
        cx, cy = centroids[i]
        wing_id = (
            "wing-" + ("left" if cx < mid_x else "right")
            + "-" + ("upper" if cy < mid_y else "lower")
        )
        mask = masks.setdefault(wing_id, np.zeros(interior_all.shape, np.uint8))
        mask[labels == i] = 255

    expected = ["wing-left-upper", "wing-left-lower", "wing-right-upper", "wing-right-lower"]
    missing = [w for w in expected if w not in masks]
    if missing:
        raise SystemExit(f"Wing regions not found in art: {missing}")

    paths: list[str] = []
    for wing_id in expected:
        others = np.zeros(interior_all.shape, np.uint8)
        for other_id, other_mask in masks.items():
            if other_id != wing_id:
                others = cv2.bitwise_or(others, other_mask)
        interior = expand_under_outline(masks[wing_id], is_white, background, others)
        contours, _ = cv2.findContours(interior, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        keep = [c for c in contours if cv2.contourArea(c) >= 25]
        d = " ".join(contour_path(c, 0, 0) for c in keep)
        # No stroke: wing edges sit fully under the black art outline.
        paths.append(
            f'  <path id="{wing_id}" class="paint-section" fill="#fff" d="{d}"/>'
        )

    svg = SVG.read_text()
    block = "\n".join(paths)
    svg = re.sub(
        r"<svg[^>]*>\n(?:  <path id=\"wing-.*?\n)*",
        lambda m: m.group(0).split("\n")[0] + "\n" + block + "\n",
        svg,
        count=1,
    )
    if "wing-left-upper" not in svg:
        svg = svg.replace(
            '<svg xmlns="http://www.w3.org/2000/svg"',
            '<svg xmlns="http://www.w3.org/2000/svg"\n' + block,
            1,
        )
    SVG.write_text(svg)
    print(f"Updated {SVG.relative_to(ROOT)} with {len(paths)} wing paths")


if __name__ == "__main__":
    main()
