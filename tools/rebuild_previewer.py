#!/usr/bin/env python3
"""
Embeds the 4 master 3x8 transparent PNG sprite sheets into both the inline chat
artifact previewer and the standalone desktop/GitHub Pages HTML previewer.
"""

from __future__ import annotations
import base64
import io
import json
import re
from pathlib import Path
from PIL import Image

REPO = Path(__file__).resolve().parent.parent
SPRITES_DIR = REPO / "sprites"
BRAIN_DIR = Path(
    "/home/antigravity/.gemini/jetski/brain/v1/default/jetski_remote_agents_3p/ff7f66f4-8693-48db-8219-5ca19e947042"
)

ARTIFACT_HTML = BRAIN_DIR / "lancer_isometric_previewer.html"
REPO_HTML = REPO / "lancer_isometric_previewer.html"
REPO_INDEX = REPO / "index.html"

MAPPING = {
    "male_se": "male_lancer_isometric_se_full_sheet.png",
    "male_nw": "male_lancer_isometric_nw_full_sheet.png",
    "female_se": "female_lancer_isometric_se_full_sheet.png",
    "female_nw": "female_lancer_isometric_nw_full_sheet.png",
}


def main() -> None:
    data: dict[str, str] = {}
    for k, fname in MAPPING.items():
        im = Image.open(SPRITES_DIR / fname)
        small = im.resize((768, 456), Image.Resampling.NEAREST).quantize(
            colors=64, method=Image.Quantize.FASTOCTREE
        )
        buf = io.BytesIO()
        small.save(buf, format="PNG", optimize=True)
        data[k] = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
        print(f"Encoded {k}: {len(buf.getvalue())} bytes")

    js_assign = "window.SPRITE_SHEETS = " + json.dumps(data) + ";"
    pattern = re.compile(r"window\.SPRITE_SHEETS\s*=\s*\{.*?\};", re.DOTALL)

    for target in [ARTIFACT_HTML, REPO_HTML, REPO_INDEX]:
        if target.exists():
            html = target.read_text(encoding="utf-8")
            assert pattern.search(html), f"Missing SPRITE_SHEETS in {target}"
            updated = pattern.sub(lambda _: js_assign, html, count=1)
            target.write_text(updated, encoding="utf-8")
            print(f"Updated {target}")


if __name__ == "__main__":
    main()
