#!/usr/bin/env python3
"""Tighten giraffe.svg viewBox to PNG size and align patch overlays."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SVG_PATH = ROOT / "assets" / "pictures" / "giraffe.svg"
PNG_PATH = ROOT / "assets" / "pictures" / "giraffe-art.png"

OLD_VIEW = 400
PW, PH = 408, 526
SCALE = min(OLD_VIEW / PW, OLD_VIEW / PH)
OX = (OLD_VIEW - PW * SCALE) / 2
OY = (OLD_VIEW - PH * SCALE) / 2


def load_interior_mask() -> tuple[np.ndarray, np.ndarray]:
    gray = np.array(Image.open(PNG_PATH).convert("L"))
    lines = gray < 128
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    fill = 255 - bw
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    line_mask = 255 - fill
    line_mask = cv2.morphologyEx(line_mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    fill = 255 - line_mask
    return lines, fill > 0


def gap_center(lines: np.ndarray, px: float, py: float) -> tuple[float, float] | None:
    y = int(round(py))
    if not (0 <= y < lines.shape[0]):
        return None
    xs = [x for x in np.where(lines[y])[0] if 10 < x < 398]
    if len(xs) < 2:
        return None
    clusters: list[list[int]] = [[xs[0]]]
    for x in xs[1:]:
        if x - clusters[-1][-1] <= 2:
            clusters[-1].append(x)
        else:
            clusters.append([x])
    best: tuple[float, float, float] | None = None
    for i in range(len(clusters) - 1):
        left_end = clusters[i][-1]
        right_start = clusters[i + 1][0]
        width = right_start - left_end
        if width < 12:
            continue
        mid = (left_end + right_start) / 2
        dist = abs(px - mid)
        if best is None or dist < best[0]:
            best = (dist, mid, width)
    if best is None:
        return None
    return best[1], y


def inside_silhouette(lines: np.ndarray, px: float, py: float) -> bool:
    y = int(round(py))
    x = int(round(px))
    if not (0 <= y < lines.shape[0] and 0 <= x < lines.shape[1]):
        return False
    xs = [xi for xi in np.where(lines[y])[0] if 10 < xi < 398]
    if len(xs) < 2:
        return False
    clusters: list[list[int]] = [[xs[0]]]
    for xi in xs[1:]:
        if xi - clusters[-1][-1] <= 2:
            clusters[-1].append(xi)
        else:
            clusters.append([xi])
    for i in range(len(clusters) - 1):
        left_end = clusters[i][-1]
        right_start = clusters[i + 1][0]
        if right_start - left_end > 5 and left_end < x < right_start:
            return True
    return False


def map_point(x: float, y: float) -> tuple[float, float]:
  # Patches were authored in 400×400 against letterboxed art; map into PNG space.
    return x - OX, y / SCALE


def _fmt(n: float) -> str:
    return f"{n:.1f}".rstrip("0").rstrip(".")


def transform_path_d(d: str, tx: float = 0.0, ty: float = 0.0, shrink: float = 1.0) -> str:
    tokens = re.findall(r"[MLQZ]|[-+]?(?:\d+\.\d*|\.\d+|\d+)", d, flags=re.I)
    if not tokens:
        return d
    nums = [float(n) for n in re.findall(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)", d)]
    pairs = list(zip(nums[0::2], nums[1::2]))
    mapped = [map_point(x, y) for x, y in pairs]
    cx = sum(p[0] for p in mapped) / len(mapped)
    cy = sum(p[1] for p in mapped) / len(mapped)

    def adjust(x: float, y: float) -> tuple[float, float]:
        nx = cx + (x - cx) * shrink + tx
        ny = cy + (y - cy) * shrink + ty
        return nx, ny

    out: list[str] = []
    i = 0
    n_idx = 0
    while i < len(tokens):
        cmd = tokens[i].upper()
        if cmd in "MLQ":
            i += 1
            coords: list[str] = []
            while i < len(tokens) and tokens[i] not in "MLQZ":
                x, y = mapped[n_idx]
                n_idx += 1
                ax, ay = adjust(x, y)
                coords.extend([_fmt(ax), _fmt(ay)])
                i += 2
            out.append(cmd + " " + " ".join(coords))
        elif cmd == "Z":
            out.append("Z")
            i += 1
        else:
            i += 1
    return " ".join(out)


def nudge_patch(d: str, lines: np.ndarray) -> str:
    nums = [float(n) for n in re.findall(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)", d)]
    pairs = [map_point(x, y) for x, y in zip(nums[0::2], nums[1::2])]
    cx = sum(p[0] for p in pairs) / len(pairs)
    cy = sum(p[1] for p in pairs) / len(pairs)
    tx = ty = 0.0
    shrink = 1.0
    if inside_silhouette(lines, cx, cy):
        return transform_path_d(d)
    target = gap_center(lines, cx, cy)
    if target:
        tx = (target[0] - cx) * 0.85
        ty = (target[1] - cy) * 0.15
    shrink = 0.88
    result = transform_path_d(d, tx=tx, ty=ty, shrink=shrink)
  # Second pass if still outside
    nums2 = [float(n) for n in re.findall(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)", result)]
    pairs2 = list(zip(nums2[0::2], nums2[1::2]))
    cx2 = sum(p[0] for p in pairs2) / len(pairs2)
    cy2 = sum(p[1] for p in pairs2) / len(pairs2)
    if not inside_silhouette(lines, cx2, cy2):
        target = gap_center(lines, cx2, cy2)
        if target:
            extra_x = target[0] - cx2
            extra_y = target[1] - cy2
            return transform_path_d(d, tx=tx + extra_x * 0.5, ty=ty + extra_y * 0.2, shrink=0.82)
    return result


def build_svg(lines: np.ndarray) -> str:
    text = SVG_PATH.read_text()
    paths = list(
        re.finditer(
            r'(<path id="(neckPatch\d+|bodyPatch\d+)" class="paint-section"[^>]*\s+d=")([^"]+)(")',
            text,
            re.S,
        )
    )
    new_paths: dict[str, str] = {}
    for m in paths:
        pid = m.group(2)
        new_paths[pid] = nudge_patch(m.group(3), lines)

    out = text
    for m in paths:
        pid = m.group(2)
        old = m.group(0)
        new = m.group(1) + new_paths[pid] + m.group(4)
        out = out.replace(old, new, 1)

    out = re.sub(
        r'viewBox="[^"]+"',
        f'viewBox="0 0 {PW} {PH}"',
        out,
        count=1,
    )
    out = re.sub(
        r'<image[^>]+/>',
        f'  <image href="assets/pictures/giraffe-art.png" xlink:href="assets/pictures/giraffe-art.png"\n'
        f'    x="0" y="0" width="{PW}" height="{PH}" pointer-events="none"/>',
        out,
        count=1,
    )
    return out


def update_catalog() -> None:
    cat_path = ROOT / "data" / "catalog.js"
    text = cat_path.read_text()
    text = re.sub(
        r"(giraffe:\s*\{[^}]*viewBox:\s*)'[^']+'",
        rf"\1'0 0 {PW} {PH}'",
        text,
        count=1,
        flags=re.S,
    )
    cat_path.write_text(text)


def main() -> int:
    lines, _ = load_interior_mask()
    SVG_PATH.write_text(build_svg(lines))
    update_catalog()
    print(f"Wrote {SVG_PATH} viewBox=0 0 {PW} {PH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
