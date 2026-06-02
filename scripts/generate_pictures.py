#!/usr/bin/env python3
"""Generate butterfly, giraffe, and house SVGs from reference sources."""

from __future__ import annotations

import re
from pathlib import Path

import cv2
import fitz
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "tmp" / "refs"
OUT = ROOT / "assets" / "pictures"
VIEW = 400
STROKE = 3.5


def segment_regions(gray: np.ndarray, min_area: float) -> list[tuple[np.ndarray, tuple[float, float, float, float]]]:
    _, bw = cv2.threshold(cv2.GaussianBlur(gray, (3, 3), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    lines = cv2.dilate(255 - bw, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), 1)
    white = cv2.bitwise_and(bw, cv2.bitwise_not(lines))
    n, labels = cv2.connectedComponents(white)
    h, w = gray.shape
    out = []
    for lab in range(1, n):
        mask = (labels == lab).astype(np.uint8) * 255
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
        approx = cv2.approxPolyDP(cnt, max(2.0, 0.004 * peri), True)
        cx, cy = x + bw / 2, y + bh / 2
        out.append((approx, (x, y, bw, bh, cx, cy, area)))
    return out


def fit_paths(regions: list, padding: float = 0.04) -> tuple[list[str], list[dict]]:
    xs, ys = [], []
    for cnt, _meta in regions:
        for p in cnt.reshape(-1, 2):
            xs.append(float(p[0]))
            ys.append(float(p[1]))
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    pad_x, pad_y = (x1 - x0) * padding, (y1 - y0) * padding
    x0 -= pad_x
    y0 -= pad_y
    x1 += pad_x
    y1 += pad_y
    cw, ch = x1 - x0, y1 - y0
    s = VIEW / max(cw, ch)
    ox = (VIEW - cw * s) / 2 - x0 * s
    oy = (VIEW - ch * s) / 2 - y0 * s

    paths, meta = [], []
    for cnt, m in regions:
        pts = cnt.reshape(-1, 2).astype(float)
        pts[:, 0] = pts[:, 0] * s + ox
        pts[:, 1] = pts[:, 1] * s + oy
        d = f"M {pts[0,0]:.1f} {pts[0,1]:.1f}"
        for x, y in pts[1:]:
            d += f" L {x:.1f} {y:.1f}"
        d += " Z"
        paths.append(d)
        x, y, bw, bh, cx, cy, area = m
        meta.append(
            {
                "cx": cx * s + ox,
                "cy": cy * s + oy,
                "x": x * s + ox,
                "y": y * s + oy,
                "w": bw * s,
                "h": bh * s,
                "area": area,
            }
        )
    return paths, meta


def load_gray(path: Path, max_dim: int = 1400) -> np.ndarray:
    g = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if g is None:
        raise SystemExit(f"Cannot read {path}")
    h, w = g.shape
    if max(h, w) > max_dim:
        sc = max_dim / max(h, w)
        g = cv2.resize(g, (int(w * sc), int(h * sc)), interpolation=cv2.INTER_AREA)
    return g


def crop_to_content(gray: np.ndarray) -> np.ndarray:
    _, bw = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)
    inv = 255 - bw
    pts = cv2.findNonZero(inv)
    if pts is None:
        return gray
    x, y, w, h = cv2.boundingRect(pts)
    return gray[y : y + h, x : x + w]


def pick(meta: list[dict], assigned: set[int], cond) -> int | None:
    cands = [i for i, m in enumerate(meta) if i not in assigned and cond(m)]
    if not cands:
        return None
    cands.sort(key=lambda i: -meta[i]["area"])
    return cands[0]


