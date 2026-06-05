#!/usr/bin/env python3
"""Generate wing paint-section paths for butterfly.svg from butterfly-art.png."""

from __future__ import annotations

import re
from collections import deque
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PNG = ROOT / "assets" / "pictures" / "butterfly-art.png"
SVG = ROOT / "assets" / "pictures" / "butterfly.svg"


def find_interior(is_white: np.ndarray, y_sl: slice, x_sl: slice) -> tuple[np.ndarray, int, int]:
    white = is_white[y_sl, x_sl].copy().astype(np.uint8) * 255
    h_q, w_q = white.shape
    outside = np.zeros((h_q, w_q), dtype=np.uint8)
    q: deque[tuple[int, int]] = deque()
    for r, c in ((0, 0), (0, w_q - 1), (h_q - 1, 0), (h_q - 1, w_q - 1)):
        if white[r, c]:
            outside[r, c] = 255
            q.append((r, c))
    while q:
        r, c = q.popleft()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < h_q and 0 <= nc < w_q and white[nr, nc] and not outside[nr, nc]:
                outside[nr, nc] = 255
                q.append((nr, nc))
    interior = ((white > 0) & (outside == 0)).astype(np.uint8) * 255
    return interior, x_sl.start or 0, y_sl.start or 0


def contour_path(contour: np.ndarray, x_off: int, y_off: int, epsilon: float = 0.008) -> str:
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon * peri, True)
    pts = [(float(p[0][0] + x_off), float(p[0][1] + y_off)) for p in approx]
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def main() -> None:
    arr = np.array(Image.open(PNG))
    rgb = arr[:, :, :3]
    is_white = (rgb[:, :, 0] > 240) & (rgb[:, :, 1] > 240) & (rgb[:, :, 2] > 240)
    mid_x, mid_y = arr.shape[1] // 2, arr.shape[0] // 2

    wings = [
        ("wing-left-upper", slice(0, mid_y), slice(0, mid_x)),
        ("wing-left-lower", slice(mid_y, arr.shape[0]), slice(0, mid_x)),
        ("wing-right-upper", slice(0, mid_y), slice(mid_x, arr.shape[1])),
        ("wing-right-lower", slice(mid_y, arr.shape[0]), slice(mid_x, arr.shape[1])),
    ]

    paths: list[str] = []
    for wing_id, y_sl, x_sl in wings:
        interior, x_off, y_off = find_interior(is_white, y_sl, x_sl)
        contours, _ = cv2.findContours(interior, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        largest = max(contours, key=cv2.contourArea)
        d = contour_path(largest, x_off, y_off)
        paths.append(
            f'  <path id="{wing_id}" class="paint-section" fill="#fff" stroke="#bbb" '
            f'stroke-width="2" d="{d}"/>'
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
