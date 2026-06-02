#!/usr/bin/env python3
"""Place butterfly paint overlays in native PNG pixel coordinates."""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PNG = ROOT / "assets" / "pictures" / "butterfly-art.png"
SVG = ROOT / "assets" / "pictures" / "butterfly.svg"
CATALOG = ROOT / "data" / "catalog.js"

STROKE = 2
MIN_DIST = 15

SECTION_IDS = [
    "leftUpperSpot",
    "leftUpperOval",
    "leftUpperBlob",
    "leftUpperDot",
    "leftUpperInner",
    "rightUpperSpot",
    "rightUpperOval",
    "rightUpperBlob",
    "rightUpperDot",
    "rightUpperInner",
    "leftLowerSpot",
    "leftLowerOval",
    "leftLowerBlob",
    "leftLowerMid",
    "rightLowerSpot",
    "rightLowerOval",
    "rightLowerBlob",
    "rightLowerMid",
]


def fmt(n: float) -> str:
    s = f"{n:.1f}"
    return s.rstrip("0").rstrip(".")


def load_gray(path: Path) -> np.ndarray:
    return np.array(Image.open(path).convert("L"))


def white_fill_mask(gray: np.ndarray) -> np.ndarray:
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    lines = cv2.dilate(255 - bw, kernel, iterations=1)
    return cv2.bitwise_and(bw, cv2.bitwise_not(lines)) > 0


def interior_fill_mask(fill: np.ndarray) -> np.ndarray:
    h, w = fill.shape
    flooded = fill.astype(np.uint8) * 255
    flood = np.zeros((h + 2, w + 2), np.uint8)
    for seed in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        cv2.floodFill(flooded, flood, seed, 0)
    return flooded > 0


def safe_interior(fill: np.ndarray, min_dist: float = MIN_DIST) -> tuple[np.ndarray, np.ndarray]:
    dist = cv2.distanceTransform(fill.astype(np.uint8) * 255, cv2.DIST_L2, 5)
    return dist > min_dist, dist


def butterfly_center(gray: np.ndarray, fill: np.ndarray) -> tuple[float, float]:
    h, w = gray.shape
    band = fill & (np.arange(h)[:, None] > h * 0.25) & (np.arange(h)[:, None] < h * 0.72)
    dark = (gray < 128) & band
    ys, xs = np.where(dark)
    if len(xs) < 50:
        return w / 2, h * 0.48
    return float(np.median(xs)), float(np.median(ys))


def pick_peaks(
    dist: np.ndarray, mask: np.ndarray, n: int, min_sep: float = 22.0
) -> list[tuple[float, float, float]]:
    work = dist.copy()
    work[~mask] = 0
    picks: list[tuple[float, float, float]] = []
    for _ in range(n * 4):
        if work.max() < MIN_DIST:
            break
        y, x = np.unravel_index(work.argmax(), work.shape)
        d = float(work[y, x])
        if d < MIN_DIST:
            break
        picks.append((float(x), float(y), d))
        cv2.circle(work, (int(x), int(y)), int(max(min_sep, d * 0.9)), 0, -1)
        if len(picks) >= n:
            break
    return picks


def circle_el(cx: float, cy: float, r: float, rid: str) -> str:
    r = max(4.0, r)
    return (
        f'  <circle id="{rid}" class="paint-section" cx="{fmt(cx)}" cy="{fmt(cy)}" '
        f'r="{fmt(r)}" fill="#fff" stroke="#bbb" stroke-width="{STROKE}"/>'
    )


def ellipse_el(cx: float, cy: float, rx: float, ry: float, rid: str, angle: float = 0.0) -> str:
    rx, ry = max(4.0, rx), max(4.0, ry)
    rot = f' transform="rotate({fmt(angle)} {fmt(cx)} {fmt(cy)})"' if angle else ""
    return (
        f'  <ellipse id="{rid}" class="paint-section" cx="{fmt(cx)}" cy="{fmt(cy)}" '
        f'rx="{fmt(rx)}" ry="{fmt(ry)}" fill="#fff" stroke="#bbb" stroke-width="{STROKE}"{rot}/>'
    )


def blob_el(cx: float, cy: float, r: float, rid: str) -> str:
    r = max(5.0, r)
    pts: list[tuple[float, float]] = []
    for i in range(8):
        a = 2 * math.pi * i / 8
        wobble = 1.0 + 0.12 * math.sin(i * 2.7)
        pts.append((cx + r * wobble * math.cos(a), cy + r * wobble * math.sin(a)))
    d = f"M {fmt(pts[0][0])} {fmt(pts[0][1])}"
    for x, y in pts[1:]:
        d += f" L {fmt(x)} {fmt(y)}"
    d += " Z"
    return (
        f'  <path id="{rid}" class="paint-section" fill="#fff" stroke="#bbb" '
        f'stroke-width="{STROKE}" stroke-linejoin="round" d="{d}"/>'
    )


