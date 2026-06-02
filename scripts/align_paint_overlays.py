#!/usr/bin/env python3
"""Analyze art PNGs and rebuild butterfly/giraffe SVG overlays in image coordinates."""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PICTURES = ROOT / "assets" / "pictures"
CATALOG = ROOT / "data" / "catalog.js"

STROKE = 2
MIN_DIST = 12
PAD_FRAC = 0.02


def load_gray(path: Path) -> np.ndarray:
    return np.array(Image.open(path).convert("L"))


def outline_bbox(gray: np.ndarray) -> tuple[int, int, int, int]:
    h, w = gray.shape
    dark = gray < 128
    ys, xs = np.where(dark)
    if len(xs) == 0:
        return 0, 0, w, h
    minx, maxx = int(xs.min()), int(xs.max())
    miny, maxy = int(ys.min()), int(ys.max())
    padx = max(2, int((maxx - minx) * PAD_FRAC))
    pady = max(2, int((maxy - miny) * PAD_FRAC))
    x0 = max(0, minx - padx)
    y0 = max(0, miny - pady)
    x1 = min(w, maxx + padx)
    y1 = min(h, maxy + pady)
    return x0, y0, x1, y1


def white_fill_mask(gray: np.ndarray) -> np.ndarray:
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    lines = cv2.dilate(255 - bw, kernel, iterations=1)
    return cv2.bitwise_and(bw, cv2.bitwise_not(lines)) > 0


def interior_fill_mask(fill: np.ndarray) -> np.ndarray:
    """White regions enclosed by outlines (exclude page background)."""
    h, w = fill.shape
    flooded = fill.astype(np.uint8) * 255
    flood = np.zeros((h + 2, w + 2), np.uint8)
    for seed in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        cv2.floodFill(flooded, flood, seed, 0)
    return flooded > 0


def safe_interior(fill: np.ndarray, min_dist: float = MIN_DIST) -> np.ndarray:
    dist = cv2.distanceTransform(fill.astype(np.uint8) * 255, cv2.DIST_L2, 5)
    return dist > min_dist, dist


def fmt(n: float) -> str:
    s = f"{n:.1f}"
    return s.rstrip("0").rstrip(".")


