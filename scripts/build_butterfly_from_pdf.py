#!/usr/bin/env python3
"""Build assets/pictures/butterfly.svg from monarch PDF (outer silhouette only).

The shipped asset is hand-traced: one outer silhouette path plus simple inner paint
sections. This script must NOT import full PDF vector paths (they include wing veins
and stray segments such as H-263.493). Use --force to regenerate from the PDF via
OpenCV outer-boundary extraction only.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import cv2
import fitz
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "tmp" / "refs" / "butterfly-monarch.pdf"
OUT_SVG = ROOT / "assets" / "pictures" / "butterfly.svg"
VIEW = 400
STROKE = 3.5

# PDF art bounds (exclude footer copyright text)
ART = (111.0, 45.0, 681.0, 508.0)

# Inner paint sections (must match data/catalog.js)
PAINT_SECTIONS = """
  <circle id="head" class="paint-section" cx="200" cy="72" r="16" fill="#fff" stroke="#111" stroke-width="3.5"/>
  <ellipse id="body" class="paint-section" cx="200" cy="168" rx="14" ry="72" fill="#fff" stroke="#111" stroke-width="3.5"/>
  <circle id="leftUpperSpot" class="paint-section" cx="118" cy="118" r="22" fill="#fff" stroke="#111" stroke-width="3.5"/>
  <circle id="rightUpperSpot" class="paint-section" cx="282" cy="118" r="22" fill="#fff" stroke="#111" stroke-width="3.5"/>
  <path id="leftUpperBand" class="paint-section" fill="#fff" stroke="#111" stroke-width="3.5" stroke-linejoin="round"
    d="M 128 168 C 118 158 138 148 158 152 C 172 156 168 178 150 184 C 134 188 122 180 128 168 Z"/>
  <path id="rightUpperBand" class="paint-section" fill="#fff" stroke="#111" stroke-width="3.5" stroke-linejoin="round"
    d="M 272 168 C 282 158 262 148 242 152 C 228 156 232 178 250 184 C 266 188 278 180 272 168 Z"/>
  <circle id="leftLowerSpot1" class="paint-section" cx="108" cy="248" r="20" fill="#fff" stroke="#111" stroke-width="3.5"/>
  <circle id="leftLowerSpot2" class="paint-section" cx="138" cy="310" r="18" fill="#fff" stroke="#111" stroke-width="3.5"/>
  <ellipse id="leftLowerSpot3" class="paint-section" cx="168" cy="348" rx="22" ry="16" fill="#fff" stroke="#111" stroke-width="3.5"/>
  <circle id="rightLowerSpot1" class="paint-section" cx="292" cy="248" r="20" fill="#fff" stroke="#111" stroke-width="3.5"/>
  <circle id="rightLowerSpot2" class="paint-section" cx="262" cy="310" r="18" fill="#fff" stroke="#111" stroke-width="3.5"/>
  <ellipse id="rightLowerSpot3" class="paint-section" cx="232" cy="348" rx="22" ry="16" fill="#fff" stroke="#111" stroke-width="3.5"/>
""".strip()

ANTENNAE = """
  <path class="decor-line" fill="none" stroke="#111" stroke-width="3" stroke-linecap="round"
    d="M 192 56 Q 176 30 166 24"/>
  <path class="decor-line" fill="none" stroke="#111" stroke-width="3" stroke-linecap="round"
    d="M 208 56 Q 224 30 234 24"/>
