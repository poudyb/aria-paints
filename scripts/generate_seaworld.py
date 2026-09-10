#!/usr/bin/env python3
"""Generate assets/pictures/seaworld.svg — the colorable Seaworld scene.

Layout follows the reference line art: octopus (top-left), fish (top-center),
dolphin (right, leaping with splash), crab (bottom-left), whale (bottom-center
with spout).

Structure of the generated SVG:
  1. Pre-colored blue wave bands (light at top -> deep at bottom). These are
     wrapped in a pointer-events:none group so taps on water do nothing.
  2. Per animal: white `paint-section` paths (colorable, ids listed in
     data/catalog.js) followed by a pointer-events:none decor group with the
     black outlines and face details drawn on top.

Neighbor groups for child-friendly tapping live in data/catalog.js.
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "pictures" / "seaworld.svg"

W, H = 1000, 600
INK = "#1f2430"


def f(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


def poly_path(pts, closed=True):
    d = f"M {f(pts[0][0])} {f(pts[0][1])} "
    d += " ".join(f"L {f(x)} {f(y)}" for x, y in pts[1:])
    return d + (" Z" if closed else "")


def smooth_closed(pts):
    """Catmull-Rom -> cubic Bezier, closed loop."""
    n = len(pts)
    d = f"M {f(pts[0][0])} {f(pts[0][1])} "
    for i in range(n):
        p0 = pts[(i - 1) % n]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d += (
            f"C {f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} "
            f"{f(p2[0])} {f(p2[1])} "
        )
    return d + "Z"


def bez(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
        y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
        out.append((x, y))
    return out


def ribbon(center, w0, w1):
    """Closed outline around a centerline with linearly tapering width."""
    n = len(center)
    left, right = [], []
    for i, (x, y) in enumerate(center):
        if i == 0:
            dx, dy = center[1][0] - x, center[1][1] - y
        elif i == n - 1:
            dx, dy = x - center[-2][0], y - center[-2][1]
        else:
            dx, dy = center[i + 1][0] - center[i - 1][0], center[i + 1][1] - center[i - 1][1]
        length = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / length, dx / length
        w = (w0 + (w1 - w0) * (i / (n - 1))) / 2.0
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return poly_path(left + right[::-1])


def curl_limb(anchor, c1, c2, curl_c, r0, a0, sweep, w0, w1, r1_frac=0.4):
    """Tapering limb: bezier descent from anchor, then an inward spiral curl."""
    entry = (curl_c[0] + r0 * math.cos(a0), curl_c[1] + r0 * math.sin(a0))
    center = bez(anchor, c1, c2, entry, 16)[:-1]
    n2 = 22
    for i in range(n2 + 1):
        t = i / n2
        a = a0 + sweep * t
        r = r0 * (1 - (1 - r1_frac) * t)
        center.append((curl_c[0] + r * math.cos(a), curl_c[1] + r * math.sin(a)))
    return ribbon(center, w0, w1)


def circle_d(cx, cy, r):
    return (
        f"M {f(cx - r)} {f(cy)} "
        f"A {f(r)} {f(r)} 0 1 0 {f(cx + r)} {f(cy)} "
        f"A {f(r)} {f(r)} 0 1 0 {f(cx - r)} {f(cy)} Z"
    )


# ---------------------------------------------------------------------------
# Water background: layered wavy bands, lighter blue at top -> deeper below.
# ---------------------------------------------------------------------------

def wave_edge(y0, amp, wl, phase):
    pts = []
    for x in range(0, W + 1, 8):
        pts.append((x, y0 + amp * math.sin(2 * math.pi * x / wl + phase)))
    return pts


def wave_band(y0, amp, wl, phase, color):
    pts = wave_edge(y0, amp, wl, phase)
    d = poly_path(pts, closed=False) + f" L {W} {H} L 0 {H} Z"
    return f'    <path fill="{color}" d="{d}"/>'


def wave_crest(y0, amp, wl, phase, x_from, x_to):
    pts = [p for p in wave_edge(y0, amp, wl, phase) if x_from <= p[0] <= x_to]
    return (
        '    <path fill="none" stroke="#ffffff" stroke-opacity="0.45" '
        f'stroke-width="4" stroke-linecap="round" d="{poly_path(pts, closed=False)}"/>'
    )


WAVES = [f'    <rect x="0" y="0" width="{W}" height="{H}" fill="#dff3fd"/>']
BANDS = [
    (78, 10, 260, 0.6, "#bfe7fb"),
    (168, 11, 230, 2.2, "#99d6f7"),
    (262, 12, 270, 4.1, "#6ec2f0"),
    (356, 12, 240, 1.3, "#48ade6"),
    (452, 13, 265, 3.4, "#2b93d4"),
    (534, 12, 235, 5.2, "#1a78bd"),
]
for y0, amp, wl, ph, color in BANDS:
    WAVES.append(wave_band(y0, amp, wl, ph, color))
WAVES.append(wave_crest(78, 10, 260, 0.6, 430, 700))
WAVES.append(wave_crest(262, 12, 270, 4.1, 60, 330))
WAVES.append(wave_crest(452, 13, 265, 3.4, 690, 970))


# ---------------------------------------------------------------------------
# Sections (white colorable shapes) and per-animal decor.
# sections: list of (id, d)  |  decor: list of raw SVG element strings
# ---------------------------------------------------------------------------

sections: list[tuple[str, str]] = []
decor: list[str] = []


def outline(d, width=5):
    decor.append(
        f'      <path fill="none" stroke="{INK}" stroke-width="{width}" '
        f'stroke-linejoin="round" stroke-linecap="round" d="{d}"/>'
    )


def add_section(sid, d, outline_width=5):
    sections.append((sid, d))
    outline(d, outline_width)


def dot(cx, cy, r, fill=INK):
    decor.append(f'      <circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}"/>')


def stroke_path(d, width=4, color=INK):
    decor.append(
        f'      <path fill="none" stroke="{color}" stroke-width="{width}" '
        f'stroke-linecap="round" stroke-linejoin="round" d="{d}"/>'
    )


# --------------------------- Octopus (top-left) ----------------------------

octo_head = smooth_closed([
    (193, 118), (200, 76), (230, 48), (265, 40), (300, 48), (330, 76),
    (337, 118), (330, 150), (307, 170), (265, 178), (223, 170), (200, 150),
])

# anchor, c1, c2, curl center, r0, entry angle, sweep, w0, w1
TENTACLES = [
    ((208, 162), (192, 196), (178, 210), (156, 244), 17, -0.9, -4.6, 26, 9),
    ((230, 170), (222, 200), (216, 218), (204, 262), 15, -0.7, 4.8, 24, 8),
    ((252, 174), (250, 204), (248, 222), (247, 268), 14, -1.2, -4.9, 23, 8),
    ((278, 174), (280, 204), (282, 222), (287, 268), 14, -1.9, 4.9, 23, 8),
    ((300, 170), (308, 200), (314, 218), (330, 262), 15, -2.4, -4.8, 24, 8),
    ((322, 162), (338, 196), (352, 210), (374, 244), 17, -2.2, 4.6, 26, 9),
]

add_section("seaworld-octoHead", octo_head)
for i, (anchor, c1, c2, cc, r0, a0, sweep, w0, w1) in enumerate(TENTACLES, 1):
    add_section(f"seaworld-octoTent{i}", curl_limb(anchor, c1, c2, cc, r0, a0, sweep, w0, w1), 4)

# Face
decor.append(f'      <ellipse cx="240" cy="106" rx="12" ry="14" fill="{INK}"/>')
decor.append(f'      <ellipse cx="290" cy="106" rx="12" ry="14" fill="{INK}"/>')
dot(236, 100, 4, "#fff")
dot(286, 100, 4, "#fff")
stroke_path("M 253 134 Q 265 144 277 134", 4.5)

# ----------------------------- Fish (top-center) ---------------------------

fish_body = smooth_closed([
    (502, 116), (520, 82), (558, 58), (606, 48), (656, 54), (696, 74),
    (720, 102), (726, 118), (712, 140), (680, 162), (634, 176), (584, 178),
    (538, 162), (510, 140),
])
fish_tail = (
    "M 720 108 C 742 84 756 58 754 34 C 780 52 794 80 792 102 "
    "L 764 118 C 790 134 798 158 792 180 C 768 176 742 150 718 128 Z"
)
fish_fin_top = "M 584 62 C 594 30 614 12 638 8 C 630 26 627 44 631 60 Z"
fish_fin_bottom = (
    "M 592 176 C 586 196 592 212 606 220 C 613 206 614 192 610 177 Z "
    "M 648 172 C 651 192 661 204 675 208 C 675 194 669 180 659 169 Z"
)

add_section("seaworld-fishBody", fish_body)
add_section("seaworld-fishTail", fish_tail)
add_section("seaworld-fishFinTop", fish_fin_top, 4)
add_section("seaworld-fishFinBottom", fish_fin_bottom, 4)

dot(548, 102, 11)
dot(552, 98, 4, "#fff")
# open smiling mouth (kept white like the line art)
decor.append(
    f'      <path fill="#fff" stroke="{INK}" stroke-width="4" stroke-linejoin="round" '
    'd="M 594 130 C 614 124 636 128 648 142 C 630 150 606 148 594 138 C 590 134 590 132 594 130 Z"/>'
)

# ------------------------- Dolphin (right, leaping) -------------------------

dolphin_body = smooth_closed([
    (752, 300), (762, 270), (784, 246), (814, 232), (850, 228), (886, 240),
    (914, 264), (933, 298), (939, 338), (931, 378), (913, 416), (894, 450),
    (872, 428), (852, 392), (838, 356), (824, 326), (804, 308), (776, 306),
])
dolphin_belly = smooth_closed([
    (770, 308), (794, 314), (814, 332), (828, 360), (840, 394), (856, 428),
    (876, 450), (886, 458), (872, 456), (850, 436), (832, 402), (820, 368),
    (806, 338), (788, 320), (768, 314),
])
dolphin_dorsal = "M 828 240 C 840 212 864 198 890 198 C 871 216 860 234 858 250 Z"
dolphin_flipper = "M 806 320 C 788 338 780 358 785 376 C 801 365 814 348 820 331 Z"
dolphin_tail = (
    "M 898 438 C 878 448 856 448 838 436 C 845 458 862 472 884 477 "
    "C 875 493 875 512 886 527 C 896 512 910 501 926 499 "
    "C 918 482 911 462 908 447 C 905 439 902 436 898 438 Z"
)
dolphin_splash = (
    "M 846 500 C 838 516 843 530 856 534 C 866 524 864 508 855 498 Z "
    "M 926 538 C 920 552 926 564 938 566 C 946 556 943 542 935 534 Z "
    + circle_d(824, 540, 8) + " " + circle_d(956, 508, 7) + " " + circle_d(902, 560, 6)
)

add_section("seaworld-dolphinBody", dolphin_body)
add_section("seaworld-dolphinBelly", dolphin_belly, 4)
add_section("seaworld-dolphinFinDorsal", dolphin_dorsal, 4)
add_section("seaworld-dolphinFlipper", dolphin_flipper, 4)
add_section("seaworld-dolphinTail", dolphin_tail, 4)
add_section("seaworld-dolphinSplash", dolphin_splash, 4)

dot(812, 282, 9)
dot(816, 278, 3.5, "#fff")
stroke_path("M 752 302 C 770 318 794 324 814 318", 4.5)  # smile
stroke_path("M 758 314 C 764 324 774 330 786 331", 4)    # lower jaw

# ---------------------------- Crab (bottom-left) ----------------------------

crab_body = smooth_closed([
    (50, 462), (60, 428), (88, 408), (145, 400), (202, 408), (230, 428),
    (240, 462), (232, 494), (202, 516), (145, 524), (88, 516), (58, 494),
])
crab_claw_left = (
    "M 76 428 C 48 436 22 422 14 396 C 6 368 20 342 44 334 "
    "L 36 306 L 60 322 C 82 330 94 352 90 378 C 87 400 84 416 76 428 Z "
    "M 60 356 L 52 338"
)
crab_claw_right = (
    "M 214 428 C 242 436 268 422 276 396 C 284 368 270 342 246 334 "
    "L 254 306 L 230 322 C 208 330 196 352 200 378 C 203 400 206 416 214 428 Z "
    "M 230 356 L 238 338"
)


def leg(p0, p1, p2, w0=15, w1=6):
    return ribbon(bez(p0, ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2), p1, p2, 14), w0, w1)


crab_legs_left = " ".join([
    leg((56, 462), (30, 466), (8, 484)),
    leg((63, 492), (38, 506), (18, 530)),
    leg((88, 515), (64, 536), (48, 558)),
])
crab_legs_right = " ".join([
    leg((234, 462), (260, 466), (282, 484)),
    leg((227, 492), (252, 506), (272, 530)),
    leg((202, 515), (226, 536), (242, 558)),
])

# Body first, smaller pieces after: later paint-sections win pointer hits, so
# the claws/legs/eyes keep their generous tap halos over the big body.
add_section("seaworld-crabBody", crab_body)
add_section("seaworld-crabClawLeft", crab_claw_left, 4.5)
add_section("seaworld-crabClawRight", crab_claw_right, 4.5)
add_section("seaworld-crabLegsLeft", crab_legs_left, 4)
add_section("seaworld-crabLegsRight", crab_legs_right, 4)
sections.append(("seaworld-crabEyeLeft", circle_d(118, 428, 14)))
outline(circle_d(118, 428, 14), 4)
sections.append(("seaworld-crabEyeRight", circle_d(172, 428, 14)))
outline(circle_d(172, 428, 14), 4)

dot(121, 430, 6)
dot(175, 430, 6)
stroke_path("M 128 466 Q 145 480 162 466", 4.5)  # smile

# ------------------------- Whale (bottom-center) ----------------------------

whale_body = smooth_closed([
    (372, 462), (378, 428), (398, 398), (434, 378), (480, 370), (528, 374),
    (566, 390), (592, 414), (604, 442), (606, 468), (596, 492), (562, 512),
    (504, 522), (440, 522), (396, 508), (376, 486),
])
whale_belly = smooth_closed([
    (390, 480), (436, 504), (494, 512), (550, 502), (586, 478), (592, 490),
    (560, 510), (502, 520), (442, 520), (398, 506), (378, 486),
])
whale_tail = (
    "M 596 470 C 620 452 630 426 624 396 C 640 410 650 430 650 448 "
    "C 664 438 682 436 696 444 C 690 472 664 490 632 492 "
    "C 618 493 605 484 596 470 Z"
)
whale_spout = (
    "M 442 368 C 434 348 422 338 407 336 C 421 327 436 331 447 342 "
    "C 447 322 456 305 471 299 C 464 314 464 331 469 344 "
    "C 480 333 495 329 508 334 C 493 340 482 351 477 368 Z"
)

add_section("seaworld-whaleBody", whale_body)
add_section("seaworld-whaleBelly", whale_belly, 4)
add_section("seaworld-whaleTail", whale_tail)
add_section("seaworld-whaleSpout", whale_spout, 4)

dot(416, 442, 8)
dot(419, 438, 3, "#fff")
stroke_path("M 402 466 Q 414 476 428 470", 4.5)   # smile
stroke_path("M 470 506 C 484 496 502 496 514 506", 4)  # flipper hint
dot(392, 316, 5)
dot(510, 306, 4)

# ---------------------------------------------------------------------------
# Assemble the SVG.
# ---------------------------------------------------------------------------

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" aria-label="Seaworld">',
    '  <g class="decor-line" pointer-events="none">',
    *WAVES,
    "  </g>",
]

for sid, d in sections:
    parts.append(f'  <path id="{sid}" class="paint-section" fill="#fff" d="{d}"/>')

parts.append('  <g class="decor-line" pointer-events="none">')
parts.extend(decor)
parts.append("  </g>")
parts.append("</svg>")

OUT.write_text("\n".join(parts) + "\n")
print(f"wrote {OUT} ({len(sections)} paint sections)")