def outer_clip_path(gray: np.ndarray, fill: np.ndarray) -> str:
    """Outer silhouette: largest dark outline contour that is not the image frame."""
    h, w = gray.shape
    dark = (gray < 128).copy()
    margin = max(4, int(min(h, w) * 0.012))
    dark[:margin, :] = False
    dark[-margin:, :] = False
    dark[:, :margin] = False
    dark[:, -margin:] = False
    dark = dark.astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    dark = cv2.morphologyEx(dark, cv2.MORPH_CLOSE, kernel, iterations=1)
    cnts, _ = cv2.findContours(dark, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates: list[np.ndarray] = []
    for cnt in cnts:
        x, y, bw, bh = cv2.boundingRect(cnt)
        if x <= 1 and y <= 1 and bw >= w - 3 and bh >= h - 3:
            continue
        if cv2.contourArea(cnt) < 500:
            continue
        candidates.append(cnt)
    if not candidates:
        blob = cv2.dilate(fill.astype(np.uint8) * 255, kernel, iterations=2)
        cnts, _ = cv2.findContours(blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        candidates = list(cnts)
    if not candidates:
        return ""
    cnt = max(candidates, key=cv2.contourArea)
    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, max(2.0, 0.008 * peri), True)
    pts = approx.reshape(-1, 2)
    d = f"M {fmt(pts[0, 0])} {fmt(pts[0, 1])}"
    for x, y in pts[1:]:
        d += f" L {fmt(x)} {fmt(y)}"
    return d + " Z"


def pick_peaks(
    dist: np.ndarray,
    mask: np.ndarray,
    n: int,
    min_sep: float,
) -> list[tuple[float, float, float]]:
    """Return up to n (cx, cy, max_radius) sorted by distance descending."""
    work = dist.copy()
    work[~mask] = 0
    picks: list[tuple[float, float, float]] = []
    h, w = work.shape
    for _ in range(n * 4):
        if work.max() < MIN_DIST:
            break
        y, x = np.unravel_index(work.argmax(), work.shape)
        d = float(work[y, x])
        if d < MIN_DIST:
            break
        picks.append((float(x), float(y), d))
        r_clear = int(max(min_sep, d * 0.9))
        cv2.circle(work, (int(x), int(y)), r_clear, 0, -1)
        if len(picks) >= n:
            break
    picks.sort(key=lambda p: (p[1], p[0]))
    return picks[:n]


def circle_el(cx: float, cy: float, r: float, rid: str) -> str:
    r = max(4.0, r)
    return (
        f'  <circle id="{rid}" class="paint-section" cx="{fmt(cx)}" cy="{fmt(cy)}" '
        f'r="{fmt(r)}" fill="#fff" stroke="#bbb" stroke-width="{STROKE}"/>'
    )


def ellipse_el(
    cx: float, cy: float, rx: float, ry: float, rid: str, angle: float = 0.0
) -> str:
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


def giraffe_blob(cx: float, cy: float, r: float, rid: str) -> str:
    r = max(8.0, min(r, 28.0))
    pts: list[tuple[float, float]] = []
    n = 11
    for i in range(n):
        a = 2 * math.pi * i / n - math.pi / 2
        wobble = 1.0 + 0.22 * math.sin(i * 3.1 + cx * 0.02)
        pts.append((cx + r * wobble * math.cos(a), cy + r * wobble * 0.85 * math.sin(a)))
    d = f"M {fmt(pts[0][0])} {fmt(pts[0][1])}"
    for x, y in pts[1:]:
        d += f" L {fmt(x)} {fmt(y)}"
    d += " Z"
    return (
        f'  <path id="{rid}" class="paint-section" fill="#fff" stroke="#bbb" '
        f'stroke-width="{STROKE}" stroke-linejoin="round" d="{d}"/>'
    )


def butterfly_center(gray: np.ndarray, fill: np.ndarray) -> tuple[float, float]:
    h, w = gray.shape
    band = fill & (np.arange(h)[:, None] > h * 0.25) & (np.arange(h)[:, None] < h * 0.72)
    dark = (gray < 128) & band
    ys, xs = np.where(dark)
    if len(xs) < 50:
        return w / 2, h * 0.48
    return float(np.median(xs)), float(np.median(ys))


def build_butterfly_overlays(
    gray: np.ndarray, fill: np.ndarray, dist: np.ndarray, safe: np.ndarray
) -> list[str]:
    h, w = gray.shape
    cx0, cy0 = butterfly_center(gray, fill)
    y_split = cy0 + h * 0.02

    zones: list[tuple[str, list[str], callable]] = [
        (
            "leftUpper",
            ["leftUpperSpot", "leftUpperOval", "leftUpperBlob", "leftUpperDot", "leftUpperInner"],
            lambda x, y: x < cx0 - 8 and y < y_split,
        ),
        (
            "rightUpper",
            ["rightUpperSpot", "rightUpperOval", "rightUpperBlob", "rightUpperDot", "rightUpperInner"],
            lambda x, y: x > cx0 + 8 and y < y_split,
        ),
        (
            "leftLower",
            ["leftLowerSpot", "leftLowerOval", "leftLowerBlob", "leftLowerMid"],
            lambda x, y: x < cx0 - 8 and y >= y_split,
        ),
        (
            "rightLower",
            ["rightLowerSpot", "rightLowerOval", "rightLowerBlob", "rightLowerMid"],
            lambda x, y: x > cx0 + 8 and y >= y_split,
        ),
    ]

    yy, xx = np.mgrid[0:h, 0:w]
    elements: list[str] = []
    for _name, ids, cond in zones:
        zone_mask = safe & np.vectorize(lambda x, y: cond(x, y))(xx, yy)
        zone_mask &= fill
        peaks = pick_peaks(dist, zone_mask, len(ids), min_sep=22)
        if len(peaks) < len(ids):
            # Relax distance for sparse zones
            zone_mask2 = fill & np.vectorize(lambda x, y: cond(x, y))(xx, yy)
            dist2 = dist.copy()
            dist2[~zone_mask2] = 0
            peaks = pick_peaks(dist2, zone_mask2, len(ids), min_sep=18)
        # Sort peaks: top-to-bottom, then outward from center
        side = -1 if "left" in ids[0] else 1
        peaks.sort(key=lambda p: (p[1], side * p[0]))
        kinds = ["circle", "ellipse", "blob", "circle", "ellipse"]
        for i, rid in enumerate(ids):
            if i >= len(peaks):
                break
            px, py, d = peaks[i]
            r = min(d * 0.55, 32.0)
            px = float(np.clip(px, r + 4, w - r - 4))
            py = float(np.clip(py, r + 4, h - r - 4))
            kind = kinds[i % len(kinds)]
            angle = math.degrees(math.atan2(py - cy0, px - cx0))
            if kind == "circle":
                elements.append(circle_el(px, py, r * 0.85, rid))
            elif kind == "ellipse":
                elements.append(
                    ellipse_el(px, py, r * 0.75, r * 1.15, rid, angle + (-18 if side < 0 else 18))
                )
            else:
                elements.append(blob_el(px, py, r * 0.8, rid))
    return elements


def giraffe_patch_mask(fill: np.ndarray, gray: np.ndarray) -> np.ndarray:
    h, w = gray.shape
    dark = gray < 128
    ys, xs = np.where(dark & (np.arange(h)[:, None] > h * 0.08))
    if len(xs) == 0:
        return fill
    x_lo, x_hi = float(np.percentile(xs, 22)), float(np.percentile(xs, 82))
    y_lo, y_hi = float(np.percentile(ys, 10)), float(np.percentile(ys, 62))
    yy, xx = np.mgrid[0:h, 0:w]
    return fill & (xx >= x_lo) & (xx <= x_hi) & (yy >= y_lo) & (yy <= y_hi)


def build_giraffe_overlays(
    gray: np.ndarray, fill: np.ndarray, dist: np.ndarray, safe: np.ndarray
) -> list[str]:
    patch_mask = giraffe_patch_mask(fill, gray) & safe
    h, w = gray.shape
    neck_ids = [f"neckPatch{i}" for i in range(1, 6)]
    body_ids = [f"bodyPatch{i}" for i in range(1, 9)]

    yy = np.arange(h)[:, None]
    neck_mask = patch_mask & (yy < h * 0.50)
    xx = np.arange(w)[None, :]
    body_mask = patch_mask & (yy >= h * 0.42) & (yy < h * 0.70) & (xx > w * 0.14) & (xx < w * 0.86)

    neck_peaks = pick_peaks(dist, neck_mask, len(neck_ids), min_sep=26)
    body_dist = dist.copy()
    for px, py, d in neck_peaks:
        cv2.circle(body_dist, (int(px), int(py)), int(max(28, d * 1.2)), 0, -1)
    body_peaks = pick_peaks(body_dist, body_mask, len(body_ids), min_sep=22)
    neck_peaks.sort(key=lambda p: p[1])
    body_peaks.sort(key=lambda p: (p[1], p[0]))

    elements: list[str] = []
    for rid, (px, py, d) in zip(neck_ids, neck_peaks):
        r = min(d * 0.48, 18.0)
        elements.append(giraffe_blob(px, py, r, rid))
    for rid, (px, py, d) in zip(body_ids, body_peaks):
        r = min(d * 0.45, 20.0)
        if px > w * 0.88 or px < w * 0.12:
            r *= 0.75
        elements.append(giraffe_blob(px, py, r, rid))
    return elements


def viewbox_str(vb: tuple[int, int, int, int]) -> str:
    x0, y0, x1, y1 = vb
    return f"{x0} {y0} {x1 - x0} {y1 - y0}"


def build_svg(
    label: str,
    png_name: str,
    vb: tuple[int, int, int, int],
    pw: int,
    ph: int,
    overlays: list[str],
    clip_d: str,
) -> str:
    x0, y0, w, h = vb[0], vb[1], vb[2] - vb[0], vb[3] - vb[1]
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="{viewbox_str(vb)}" aria-label="{label}">',
        "  <defs>",
        f'    <clipPath id="clip"><path d="{clip_d}"/></clipPath>',
        "  </defs>",
        f'  <image href="assets/pictures/{png_name}" xlink:href="assets/pictures/{png_name}"',
        f'    x="0" y="0" width="{pw}" height="{ph}" pointer-events="none"/>',
        '  <g clip-path="url(#clip)">',
    ]
    lines.extend(overlays)
    lines.extend(["  </g>", "</svg>", ""])
    return "\n".join(lines)