def build_overlays(gray: np.ndarray, fill: np.ndarray, dist: np.ndarray, safe: np.ndarray) -> list[str]:
    h, w = gray.shape
    cx0, cy0 = butterfly_center(gray, fill)
    y_split = cy0 + h * 0.02
    yy, xx = np.mgrid[0:h, 0:w]

    zones: list[tuple[list[str], np.ndarray]] = [
        (
            ["leftUpperSpot", "leftUpperOval", "leftUpperBlob", "leftUpperDot", "leftUpperInner"],
            safe & fill & (xx < cx0 - 8) & (yy < y_split),
        ),
        (
            ["rightUpperSpot", "rightUpperOval", "rightUpperBlob", "rightUpperDot", "rightUpperInner"],
            safe & fill & (xx > cx0 + 8) & (yy < y_split),
        ),
        (
            ["leftLowerSpot", "leftLowerOval", "leftLowerBlob", "leftLowerMid"],
            safe & fill & (xx < cx0 - 8) & (yy >= y_split),
        ),
        (
            ["rightLowerSpot", "rightLowerOval", "rightLowerBlob", "rightLowerMid"],
            safe & fill & (xx > cx0 + 8) & (yy >= y_split),
        ),
    ]

    elements: list[str] = []
    kinds = ["circle", "ellipse", "blob", "circle", "ellipse"]
    for ids, zone_mask in zones:
        peaks = pick_peaks(dist, zone_mask, len(ids))
        if len(peaks) < len(ids):
            relaxed = fill & zone_mask
            dist2 = dist.copy()
            dist2[~relaxed] = 0
            peaks = pick_peaks(dist2, relaxed, len(ids), min_sep=18)
        side = -1 if ids[0].startswith("left") else 1
        peaks.sort(key=lambda p: (p[1], side * p[0]))
        for i, rid in enumerate(ids):
            if i >= len(peaks):
                break
            px, py, d = peaks[i]
            r = min(d * 0.55, 32.0)
            px = float(np.clip(px, r + 4, w - r - 4))
            py = float(np.clip(py, r + 4, h - r - 4))
            kind = kinds[i % len(kinds)]
            angle = math.degrees(math.atan2(py - cy0, px - cx0)) + (-18 if side < 0 else 18)
            if kind == "circle":
                elements.append(circle_el(px, py, r * 0.85, rid))
            elif kind == "ellipse":
                elements.append(ellipse_el(px, py, r * 0.75, r * 1.15, rid, angle))
            else:
                elements.append(blob_el(px, py, r * 0.8, rid))
    return elements


def parse_centroid(el: str) -> tuple[float, float] | None:
    m = re.search(r'\bid="([^"]+)"', el)
    if not m:
        return None
    if 'cx="' in el:
        cx = float(re.search(r'cx="([^"]+)"', el).group(1))
        cy = float(re.search(r'cy="([^"]+)"', el).group(1))
        return cx, cy
    d = re.search(r'\bd="([^"]+)"', el).group(1)
    nums = [float(x) for x in re.findall(r"[-+]?\d*\.?\d+", d)]
    if len(nums) < 4:
        return None
    xs, ys = nums[0::2], nums[1::2]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def section_id(el: str) -> str:
    m = re.search(r'id="([^"]+)"', el)
    return m.group(1) if m else "?"


def verify_on_white(gray: np.ndarray, fill: np.ndarray, overlays: list[str]) -> bool:
    ok = True
    for el in overlays:
        rid = section_id(el)
        c = parse_centroid(el)
        if c is None:
            continue
        x, y = int(round(c[0])), int(round(c[1]))
        if not (0 <= x < gray.shape[1] and 0 <= y < gray.shape[0]):
            print(f"  FAIL {rid}: out of bounds")
            ok = False
            continue
        if gray[y, x] >= 200 and fill[y, x]:
            continue
        print(f"  FAIL {rid}: centroid ({x},{y}) not on white wing (gray={gray[y,x]}, fill={fill[y,x]})")
        ok = False
    return ok


def build_svg(pw: int, ph: int, overlays: list[str]) -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {pw} {ph}" aria-label="Butterfly">',
        f'  <image href="assets/pictures/butterfly-art.png" xlink:href="assets/pictures/butterfly-art.png"',
        f'    x="0" y="0" width="{pw}" height="{ph}" pointer-events="none"/>',
    ]
    lines.extend(overlays)
    lines.extend(["</svg>", ""])
    return "\n".join(lines)


def update_catalog_viewbox(vb: str) -> None:
    text = CATALOG.read_text()
    text = re.sub(
        r"(butterfly:\s*\{[^}]*viewBox:\s*)'[^']+'",
        rf"\1'{vb}'",
        text,
        count=1,
        flags=re.S,
    )
    CATALOG.write_text(text)


def main() -> int:
    if not PNG.exists():
        print(f"Missing {PNG}", file=sys.stderr)
        return 1

    gray = load_gray(PNG)
    ph, pw = gray.shape
    raw_fill = white_fill_mask(gray)
    fill = interior_fill_mask(raw_fill)
    safe, dist = safe_interior(fill)
    overlays = build_overlays(gray, fill, dist, safe)

    print(f"PNG size: {pw}x{ph}")
    print(f"Overlays: {len(overlays)}")
    if not verify_on_white(gray, fill, overlays):
        print("Centroid verification failed", file=sys.stderr)
        return 1

    svg = build_svg(pw, ph, overlays)
    SVG.write_text(svg)
    update_catalog_viewbox(f"0 0 {pw} {ph}")
    print(f"Wrote {SVG} viewBox=0 0 {pw} {ph}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