def assign_house(meta: list[dict]) -> list[str]:
    ids = [""] * len(meta)
    used: set[int] = set()

    def set_id(i, name):
        ids[i] = name
        used.add(i)

    # top smoke / clouds by y
    tops = sorted([i for i, m in enumerate(meta) if m["cy"] < 70], key=lambda i: meta[i]["cx"])
    for name, i in zip(["smoke3", "smoke2", "smoke1"], tops[:3]):
        if i is not None:
            set_id(i, name)
    clouds = sorted([i for i, m in enumerate(meta) if i not in used and m["cy"] < 55], key=lambda i: meta[i]["cx"])
    # skip - house ref may not have separate clouds as fill regions

    i = pick(meta, used, lambda m: m["cx"] < 95 and m["cy"] < 160 and m["area"] > 2000)
    if i is not None:
        set_id(i, "treeFoliage")
    i = pick(meta, used, lambda m: m["cx"] < 80 and m["cy"] > 170 and m["h"] > 25)
    if i is not None:
        set_id(i, "treeTrunk")
    i = pick(meta, used, lambda m: m["cx"] < 75 and m["cy"] > 200)
    if i is not None:
        set_id(i, "bushLeft")
    i = pick(meta, used, lambda m: m["cx"] < 110 and m["cy"] > 200)
    if i is not None:
        set_id(i, "bushRight")

    i = pick(meta, used, lambda m: m["cy"] < 100 and m["cx"] > 150 and m["w"] > m["h"])
    if i is not None:
        set_id(i, "gableRoof")
    i = pick(meta, used, lambda m: m["cy"] < 120 and m["cx"] > 230 and m["w"] > 80)
    if i is not None:
        set_id(i, "wingRoof")
    i = pick(meta, used, lambda m: 150 < m["cx"] < 200 and m["cy"] < 60)
    if i is not None:
        set_id(i, "chimney")

    i = pick(meta, used, lambda m: 100 < m["cx"] < 200 and 130 < m["cy"] < 220 and m["area"] > 3000)
    if i is not None:
        set_id(i, "frontWall")
    i = pick(meta, used, lambda m: m["cx"] > 230 and 150 < m["cy"] < 250)
    if i is not None:
        set_id(i, "wingWall")

    i = pick(meta, used, lambda m: 160 < m["cx"] < 195 and 100 < m["cy"] < 140 and m["w"] < 35)
    if i is not None:
        set_id(i, "atticWindow")
    i = pick(meta, used, lambda m: 120 < m["cx"] < 165 and m["cy"] > 175 and m["h"] > 40)
    if i is not None:
        set_id(i, "door")
    i = pick(meta, used, lambda m: m["cy"] > 235 and 110 < m["cx"] < 180 and m["h"] < 15)
    if i is not None:
        set_id(i, "doorStep")
    i = pick(meta, used, lambda m: 175 < m["cx"] < 210 and 170 < m["cy"] < 210)
    if i is not None:
        set_id(i, "frontWindow")
    i = pick(meta, used, lambda m: m["cx"] > 250 and 170 < m["cy"] < 210)
    if i is not None:
        set_id(i, "wingWindowTop")
    i = pick(meta, used, lambda m: m["cx"] > 250 and m["cy"] > 210)
    if i is not None:
        set_id(i, "wingWindowBottom")

    n = 1
    for i in range(len(meta)):
        if not ids[i]:
            ids[i] = f"houseExtra{n}"
            n += 1
    return ids


def assign_butterfly(meta: list[dict]) -> list[str]:
    ids = [""] * len(meta)
    used: set[int] = set()

    def set_id(i, name):
        if i is None or i in used:
            return
        ids[i] = name
        used.add(i)

    body = pick(meta, used, lambda m: 175 < m["cx"] < 225 and 130 < m["cy"] < 210)
    set_id(body, "thorax")
    head = pick(meta, used, lambda m: 185 < m["cx"] < 215 and m["cy"] < 140)
    set_id(head, "head")

    for side, px in [("left", lambda m: m["cx"] < 195), ("right", lambda m: m["cx"] > 205)]:
        uppers = sorted(
            [i for i, m in enumerate(meta) if i not in used and px(m) and m["cy"] < 150],
            key=lambda i: (-meta[i]["area"], meta[i]["cy"]),
        )
        lowers = sorted(
            [i for i, m in enumerate(meta) if i not in used and px(m) and m["cy"] >= 150],
            key=lambda i: (-meta[i]["area"], meta[i]["cy"]),
        )
        spots = [i for i in uppers if meta[i]["area"] < 900]
        panels = [i for i in uppers if i not in spots]
        for j, i in enumerate(spots[:1]):
            set_id(i, f"{side}UpperSpot")
        for j, i in enumerate(sorted(spots[1:], key=lambda k: meta[k]["cy"])):
            set_id(i, f"{side}UpperSpot{j+2}")
        names = ["UpperBorder", "UpperPanelA", "UpperPanelB", "UpperPanelC"]
        for j, i in enumerate(panels[:4]):
            set_id(i, f"{side}{names[j]}")

        dots = [i for i in lowers if meta[i]["area"] < 750 and meta[i]["cy"] > 190]
        panels_l = [i for i in lowers if i not in dots]
        for j, i in enumerate(sorted(dots, key=lambda k: (meta[k]["cx"], meta[k]["cy"]))[:5]):
            set_id(i, f"{side}LowerDot{j+1}")
        lnames = ["LowerBorder", "LowerPanelA", "LowerPanelB"]
        for j, i in enumerate(panels_l[:3]):
            set_id(i, f"{side}{lnames[j]}")

    n = 1
    for i in range(len(meta)):
        if not ids[i]:
            ids[i] = f"butterflyExtra{n}"
            n += 1
    return ids


