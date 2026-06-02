#!/usr/bin/env python3
"""Trace coloring-page line art to paint-section SVG (viewBox 0 0 400 400)."""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import cv2
import numpy as np

VIEW = 400
STROKE = 3.5
MIN_AREA = 80  # px at trace resolution; scaled with image


def load_gray(path: Path, max_dim: int = 1200) -> tuple[np.ndarray, float]:
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise SystemExit(f"Cannot read {path}")
    h, w = img.shape
    scale = 1.0
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return img, scale


def binarize(gray: np.ndarray, invert: bool = True) -> np.ndarray:
    """White fill regions, black lines."""
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if invert:
        # line art: dark lines on white -> white regions for flood/contour fill
        bw = 255 - bw
    # close small gaps in lines
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    lines = 255 - bw
    lines = cv2.morphologyEx(lines, cv2.MORPH_CLOSE, kernel, iterations=1)
    bw = 255 - lines
    return bw


def contour_to_path(cnt: np.ndarray, sx: float, sy: float, ox: float, oy: float) -> str:
    pts = cnt.reshape(-1, 2).astype(float)
    pts[:, 0] = pts[:, 0] * sx + ox
    pts[:, 1] = pts[:, 1] * sy + oy
    parts = [f"M {pts[0,0]:.1f} {pts[0,1]:.1f}"]
    for x, y in pts[1:]:
        parts.append(f"L {x:.1f} {y:.1f}")
    parts.append("Z")
    return " ".join(parts)


def bbox_area(cnt) -> float:
    x, y, w, h = cv2.boundingRect(cnt)
    return w * h


def trace_regions(
    gray: np.ndarray,
    min_area: float,
    padding: float = 0.04,
) -> tuple[list[dict], tuple[float, float, float, float]]:
    """Return paint regions + content bounds in 400 space."""
    fill = binarize(gray)
    h, w = fill.shape
    # find enclosed white regions (coloring cells)
    contours, hierarchy = cv2.findContours(fill, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None:
        return [], (0, 0, w, h)

    hier = hierarchy[0]
    regions = []
    for i, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue
        # outer contours with white fill inside black lines
        parent = hier[i][3]
        # skip outer canvas frame
        peri = cv2.arcLength(cnt, True)
        if peri < 20:
            continue
        x, y, bw, bh = cv2.boundingRect(cnt)
        if bw > 0.98 * w and bh > 0.98 * h:
            continue
        approx = cv2.approxPolyDP(cnt, 0.002 * peri, True)
        regions.append(
            {
                "cnt": approx,
                "area": area,
                "bbox": (x, y, bw, bh),
                "depth": 0 if parent == -1 else 1,
            }
        )

    if not regions:
        return [], (0, 0, w, h)

    xs = [r["bbox"][0] for r in regions] + [r["bbox"][0] + r["bbox"][2] for r in regions]
    ys = [r["bbox"][1] for r in regions] + [r["bbox"][1] + r["bbox"][3] for r in regions]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    pad_x = (x1 - x0) * padding
    pad_y = (y1 - y0) * padding
    x0 = max(0, x0 - pad_x)
    y0 = max(0, y0 - pad_y)
    x1 = min(w, x1 + pad_x)
    y1 = min(h, y1 + pad_y)
    cw, ch = x1 - x0, y1 - y0
    s = VIEW / max(cw, ch)
    ox = (VIEW - cw * s) / 2 - x0 * s
    oy = (VIEW - ch * s) / 2 - y0 * s
    for r in regions:
        r["path"] = contour_to_path(r["cnt"], s, s, ox, oy)
        r["cx"] = (r["bbox"][0] + r["bbox"][2] / 2) * s + ox
        r["cy"] = (r["bbox"][1] + r["bbox"][3] / 2) * s + oy
    return regions, (x0, y0, x1, y1)


def extract_line_mask(gray: np.ndarray) -> np.ndarray:
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    lines = 255 - bw
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    lines = cv2.morphologyEx(lines, cv2.MORPH_CLOSE, kernel, iterations=1)
    return lines


def hough_decor_lines(gray: np.ndarray, bounds, n_max: int = 80) -> list[str]:
    """Thin internal lines (window crosses, veins) as decor-line paths."""
    lines_mask = extract_line_mask(gray)
    h, w = gray.shape
    x0, y0, x1, y1 = bounds
    roi = lines_mask[int(y0) : int(y1), int(x0) : int(x1)]
    edges = cv2.Canny(roi, 50, 150)
    detected = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=25, minLineLength=12, maxLineGap=4)
    if detected is None:
        return []
    cw, ch = x1 - x0, y1 - y0
    s = VIEW / max(cw, ch)
    ox = (VIEW - cw * s) / 2 - x0 * s
    oy = (VIEW - ch * s) / 2 - y0 * s
    out = []
    for seg in detected[:n_max]:
        x1l, y1l, x2l, y2l = seg[0]
        ax = x1l * s + ox
        ay = y1l * s + oy
        bx = x2l * s + ox
        by = y2l * s + oy
        length = ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5
        if length < 8 or length > 120:
            continue
        out.append(f"M {ax:.1f} {ay:.1f} L {bx:.1f} {by:.1f}")
    return out


def slugify(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_")
    return s or "region"


def assign_ids(regions: list[dict], prefix: str) -> None:
    """Stable ids by position (top-bottom, left-right)."""
    regions.sort(key=lambda r: (round(r["cy"] / 8), round(r["cx"] / 8), -r["area"]))
    tall = sorted(regions, key=lambda r: -r["bbox"][3])
    for i, r in enumerate(regions):
        r["id"] = f"{prefix}{i + 1}"


def build_svg(
    title: str,
    regions: list[dict],
    decor: list[str],
    ids: list[str] | None = None,
) -> str:
    if ids:
        for r, rid in zip(regions, ids):
            r["id"] = rid
    else:
        assign_ids(regions, "section")

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW} {VIEW}" aria-label="{title}">',
    ]
    for r in regions:
        rid = r["id"]
        lines.append(
            f'  <path id="{rid}" class="paint-section" fill="#fff" stroke="#111" '
            f'stroke-width="{STROKE}" stroke-linejoin="round" d="{r["path"]}"/>'
        )
    for i, d in enumerate(decor):
        lines.append(
            f'  <path class="decor-line" fill="none" stroke="#111" stroke-width="3" '
            f'stroke-linecap="round" d="{d}"/>'
        )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--title", default="Picture")
    ap.add_argument("--min-area", type=float, default=MIN_AREA)
    ap.add_argument("--prefix", default="section")
    ap.add_argument("--no-decor", action="store_true")
    args = ap.parse_args()

    gray, _ = load_gray(Path(args.image))
    h, w = gray.shape
    min_a = args.min_area * (max(h, w) / 800) ** 2
    regions, bounds = trace_regions(gray, min_a)
    assign_ids(regions, args.prefix)
    decor = [] if args.no_decor else hough_decor_lines(gray, bounds)
    svg = build_svg(args.title, regions, decor)
    Path(args.output).write_text(svg)
    print(f"Wrote {args.output}: {len(regions)} sections, {len(decor)} decor lines")
    print("ids:", ", ".join(r["id"] for r in regions))


if __name__ == "__main__":
    main()
