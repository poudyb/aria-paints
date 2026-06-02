#!/usr/bin/env python3
"""Trace reference images into paint-section SVGs (excludes outer background)."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import cv2
import fitz
import numpy as np

VIEW = 400
STROKE = 3.5


def load_gray(path: Path, max_dim: int = 1600) -> np.ndarray:
    g = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if g is None:
        raise SystemExit(f"Cannot read {path}")
    h, w = g.shape
    if max(h, w) > max_dim:
        sc = max_dim / max(h, w)
        g = cv2.resize(g, (int(w * sc), int(h * sc)), interpolation=cv2.INTER_AREA)
    return g


def crop_content(gray: np.ndarray) -> np.ndarray:
    _, bw = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)
    pts = cv2.findNonZero(255 - bw)
    if pts is None:
        return gray
    x, y, w, h = cv2.boundingRect(pts)
    return gray[y : y + h, x : x + w]


def interior_white_mask(gray: np.ndarray) -> np.ndarray:
    _, bw = cv2.threshold(cv2.GaussianBlur(gray, (3, 3), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    lines = 255 - bw
    lines = cv2.dilate(lines, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), 2)
    white = cv2.bitwise_and(bw, cv2.bitwise_not(lines))
    h, w = white.shape
    flood = white.copy()
    mask = np.zeros((h + 2, w + 2), np.uint8)
    for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        cv2.floodFill(flood, mask, seed, 0)
    return flood


def trace_regions(gray: np.ndarray, min_area: float) -> list[tuple]:
    fill = interior_white_mask(gray)
    n, labels = cv2.connectedComponents(fill)
    h, w = fill.shape
    regions = []
    for lab in range(1, n):
        mask = (labels == lab).astype(np.uint8) * 255
        area = cv2.countNonZero(mask)
        if area < min_area:
            continue
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not cnts:
            continue
        cnt = max(cnts, key=cv2.contourArea)
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, max(1.5, 0.003 * peri), True)
        x, y, bw, bh = cv2.boundingRect(cnt)
        regions.append((approx, (x, y, bw, bh, x + bw / 2, y + bh / 2, area)))
    return regions


def to_viewbox(regions: list) -> tuple[list[str], list[dict]]:
    xs, ys = [], []
    for cnt, _ in regions:
        for p in cnt.reshape(-1, 2):
            xs.append(float(p[0]))
            ys.append(float(p[1]))
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    pad = 0.04
    px, py = (x1 - x0) * pad, (y1 - y0) * pad
    x0 -= px
    y0 -= py
    x1 += px
    y1 += py
    cw, ch = x1 - x0, y1 - y0
    s = VIEW / max(cw, ch)
    ox = (VIEW - cw * s) / 2 - x0 * s
    oy = (VIEW - ch * s) / 2 - y0 * s
    paths, meta = [], []
    for cnt, m in regions:
        pts = cnt.reshape(-1, 2).astype(float)
        pts[:, 0] = pts[:, 0] * s + ox
        pts[:, 1] = pts[:, 1] * s + oy
        d = f"M {pts[0,0]:.1f} {pts[0,1]:.1f}" + "".join(f" L {x:.1f} {y:.1f}" for x, y in pts[1:]) + " Z"
        paths.append(d)
        x, y, bw, bh, cx, cy, area = m
        meta.append({"cx": cx * s + ox, "cy": cy * s + oy, "area": area, "w": bw * s, "h": bh * s})
    return paths, meta


# --- semantic naming ---

def name_butterfly(meta: list[dict]) -> list[str]:
    ids = [""] * len(meta)
    used: set[int] = set()

    def assign(name: str, cond) -> None:
        cands = [i for i, m in enumerate(meta) if i not in used and cond(m)]
        if not cands:
            return
        i = max(cands, key=lambda j: meta[j]["area"])
        ids[i] = name
        used.add(i)

    assign("thorax", lambda m: 188 < m["cx"] < 212 and 150 < m["cy"] < 210)
    assign("head", lambda m: 192 < m["cx"] < 208 and m["cy"] < 145)

    for side, left in [("left", True), ("right", False)]:
        px = (lambda m, l=left: m["cx"] < 200) if left else (lambda m: m["cx"] > 200)
        uppers = sorted([i for i, m in enumerate(meta) if i not in used and px(m) and m["cy"] < 155], key=lambda i: -meta[i]["area"])
        lowers = sorted([i for i, m in enumerate(meta) if i not in used and px(m) and m["cy"] >= 155], key=lambda i: -meta[i]["area"])

        spots = [i for i in uppers if meta[i]["area"] < 700]
        panels = [i for i in uppers if i not in spots]
        for j, i in enumerate(sorted(spots, key=lambda k: meta[k]["cy"])[:1]):
            ids[i] = f"{side}UpperSpot"
            used.add(i)
        for j, i in enumerate(sorted(panels, key=lambda k: -meta[k]["area"])[:4]):
            nm = ["UpperBorder", "UpperPanelA", "UpperPanelB", "UpperPanelC"][j]
            ids[i] = f"{side}{nm}"
            used.add(i)

        dots = sorted([i for i in lowers if meta[i]["area"] < 650], key=lambda k: (meta[k]["cx"], meta[k]["cy"]))
        panels_l = [i for i in lowers if i not in dots]
        for j, i in enumerate(dots[:5]):
            ids[i] = f"{side}LowerDot{j+1}"
            used.add(i)
        for j, i in enumerate(sorted(panels_l, key=lambda k: -meta[k]["area"])[:3]):
            nm = ["LowerBorder", "LowerPanelA", "LowerPanelB"][j]
            ids[i] = f"{side}{nm}"
            used.add(i)

    n = 1
    for i in range(len(meta)):
        if not ids[i]:
            ids[i] = f"wingPart{n}"
            n += 1
    return ids


def name_house(meta: list[dict]) -> list[str]:
    ids = [""] * len(meta)
    used: set[int] = set()

    def assign(name, cond):
        cands = [i for i, m in enumerate(meta) if i not in used and cond(m)]
        if not cands:
            return
        i = max(cands, key=lambda j: meta[j]["area"])
        ids[i] = name
        used.add(i)

    tops = sorted([i for i, m in enumerate(meta) if m["cy"] < 55], key=lambda i: meta[i]["cx"])
    for nm, i in zip(["smoke3", "smoke2", "smoke1"], tops):
        if i not in used:
            ids[i] = nm
            used.add(i)

    assign("treeFoliage", lambda m: m["cx"] < 80 and m["cy"] < 150)
    assign("treeTrunk", lambda m: m["cx"] < 75 and 160 < m["cy"] < 230)
    assign("bushLeft", lambda m: m["cx"] < 55 and m["cy"] > 200)
    assign("bushRight", lambda m: 50 < m["cx"] < 110 and m["cy"] > 200)
    assign("gableRoof", lambda m: 100 < m["cx"] < 220 and m["cy"] < 130 and m["w"] > 60)
    assign("wingRoof", lambda m: m["cx"] > 230 and m["cy"] < 130)
    assign("chimney", lambda m: 150 < m["cx"] < 185 and m["cy"] < 70)
    assign("frontWall", lambda m: 95 < m["cx"] < 210 and 120 < m["cy"] < 230)
    assign("wingWall", lambda m: m["cx"] > 220 and 120 < m["cy"] < 250)
    assign("atticWindow", lambda m: 165 < m["cx"] < 195 and 95 < m["cy"] < 130)
    assign("door", lambda m: 125 < m["cx"] < 175 and m["cy"] > 180 and m["h"] > 35)
    assign("doorStep", lambda m: 115 < m["cx"] < 185 and m["cy"] > 235 and m["h"] < 20)
    assign("frontWindow", lambda m: 175 < m["cx"] < 215 and 160 < m["cy"] < 210)
    assign("wingWindowTop", lambda m: m["cx"] > 250 and 170 < m["cy"] < 220)
    assign("wingWindowBottom", lambda m: m["cx"] > 250 and m["cy"] > 220)

    n = 1
    for i in range(len(meta)):
        if not ids[i]:
            ids[i] = f"trim{n}"
            n += 1
    return ids


def name_giraffe(meta: list[dict]) -> list[str]:
    ids = [""] * len(meta)
    used: set[int] = set()

    def assign(name, cond):
        cands = [i for i, m in enumerate(meta) if i not in used and cond(m)]
        if not cands:
            return
        i = max(cands, key=lambda j: meta[j]["area"])
        ids[i] = name
        used.add(i)

    assign("sun", lambda m: m["cx"] < 70 and m["cy"] < 70)
    assign("cloudLeft", lambda m: m["cx"] < 130 and 40 < m["cy"] < 100)
    assign("cloudRight", lambda m: m["cx"] > 280 and m["cy"] < 100)
    assign("hillBack", lambda m: m["cy"] > 200 and m["area"] > 5000 and m["cy"] < 280)
    assign("hillFront", lambda m: m["cy"] > 250 and m["area"] > 4000)
    assign("treeLeftCanopy", lambda m: m["cx"] < 90 and 100 < m["cy"] < 200)
    assign("treeLeftTrunk", lambda m: m["cx"] < 95 and m["w"] < 30 and m["h"] > 25)
    assign("treeRightCanopy", lambda m: m["cx"] > 300 and 100 < m["cy"] < 200)
    assign("treeRightTrunk", lambda m: m["cx"] > 310 and m["w"] < 30 and m["h"] > 25)
    grasses = sorted([i for i, m in enumerate(meta) if i not in used and m["cy"] > 300 and m["area"] < 1500], key=lambda i: meta[i]["cx"])
    for j, i in enumerate(grasses[:4]):
        ids[i] = f"grass{j+1}"
        used.add(i)
    assign("body", lambda m: 130 < m["cx"] < 260 and 180 < m["cy"] < 280 and m["area"] > 2500)
    assign("neck", lambda m: 150 < m["cx"] < 240 and 70 < m["cy"] < 200 and m["h"] > 60)
    assign("head", lambda m: 150 < m["cx"] < 250 and m["cy"] < 90 and m["area"] > 600)
    assign("earLeft", lambda m: m["cx"] < 175 and m["cy"] < 95)
    assign("earRight", lambda m: m["cx"] > 215 and m["cy"] < 100)
    assign("hornLeft", lambda m: 165 < m["cx"] < 185 and m["cy"] < 55)
    assign("hornRight", lambda m: 195 < m["cx"] < 215 and m["cy"] < 55)
    assign("hornTipLeft", lambda m: m["area"] < 400 and 165 < m["cx"] < 185 and m["cy"] < 50)
    assign("hornTipRight", lambda m: m["area"] < 400 and 195 < m["cx"] < 215 and m["cy"] < 50)
    assign("tail", lambda m: m["cx"] > 290 and 180 < m["cy"] < 260)
    assign("tailTuft", lambda m: m["cx"] > 310 and m["area"] < 600)

    legs = sorted([i for i, m in enumerate(meta) if i not in used and m["cy"] > 240 and 20 < m["w"] < 40 and m["h"] > 50], key=lambda i: meta[i]["cx"])
    for nm, i in zip(["legBackLeft", "legFrontLeft", "legBackRight", "legFrontRight"], legs[:4]):
        ids[i] = nm
        used.add(i)
    hoofs = sorted([i for i, m in enumerate(meta) if i not in used and m["cy"] > 320 and m["area"] < 800], key=lambda i: meta[i]["cx"])
    for nm, i in zip(["hoofBackLeft", "hoofFrontLeft", "hoofBackRight", "hoofFrontRight"], hoofs[:4]):
        ids[i] = nm
        used.add(i)

    spots = sorted([i for i, m in enumerate(meta) if i not in used and m["area"] < 1500 and 90 < m["cx"] < 280], key=lambda i: (meta[i]["cy"], meta[i]["cx"]))
    neck = [i for i in spots if meta[i]["cy"] < 200][:4]
    body = [i for i in spots if meta[i]["cy"] >= 200][:8]
    for j, i in enumerate(neck):
        ids[i] = f"neckSpot{j+1}"
        used.add(i)
    for j, i in enumerate(body):
        ids[i] = f"bodySpot{j+1}"
        used.add(i)

    n = 1
    for i in range(len(meta)):
        if not ids[i]:
            ids[i] = f"scene{n}"
            n += 1
    return ids


DECOR = {
    "butterfly": [
        "M 198 118 Q 172 92 152 72",
        "M 202 118 Q 228 92 248 72",
    ],
    "house": [
        "M 184 116 V156 M164 136 H204",
        "M 214 252 V296 M192 274 H236",
        "M 304 248 V292 M282 270 H326",
        "M 304 298 V342 M282 320 H326",
        "M 140 328 L 140 268 Q 140 238 156 238 Q 172 238 172 268 L 172 328",
        '<circle class="decor-line" cx="142" cy="288" r="5" fill="#111"/>',
    ],
    "giraffe": [
        '<circle class="decor-line" cx="208" cy="118" r="4" fill="#111"/>',
        "M 72 42 L88 28 M76 48 L92 34 M80 54 L96 40 M84 60 L100 46",
        "M 178 88 L 192 102",
        "M 218 90 L 204 104",
    ],
}


def build_svg(title, paths, ids, decor):
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW} {VIEW}" aria-label="{title}">']
    for rid, d in zip(ids, paths):
        lines.append(
            f'  <path id="{rid}" class="paint-section" fill="#fff" stroke="#111" '
            f'stroke-width="{STROKE}" stroke-linejoin="round" d="{d}"/>'
        )
    for item in decor:
        if item.startswith("<"):
            lines.append(f"  {item}")
        else:
            lines.append(
                f'  <path class="decor-line" fill="none" stroke="#111" stroke-width="3" '
                f'stroke-linecap="round" d="{item}"/>'
            )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def pdf_render(path: Path) -> np.ndarray:
    doc = fitz.open(path)
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    doc.close()
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)


def main():
    jobs = [
        ("butterfly", pdf_render(REFS / "butterfly.pdf"), 90, name_butterfly),
        ("house", load_gray(REFS / "house-ref.png"), 120, name_house),
        ("giraffe", crop_content(load_gray(REFS / "giraffe_img_0.png")), 100, name_giraffe),
    ]
    REFS.mkdir(parents=True, exist_ok=True)
    OUT = Path(__file__).resolve().parents[1] / "assets" / "pictures"
    OUT.mkdir(parents=True, exist_ok=True)

    for name, gray, min_a, namer in jobs:
        scale = (max(gray.shape) / 1000) ** 2
        regions = trace_regions(gray, min_a * scale)
        paths, meta = to_viewbox(regions)
        ids = namer(meta)
        # drop trim/scene/wingPart extras by merging into nearest? keep only catalog-like
        extras = [i for i, s in enumerate(ids) if re.search(r"(trim|scene|wingPart)\d+", s)]
        if extras:
            print(f"  {name}: {len(extras)} unmapped regions kept as extra ids")
        svg = build_svg(name.title(), paths, ids, DECOR.get(name, []))
        (OUT / f"{name}.svg").write_text(svg)
        print(f"{name}: {len(ids)} sections written")


if __name__ == "__main__":
    REFS = Path(__file__).resolve().parents[1] / "tmp" / "refs"
    OUT = Path(__file__).resolve().parents[1] / "assets" / "pictures"
    main()