def update_catalog_viewbox(picture: str, vb_str: str) -> None:
    text = CATALOG.read_text()
    text = re.sub(
        rf"({picture}:\s*\{{[^}}]*viewBox:\s*)'[^']+'",
        rf"\1'{vb_str}'",
        text,
        count=1,
        flags=re.S,
    )
    CATALOG.write_text(text)


def analyze(name: str) -> dict:
    png = PICTURES / f"{name}-art.png"
    gray = load_gray(png)
    ph, pw = gray.shape
    vb = outline_bbox(gray)
    raw_fill = white_fill_mask(gray)
    fill = interior_fill_mask(raw_fill)
    safe, dist = safe_interior(fill)
    clip = outer_clip_path(gray, fill)
    if name == "butterfly":
        overlays = build_butterfly_overlays(gray, fill, dist, safe)
    else:
        overlays = build_giraffe_overlays(gray, fill, dist, safe)
    return {
        "png": png,
        "pw": pw,
        "ph": ph,
        "vb": vb,
        "vb_str": viewbox_str(vb),
        "clip": clip,
        "overlays": overlays,
        "count": len(overlays),
    }


def write_picture(name: str, info: dict) -> None:
    label = name.capitalize()
    svg = build_svg(
        label,
        f"{name}-art.png",
        info["vb"],
        info["pw"],
        info["ph"],
        info["overlays"],
        info["clip"],
    )
    out = PICTURES / f"{name}.svg"
    out.write_text(svg)
    update_catalog_viewbox(name, info["vb_str"])
    print(f"Wrote {out} viewBox={info['vb_str']} sections={info['count']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pictures", nargs="*", default=["butterfly", "giraffe"])
    parser.add_argument("--write", action="store_true", help="Write SVG + catalog viewBox")
    args = parser.parse_args()

    for name in args.pictures:
        info = analyze(name)
        print(f"\n{name}:")
        print(f"  PNG size: {info['pw']}x{info['ph']}")
        print(f"  viewBox: {info['vb_str']}")
        print(f"  overlays: {info['count']}")
        if args.write:
            write_picture(name, info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