""".strip()

# Hand-traced fallback when OpenCV contour is degenerate
HAND_SILHOUETTE = (
    "M 200 46 C 115 50 32 92 22 150 C 14 195 32 240 70 258 "
    "C 90 268 100 288 104 315 C 112 355 128 382 158 388 "
    "C 175 392 188 370 194 335 C 197 305 199 278 200 255 "
    "C 201 278 203 305 206 335 C 212 370 225 392 242 388 "
    "C 272 382 288 355 296 315 C 300 288 310 268 330 258 "
    "C 368 240 386 195 378 150 C 368 92 285 50 200 46 Z"
)


def extract_outer_silhouette(
    eps_factor: float = 0.009,
    pad: float = 0.06,
) -> str:
    """Morphological outer boundary of PDF line art — no interior strokes."""
    doc = fitz.open(PDF)
    page = doc[0]
    clip = fitz.Rect(*ART)
    mat = fitz.Matrix(300 / 72, 300 / 72)
    pix = page.get_pixmap(matrix=mat, clip=clip, alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    doc.close()

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    mask = (gray < 180).astype(np.uint8) * 255
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
    solid = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k, iterations=6)
    solid = cv2.morphologyEx(
        solid,
        cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)),
        iterations=2,
    )
    cnts, _ = cv2.findContours(solid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not cnts:
        return HAND_SILHOUETTE

    cnt = max(cnts, key=cv2.contourArea)
    h, w = solid.shape
    area_ratio = cv2.contourArea(cnt) / (h * w)
    if area_ratio < 0.15 or area_ratio > 0.85:
        return HAND_SILHOUETTE

    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, eps_factor * peri, True)
    if len(approx) < 8 or len(approx) > 80:
        return HAND_SILHOUETTE

    x0, y0 = w * pad, h * pad
    x1, y1 = w * (1 - pad), h * (1 - pad)
    cw, ch = x1 - x0, y1 - y0
    s = VIEW / max(cw, ch)
    ox = (VIEW - cw * s) / 2 - x0 * s
    oy = (VIEW - ch * s) / 2 - y0 * s

    pts = approx.reshape(-1, 2).astype(float)
    pts[:, 0] = np.clip(pts[:, 0] * s + ox, 12, 388)
    pts[:, 1] = np.clip(pts[:, 1] * s + oy, 12, 388)

    # Reject contours that spike toward the center (internal chord artifacts)
    cx, cy = 200.0, 200.0
    dists = np.hypot(pts[:, 0] - cx, pts[:, 1] - cy)
    if np.min(dists) < 35:
        return HAND_SILHOUETTE

    top_i = int(np.argmin(pts[:, 1]))
    pts = np.roll(pts, -top_i, axis=0)
    d = f"M {pts[0, 0]:.1f} {pts[0, 1]:.1f}"
    for x, y in pts[1:]:
        d += f" L {x:.1f} {y:.1f}"
    return d + " Z"


def build(silhouette_d: str | None = None) -> list[str]:
    if not PDF.exists():
        raise SystemExit(f"Missing reference PDF: {PDF}")

    d = silhouette_d or extract_outer_silhouette()
    ids = re.findall(r'id="([^"]+)"\s+class="paint-section"', PAINT_SECTIONS)

    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {VIEW} {VIEW}" aria-label="Butterfly">',
        "  <!-- Outer monarch silhouette only (no interior PDF strokes) -->",
        f'  <path id="silhouette" fill="#fff" stroke="#111" stroke-width="4" '
        f'stroke-linejoin="round" stroke-linecap="round" d="{d}"/>',
        "  <!-- Colorable inner shapes -->",
        *("  " + line for line in PAINT_SECTIONS.splitlines()),
        "  <!-- Antennae (fixed decor) -->",
        *("  " + line for line in ANTENNAE.splitlines()),
        "</svg>\n",
    ]
    OUT_SVG.write_text("\n".join(lines))
    return ids


def main() -> int:
    if "--force" not in sys.argv:
        print(
            "Refusing to overwrite butterfly.svg (use hand-traced production asset).\n"
            "Re-run with --force to regenerate outer silhouette + inner sections only.",
            file=sys.stderr,
        )
        return 1
    ids = build()
    print(f"Wrote {OUT_SVG} ({len(ids)} paint sections, outer contour only)")
    print("ids:", ", ".join(ids))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
