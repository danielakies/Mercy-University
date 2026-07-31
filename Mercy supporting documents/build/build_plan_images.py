"""Inline the floor plates as data URLs.

The dashboard reads pixel data off the plans to hit-test zones and build the stacked view.
A browser opened on a file:// path treats every local image as a separate origin, so drawing
one onto a canvas taints it and getImageData() throws. Data URLs are same-origin, which keeps
the dashboard working when it is opened by double-clicking the HTML instead of being served.
"""

import base64
import json
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent
PLATES = ["plan_refs/MH_G.png", "plan_refs/MH_1.png", "plan_refs/MH_2.png", "plan_refs/MH_3.png"]
OUT = DOCS / "plan_images.js"


def main():
    images = {}
    for rel in PLATES:
        path = DOCS / rel
        if not path.exists():
            raise SystemExit(f"missing plate: {path}")
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        images[rel] = f"data:image/png;base64,{data}"

    body = ",\n".join(f'  {json.dumps(k)}: {json.dumps(v)}' for k, v in images.items())
    OUT.write_text(f"window.MERCY_PLAN_IMAGES = {{\n{body}\n}};\n", encoding="utf-8")

    size = OUT.stat().st_size / 1024
    print(f"{len(images)} plates inlined -> plan_images.js ({size:,.0f} KB)")


if __name__ == "__main__":
    main()
