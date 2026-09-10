#!/usr/bin/env python3
"""Seaworld is generated like giraffe: PNG overlay + traced paint sections.

Run: python3 scripts/generate_picture_sections.py seaworld
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.argv = [str(ROOT / "scripts" / "generate_picture_sections.py"), "seaworld"]
runpy.run_path(str(ROOT / "scripts" / "generate_picture_sections.py"), run_name="__main__")
