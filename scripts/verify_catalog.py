#!/usr/bin/env python3
"""Verify paint-section IDs in SVGs match data/catalog.js."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def extract_svg_ids(svg_path: Path) -> set[str]:
    text = svg_path.read_text()
    return set(re.findall(r'id="([^"]+)"\s+class="paint-section"', text))


def extract_catalog_ids(picture: str) -> set[str]:
    catalog = (ROOT / "data" / "catalog.js").read_text()
    m = re.search(rf"{picture}:\s*\{{[^}}]*sections:\s*\[([^\]]+)\]", catalog, re.S)
    if not m:
        raise SystemExit(f"Picture {picture!r} not found in catalog")
    return set(re.findall(r"'([^']+)'", m.group(1)))


def main() -> int:
    pictures = sys.argv[1:] or ["butterfly", "giraffe", "house"]
    failed = False
    for name in pictures:
        svg_path = ROOT / "assets" / "pictures" / f"{name}.svg"
        if not svg_path.exists():
            print(f"MISSING {svg_path}")
            failed = True
            continue
        svg_ids = extract_svg_ids(svg_path)
        cat_ids = extract_catalog_ids(name)
        only_svg = sorted(svg_ids - cat_ids)
        only_cat = sorted(cat_ids - svg_ids)
        ok = not only_svg and not only_cat
        status = "OK" if ok else "MISMATCH"
        print(f"{name}: {status}  svg={len(svg_ids)}  catalog={len(cat_ids)}")
        if only_svg:
            print(f"  in SVG only: {only_svg}")
            failed = True
        if only_cat:
            print(f"  in catalog only: {only_cat}")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
