#!/usr/bin/env python3
"""Build paint-section SVG from PDF vector drawings + raster cell segmentation."""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import cv2
import fitz
import numpy as np

VIEW = 400
STROKE = 3.5


def page_to_gray(page: fitz.Page, dpi: int = 150) -> np.ndarray:
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img
    return gray


def segment_paint_regions(gray: np.ndarray, min_area: float) -> list[np.ndarray]:
    """Connected white components separated by black lines."""
    _, bw = cv2.threshold(cv2.GaussianBlur(gray, (3, 3), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    white = bw.copy()
    lines = 255 - white
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    lines = cv2.dilate(lines, kernel, iterations=1)
    white = cv2.bitwise_and(white, cv2.bitwise_not(lines))
    num, labels = cv2.connectedComponents(white)
    h, w = gray.shape
    regions = []
    for label in range(1, num):
        mask = (labels == label).astype(np.uint8) * 255
        area = cv2.countNonZero(mask)
        if area < min_area:
            continue
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not cnts:
            continue
        cnt = max(cnts, key=cv2.contourArea)
        if cv2.contourArea(cnt) < min_area:
            continue
        x, y, bw, bh = cv2.boundingRect(cnt)
        if bw > 0.97 * w and bh > 0.97 * h:
            continue
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, max(1.5, 0.0025 * peri), True)
        regions.append(approx)
    return regions


def fit_to_viewbox(contours: list, padding: float = 0.05) -> tuple[list[str], list[tuple[float, float]]]:
    xs, ys = [], []
    for cnt in contours:
        for p in cnt.reshape(-1, 2):
            xs.append(float(p[0]))
            ys.append(float(p[1]))
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    cw, ch = x1 - x0, y1 - y0
    pad_x, pad_y = cw * padding, ch * padding
    x0 -= pad_x
    y0 -= pad_y
    x1 += pad_x
    y1 += pad_y
    cw, ch = x1 - x0, y1 - y0
    s = VIEW / max(cw, ch)
    ox = (VIEW - cw * s) / 2 - x0 * s
    oy = (VIEW - ch * s) / 2 - y0 * s

    paths = []
    centroids = []
    for cnt in contours:
        pts = cnt.reshape(-1, 2).astype(float)
        pts[:, 0] = pts[:, 0] * s + ox
        pts[:, 1] = pts[:, 1] * s + oy
        cx, cy = pts[:, 0].mean(), pts[:, 1].mean()
        centroids.append((cx, cy))
        d = f"M {pts[0,0]:.1f} {pts[0,1]:.1f}"
        for x, y in pts[1:]:
            d += f" L {x:.1f} {y:.1f}"
        d += " Z"
        paths.append(d)
    return paths, centroids


def drawing_to_path(drawing: dict) -> str | None:
    """Convert pymupdf drawing dict to SVG path in page coords (y flipped later)."""
    items = drawing.get("items") or []
    if not items:
        return None
    parts = []
    cur = None
    for it in items:
        op = it[0]
        if op == "l":
            p = fitz.Point(it[1])
            if cur is None:
                parts.append(f"M {p.x:.2f} {p.y:.2f}")
            else:
                parts.append(f"L {p.x:.2f} {p.y:.2f}")
            cur = p
        elif op == "c":
            p1, p2, p3 = fitz.Point(it[1]), fitz.Point(it[2]), fitz.Point(it[3])
            if cur is None:
                parts.append(f"M {p1.x:.2f} {p1.y:.2f}")
            parts.append(
                f"C {p1.x:.2f} {p1.y:.2f} {p2.x:.2f} {p2.y:.2f} {p3.x:.2f} {p3.y:.2f}"
            )
            cur = p3
        elif op == "re":
            r = it[1]
            parts.append(
                f"M {r.x0:.2f} {r.y0:.2f} L {r.x1:.2f} {r.y0:.2f} "
                f"L {r.x1:.2f} {r.y1:.2f} L {r.x0:.2f} {r.y1:.2f} Z"
            )
            cur = fitz.Point(r.x1, r.y1)
    if not parts:
        return None
    if drawing.get("closePath"):
        parts.append("Z")
    return " ".join(parts)


def map_page_path_to_view(d: str, page_h: float, bounds, s: float, ox: float, oy: float) -> str:
    """Flip PDF y and scale path d to viewBox."""
    x0, y0, x1, y1 = bounds

    def repl(m):
        cmd = m.group(1)
        nums = [float(n) for n in re.findall(r"[-+]?(?:\d*\.\d+|\d+)", m.group(0)[len(cmd) :])]
        out = []
        i = 0
        while i < len(nums):
            x, y = nums[i], nums[i + 1]
            y = page_h - y
            x = x * s + ox
            y = y * s + oy
            out.extend([f"{x:.1f}", f"{y:.1f}"])
            i += 2
        return cmd + " ".join(out)

    return re.sub(r"([MLCQZ])\s*[-\d\.\s]+", repl, d, flags=re.I)


def extract_stroke_decor(page: fitz.Page, bounds, s: float, ox: float, oy: float) -> list[str]:
    decor = []
    ph = page.rect.height
    for d in page.get_drawings():
        if d.get("fill"):
            continue
        if (d.get("width") or 0) < 1:
            continue
        p = drawing_to_path(d)
        if not p:
            continue
        decor.append(map_page_path_to_view(p, ph, bounds, s, ox, oy))
    return decor


def name_butterfly(ids: list[str], centroids: list[tuple[float, float]]) -> list[str]:
    """Assign semantic ids for monarch butterfly regions."""
    named = []
    body = []
    for i, (cx, cy) in enumerate(centroids):
        if 175 < cx < 225 and 170 < cy < 240:
            body.append(i)
    body_idx = body[0] if body else None

    upper_left, upper_right, lower_left, lower_right = [], [], [], []
    spots_ul, spots_ur = [], []
    dots_l, dots_r = [], []

    for i, (cx, cy) in enumerate(centroids):
        if body_idx is not None and i == body_idx:
            continue
        if cy < 175:
            if cx < 195:
                if cy < 120 and cx < 120:
                    spots_ul.append(i)
                else:
                    upper_left.append(i)
            else:
                if cy < 120 and cx > 280:
                    spots_ur.append(i)
                else:
                    upper_right.append(i)
        else:
            if cx < 195:
                if cy > 300 and cx < 120:
                    dots_l.append(i)
                else:
                    lower_left.append(i)
            else:
                if cy > 300 and cx > 280:
                    dots_r.append(i)
                else:
                    lower_right.append(i)

    def sort_by_pos(idxs):
        return sorted(idxs, key=lambda j: (centroids[j][1], centroids[j][0]))

    result = [""] * len(centroids)
    if body_idx is not None:
        result[body_idx] = "abdomen" if centroids[body_idx][1] > 200 else "thorax"
        # refine: topmost body = head area - monarch body is one piece often
        if len(body) == 1:
            result[body_idx] = "thorax"

    for j, i in enumerate(sort_by_pos(upper_left)):
        result[i] = ["leftUpperBorder", "leftUpperPanelA", "leftUpperPanelB", "leftUpperPanelC"][min(j, 3)] if j < 4 else f"leftUpperExtra{j}"
    for j, i in enumerate(sort_by_pos(upper_right)):
        result[i] = ["rightUpperBorder", "rightUpperPanelA", "rightUpperPanelB", "rightUpperPanelC"][min(j, 3)] if j < 4 else f"rightUpperExtra{j}"
    for j, i in enumerate(sort_by_pos(lower_left)):
        result[i] = ["leftLowerBorder", "leftLowerPanelA", "leftLowerPanelB"][min(j, 2)] if j < 3 else f"leftLowerExtra{j}"
    for j, i in enumerate(sort_by_pos(lower_right)):
        result[i] = ["rightLowerBorder", "rightLowerPanelA", "rightLowerPanelB"][min(j, 2)] if j < 3 else f"rightLowerExtra{j}"
    for j, i in enumerate(sort_by_pos(spots_ul)):
        result[i] = "leftUpperSpot" if j == 0 else f"leftUpperSpot{j+1}"
    for j, i in enumerate(sort_by_pos(spots_ur)):
        result[i] = "rightUpperSpot" if j == 0 else f"rightUpperSpot{j+1}"
    for j, i in enumerate(sort_by_pos(dots_l)):
        result[i] = f"leftLowerDot{j+1}"
    for j, i in enumerate(sort_by_pos(dots_r)):
        result[i] = f"rightLowerDot{j+1}"

    for i in range(len(centroids)):
        if not result[i]:
            result[i] = f"region{i+1}"
    return result


def build_svg(title: str, paths: list[str], ids: list[str], decor: list[str]) -> str:
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW} {VIEW}" aria-label="{title}">',
    ]
    for rid, d in zip(ids, paths):
        lines.append(
            f'  <path id="{rid}" class="paint-section" fill="#fff" stroke="#111" '
            f'stroke-width="{STROKE}" stroke-linejoin="round" d="{d}"/>'
        )
    for d in decor:
        lines.append(
            f'  <path class="decor-line" fill="none" stroke="#111" stroke-width="3" '
            f'stroke-linecap="round" d="{d}"/>'
        )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def process_pdf(pdf_path: Path, out_path: Path, title: str, naming: str | None, min_area: float):
    doc = fitz.open(pdf_path)
    page = doc[0]
    gray = page_to_gray(page, dpi=180)
    h, w = gray.shape
    min_a = min_area * (max(h, w) / 1000) ** 2
    contours = segment_paint_regions(gray, min_a)
    paths, centroids = fit_to_viewbox(contours)

    # bounds for decor mapping
    xs = [c[0] for c in centroids]
    ys = [c[1] for c in centroids]
    # recompute scale from contours raw - use fit bounds embedded
    # decor from vector strokes
    x0, y0, x1, y1 = 0, 0, page.rect.width, page.rect.height
    cw, ch = x1 - x0, y1 - y0
    s = VIEW / max(cw, ch) * 0.9
    ox = (VIEW - cw * s) / 2
    oy = (VIEW - ch * s) / 2
    decor = extract_stroke_decor(page, (x0, y0, x1, y1), s, ox, oy)

    if naming == "butterfly":
        ids = name_butterfly([], centroids)
        # fix head - smallest body region near center top
        for i, (cx, cy) in enumerate(centroids):
            if 185 < cx < 215 and 155 < cy < 195:
                ids[i] = "head"
    else:
        ids = [f"section{i+1}" for i in range(len(paths))]

    # antennae from filled drawings
    for d in page.get_drawings():
        fill = d.get("fill")
        if not fill or fill == (1, 1, 1):
            continue
        if len(d.get("items", [])) < 4:
            continue
        p = drawing_to_path(d)
        if p:
            decor.append(map_page_path_to_view(p, page.rect.height, (0, 0, 1, 1), s, ox, oy))

    svg = build_svg(title, paths, ids, decor)
    out_path.write_text(svg)
    doc.close()
    print(f"Wrote {out_path}: {len(paths)} sections")
    print("ids:", ", ".join(ids))


def process_image(img_path: Path, out_path: Path, title: str, min_area: float):
    gray = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
    if gray is None:
        raise SystemExit(f"bad image {img_path}")
    h, w = gray.shape
    if max(h, w) > 1400:
        sc = 1400 / max(h, w)
        gray = cv2.resize(gray, (int(w * sc), int(h * sc)))
    min_a = min_area * (max(gray.shape) / 1000) ** 2
    contours = segment_paint_regions(gray, min_a)
    paths, centroids = fit_to_viewbox(contours)
    ids = [f"section{i+1}" for i in range(len(paths))]
    svg = build_svg(title, paths, ids, [])
    out_path.write_text(svg)
    print(f"Wrote {out_path}: {len(paths)} sections")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--title", default="Picture")
    ap.add_argument("--naming")
    ap.add_argument("--min-area", type=float, default=200)
    args = ap.parse_args()
    inp = Path(args.input)
    out = Path(args.output)
    if inp.suffix.lower() == ".pdf":
        process_pdf(inp, out, args.title, args.naming, args.min_area)
    else:
        process_image(inp, out, args.title, args.min_area)


if __name__ == "__main__":
    main()