def assign_giraffe(meta: list[dict]) -> list[str]:
    ids = [""] * len(meta)
    used: set[int] = set()

    def set_id(i, name):
        if i is None or i in used:
            return
        ids[i] = name
        used.add(i)

    set_id(pick(meta, used, lambda m: m["cx"] < 70 and m["cy"] < 70), "sun")
    set_id(pick(meta, used, lambda m: m["cx"] < 120 and 50 < m["cy"] < 100), "cloudLeft")
    set_id(pick(meta, used, lambda m: m["cx"] > 280 and m["cy"] < 90), "cloudRight")
    set_id(pick(meta, used, lambda m: m["cy"] > 220 and m["area"] > 8000), "hillFront")
    set_id(pick(meta, used, lambda m: 170 < m["cy"] < 240 and m["area"] > 5000), "hillBack")

    for name, cond in [
        ("treeLeftCanopy", lambda m: m["cx"] < 90 and 120 < m["cy"] < 200),
        ("treeLeftTrunk", lambda m: m["cx"] < 95 and m["w"] < 25 and m["h"] > 30),
        ("treeRightCanopy", lambda m: m["cx"] > 300 and 120 < m["cy"] < 200),
        ("treeRightTrunk", lambda m: m["cx"] > 310 and m["w"] < 25 and m["h"] > 30),
    ]:
        set_id(pick(meta, used, cond), name)

    grasses = sorted(
        [i for i, m in enumerate(meta) if i not in used and m["cy"] > 300 and m["area"] < 1200],
        key=lambda i: meta[i]["cx"],
    )
    for j, i in enumerate(grasses[:4]):
        set_id(i, f"grass{j+1}")

    # legs by x bands
    legs = sorted(
        [i for i, m in enumerate(meta) if i not in used and m["cy"] > 250 and m["h"] > 40 and m["w"] < 35],
        key=lambda i: meta[i]["cx"],
    )
    leg_names = [
        "legBackLeft", "legFrontLeft", "legBackRight", "legFrontRight",
    ]
    hoof_names = ["hoofBackLeft", "hoofFrontLeft", "hoofBackRight", "hoofFrontRight"]
    for i, nm in zip(legs[:4], leg_names):
        set_id(i, nm)
    hoofs = sorted(
        [i for i, m in enumerate(meta) if i not in used and m["cy"] > 330 and m["area"] < 600],
        key=lambda i: meta[i]["cx"],
    )
    for i, nm in zip(hoofs[:4], hoof_names):
        set_id(i, nm)

    set_id(pick(meta, used, lambda m: m["cx"] > 300 and 200 < m["cy"] < 280 and m["w"] < 60), "tail")
    set_id(pick(meta, used, lambda m: m["cx"] > 320 and m["area"] < 500), "tailTuft")
    set_id(pick(meta, used, lambda m: 140 < m["cx"] < 260 and 200 < m["cy"] < 290 and m["area"] > 2000), "body")
    set_id(pick(meta, used, lambda m: 150 < m["cx"] < 240 and 80 < m["cy"] < 200 and m["h"] > 80), "neck")
    set_id(pick(meta, used, lambda m: 150 < m["cx"] < 250 and m["cy"] < 100 and m["area"] > 800), "head")
    set_id(pick(meta, used, lambda m: m["cx"] < 175 and m["cy"] < 90), "earLeft")
    set_id(pick(meta, used, lambda m: m["cx"] > 220 and m["cy"] < 95), "earRight")
    set_id(pick(meta, used, lambda m: 165 < m["cx"] < 185 and m["cy"] < 60), "hornLeft")
    set_id(pick(meta, used, lambda m: 200 < m["cx"] < 220 and m["cy"] < 60), "hornRight")
    set_id(pick(meta, used, lambda m: m["area"] < 350 and m["cy"] < 55), "hornTipLeft")
    set_id(pick(meta, used, lambda m: m["area"] < 350 and m["cy"] < 55 and m["cx"] > 200), "hornTipRight")

    spots = sorted(
        [i for i, m in enumerate(meta) if i not in used and m["area"] < 1200 and 100 < m["cx"] < 280],
        key=lambda i: (meta[i]["cy"], meta[i]["cx"]),
    )
    neck_spots = [i for i in spots if meta[i]["cy"] < 200][:4]
    body_spots = [i for i in spots if meta[i]["cy"] >= 200][:8]
    for j, i in enumerate(neck_spots):
        set_id(i, f"neckSpot{j+1}")
    for j, i in enumerate(body_spots):
        set_id(i, f"bodySpot{j+1}")

    n = 1
    for i in range(len(meta)):
        if not ids[i]:
            ids[i] = f"giraffeExtra{n}"
            n += 1
    return ids


def decor_for_windows() -> list[str]:
  return [
    'M 184 116 V156 M164 136 H204',
    'M 214 252 V296 M192 274 H236',
    'M 304 248 V292 M282 270 H326',
    'M 304 298 V342 M282 320 H326',
    'M 140 328 L 140 268 Q 140 238 156 238 Q 172 238 172 268 L 172 328',
    '<circle class="decor-line" cx="142" cy="288" r="5" fill="#111"/>',
  ]


def extract_pdf_antennae(pdf_path: Path) -> list[str]:
    doc = fitz.open(pdf_path)
    page = doc[0]
    ph = page.rect.height
    decor = []
    for d in page.get_drawings():
        if not d.get("fill"):
            continue
        items = d.get("items") or []
        if len(items) < 4:
            continue
        parts = []
        for it in items:
            if it[0] == "c":
                p1, p2, p3 = it[1], it[2], it[3]
                parts.append(f"C {p1.x:.1f} {ph-p1.y:.1f} {p2.x:.1f} {ph-p2.y:.1f} {p3.x:.1f} {ph-p3.y:.1f}")
        if parts:
            # scale roughly to 400 - butterfly pdf
            decor.append("M " + parts[0][2:] + " " + " ".join(parts))
    doc.close()
    return decor


def build_svg(title: str, paths: list[str], ids: list[str], decor: list[str]) -> str:
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


def generate_butterfly():
    src = REFS / "butterfly.pdf"
    doc = fitz.open(src)
    page = doc[0]
    mat = fitz.Matrix(180 / 72, 180 / 72)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    gray = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    gray = cv2.cvtColor(gray, cv2.COLOR_RGB2GRAY)
    doc.close()
    regions = segment_regions(gray, min_area=120 * (max(gray.shape) / 1000) ** 2)
    paths, meta = fit_paths(regions)
    ids = assign_butterfly(meta)
    decor = [
        "M 198 118 Q 175 95 155 75",
        "M 202 118 Q 225 95 245 75",
    ]
    return build_svg("Butterfly", paths, ids, decor), ids


def generate_house():
    gray = load_gray(REFS / "house-ref.png")
    regions = segment_regions(gray, min_area=150 * (max(gray.shape) / 1000) ** 2)
    paths, meta = fit_paths(regions)
    ids = assign_house(meta)
    decor = [
        "M 184 116 V156 M164 136 H204",
        "M 214 252 V296 M192 274 H236",
        "M 304 248 V292 M282 270 H326",
        "M 304 298 V342 M282 320 H326",
        "M 140 328 L 140 268 Q 140 238 156 238 Q 172 238 172 268 L 172 328",
    ]
    svg = build_svg("House", paths, ids, decor)
    svg = svg.replace(
        "</svg>",
        '  <circle class="decor-line" cx="142" cy="288" r="5" fill="#111"/>\n</svg>',
    )
    return svg, ids


def generate_giraffe():
    gray = crop_to_content(load_gray(REFS / "giraffe_img_0.png"))
    regions = segment_regions(gray, min_area=90 * (max(gray.shape) / 1000) ** 2)
    paths, meta = fit_paths(regions)
    ids = assign_giraffe(meta)
    decor = [
        "M 178 88 L 192 102",
        "M 218 90 L 204 104",
        '<circle class="decor-line" cx="210" cy="118" r="4" fill="#111"/>',
        "M 72 42 L88 28 M76 48 L92 34 M80 54 L96 40 M84 60 L100 46",
    ]
    return build_svg("Giraffe", paths, ids, decor), ids


def main():
    REFS.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    for name, gen in [
        ("butterfly", generate_butterfly),
        ("house", generate_house),
        ("giraffe", generate_giraffe),
    ]:
        svg, ids = gen()
        out = OUT / f"{name}.svg"
        out.write_text(svg)
        print(f"{name}: {len(ids)} sections -> {out}")


if __name__ == "__main__":
    main()
