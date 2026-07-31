"""Extract the Main Hall zone standard and zone plans from the 2021 zone drawings.

Source: "2021 10 26 Final Main Hall Updated Floorplan Zones.pdf" (Noelker and Hull, NHA #20084).
Each page is one floor: a legend of colour swatches with zone names and square footages, and
the plan drawn as flat colour fills in those same colours.

The colour fills in the PDF are rectangles clipped to complex outlines, which do not survive
vector extraction cleanly. Instead each floor is rendered to a flat PNG and the dashboard
resolves a zone by sampling the pixel colour under the cursor. Interior pixels are flat, so
the lookup is exact.

Writes room_categories.js, zone_plans.js and plan_refs/MH_<floor>.png.
"""
import json
from collections import Counter
from pathlib import Path

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parents[1]
SRC = ROOT / "2021 10 26 Final Main Hall Updated Floorplan Zones.pdf"

DPI = 200
SCALE = DPI / 72.0

FLOORS = [
    {"page": 0, "id": "1", "label": "First Floor"},
    {"page": 1, "id": "2", "label": "Second Floor"},
    {"page": 2, "id": "3", "label": "Third Floor"},
    {"page": 3, "id": "G", "label": "Ground Floor"},
]

# Same program, inconsistent legend wording across sheets (3rd floor used the longer form).
NAME_ALIASES = {
    "GENERAL USE CLASSROOMS": "GENERAL CLASSROOMS",
}

def canon_name(name: str) -> str:
    return NAME_ALIASES.get(name.upper(), name)

# The legend block, in PDF points. Masked out before the plan colours are counted.
LEGEND_BOX = (470, 0, 920, 236)
SWATCH_MAX = 20
# Width of one legend column: enough to reach the right-aligned SF figure, not the next column.
LEGEND_COL_W = 200
# Greys, white and black are drawing linework rather than zone fills.
MIN_ZONE_PX = 400
MAX_COLOUR_DIST = 110
# A matched fill must cover at least this share of the pixels its stated area implies.
MIN_AREA_RATIO = 0.3


def hexof(c):
    return "#%02X%02X%02X" % tuple(c)


def is_linework(c):
    """Pure greys (including white and black) are drawing linework, never a zone fill."""
    r, g, b = c
    return r == g == b


def swatch_colour(im, name_x0, y0):
    """Sample the colour swatch printed just left of a legend label.

    Swatch positions vary by sheet and one of them is missing from the PDF image list
    altogether, so the strip is sampled off the render rather than off the image bbox.
    """
    box = (
        int((name_x0 - 24) * SCALE), int((y0 - 1) * SCALE),
        int((name_x0 - 6) * SCALE), int((y0 + 15) * SCALE),
    )
    counts = Counter(im.crop(box).convert("RGB").getdata())
    for c, _ in counts.most_common():
        if not is_linework(c):
            return c
    return None


def legend_rows(page, im):
    """Read the legend as text rows, then sample each row's swatch colour off the render.

    A line can hold two legend entries side by side, and a long zone name wraps onto the
    line below. Entries are therefore split at each "SF" token rather than by column.
    """
    words = [w for w in page.get_text("words")
             if LEGEND_BOX[0] < w[0] < LEGEND_BOX[2] + 60 and w[1] < LEGEND_BOX[3]]
    lines = {}
    for w in words:
        lines.setdefault(round(w[1], 1), []).append(w)

    ordered = sorted(lines.items())
    rows, by_x = [], {}
    for y0, ws in ordered:
        ws.sort(key=lambda w: w[0])
        toks = [w[4] for w in ws]
        if not any(t.upper() == "SF" for t in toks):
            # No SF figure: this line continues the name of an entry started above.
            for w in ws:
                owner = by_x.get(round(w[0], 0))
                if owner is not None and 0 < y0 - owner["y"] < 16:
                    owner["name"] += " " + w[4]
            continue
        entry = []
        for w in ws:
            if w[4].upper() == "SF":
                if len(entry) >= 2:
                    try:
                        sf = int(entry[-1][4].replace(",", ""))
                    except ValueError:
                        entry = []
                        continue
                    name_ws = entry[:-1]
                    x0 = name_ws[0][0]
                    r = {"name": " ".join(t[4] for t in name_ws).strip(" -"),
                         "sf": sf, "y": y0, "x": x0,
                         "swatch": swatch_colour(im, x0, y0)}
                    if r["name"]:
                        rows.append(r)
                        by_x[round(x0, 0)] = r
                entry = []
            else:
                entry.append(w)
    return rows


def legend_masks(rows):
    """Small per-row masks that do not erase plan areas behind a tall legend block."""
    return [
        (r["x"] - 30, r["y"] - 5, r["x"] + LEGEND_COL_W, r["y"] + 16)
        for r in rows
    ]


def plan_colours(im, boxes):
    """Count flat colour fills across the plan, ignoring the legend block and linework."""
    masked = im.copy()
    for box in boxes:
        masked.paste((255, 255, 255), tuple(int(v * SCALE) for v in box))
    counts = Counter(masked.convert("RGB").getdata())
    return {c: n for c, n in counts.items() if n >= MIN_ZONE_PX and not is_linework(c)}, masked


def dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def cluster_colours(colours, tol=14):
    """Fold anti-aliasing variants into the solid fill they came from.

    Without this a swatch can bind to a near-identical few-hundred-pixel variant instead
    of the real region: second-floor SIM LAB matched #B58D35 (602 px) over #B38C33 (357k).
    """
    reps = []
    for c, n in sorted(colours.items(), key=lambda kv: -kv[1]):
        for i, (rc, rn) in enumerate(reps):
            if dist(c, rc) <= tol:
                reps[i] = (rc, rn + n)
                break
        else:
            reps.append((c, n))
    return dict(reps)


def match(rows, colours, scale=None):
    """Greedily bind each legend swatch to its nearest unused plan colour.

    When a pixels-per-SF scale is supplied, a candidate must also be big enough to hold the
    zone's stated area. First-floor ASSEMBLY needs this: the auditorium fill is shaded well
    darker than its swatch, so on colour distance alone it loses to small look-alikes.
    """
    pairs = []
    for i, r in enumerate(rows):
        if r["swatch"] is None:
            continue
        for c, n in colours.items():
            d = dist(r["swatch"], c)
            if d > MAX_COLOUR_DIST:
                continue
            if scale is not None and n < MIN_AREA_RATIO * r["sf"] * scale:
                continue
            pairs.append((d, i, c, n))
    pairs.sort()
    used_row, used_col, out = set(), set(), {}
    for d, i, c, n in pairs:
        if i in used_row or c in used_col:
            continue
        used_row.add(i)
        used_col.add(c)
        out[i] = (c, n, d)
    return out


def bind(rows, colours):
    """Match on colour alone, calibrate pixels per SF from the confident hits, then rematch."""
    clustered = cluster_colours(colours)
    first = match(rows, clustered)
    ratios = sorted(
        first[i][1] / rows[i]["sf"]
        for i in first if rows[i]["sf"] > 200 and first[i][2] < 10
    )
    if not ratios:
        return clustered, first
    scale = ratios[len(ratios) // 2]
    return clustered, match(rows, clustered, scale)


def main():
    doc = fitz.open(SRC)
    refs = OUT / "plan_refs"
    refs.mkdir(exist_ok=True)

    floors, totals, colour_of = [], Counter(), {}

    # First pass: read every legend so a sheet whose swatch is missing from the PDF can
    # borrow the colour that the same zone uses elsewhere. Third-floor STORAGE / CLOSETS
    # has no swatch drawn at all.
    pages, known = [], {}
    for f in FLOORS:
        page = doc[f["page"]]
        pm = page.get_pixmap(dpi=DPI, colorspace=fitz.csRGB, alpha=False)
        im = Image.frombytes("RGB", (pm.width, pm.height), pm.samples)
        rows = legend_rows(page, im)
        for r in rows:
            if r["swatch"] is not None:
                known.setdefault(r["name"].upper(), r["swatch"])
        pages.append((f, page, im, rows))

    for f, page, im, rows in pages:
        for r in rows:
            if r["swatch"] is None:
                r["swatch"] = known.get(r["name"].upper())
                if r["swatch"] is not None:
                    print(f"  note: {f['label']} '{r['name']}' swatch missing from PDF, "
                          f"colour taken from another sheet")
        colours, masked = plan_colours(im, legend_masks(rows))
        colours, bound = bind(rows, colours)

        # Crop to the drawn plan so the dashboard is not mostly whitespace. Cropping the
        # masked image keeps the legend and title block out of the output.
        zone_cols = {bound[i][0] for i in bound}
        xs, ys = [], []
        px = masked.load()
        for y in range(0, masked.height, 3):
            for x in range(0, masked.width, 3):
                if px[x, y] in zone_cols:
                    xs.append(x)
                    ys.append(y)
        pad = int(14 * SCALE)
        box = (max(min(xs) - pad, 0), max(min(ys) - pad, 0),
               min(max(xs) + pad, masked.width), min(max(ys) + pad, masked.height))
        crop = masked.crop(box)
        img_name = f"MH_{f['id']}.png"
        crop.save(refs / img_name, optimize=True)

        zones, unmatched = [], []
        for i, r in enumerate(rows):
            if i not in bound:
                unmatched.append(r["name"])
                continue
            c, n, d = bound[i]
            name = canon_name(r["name"])
            zones.append({"name": name, "color": hexof(c), "sf": r["sf"], "px": n})
            totals[name] += r["sf"]
            colour_of.setdefault(name, hexof(c))
        zones.sort(key=lambda z: -z["sf"])

        # Pixel counts should track the printed square footages; a bad colour match shows up here.
        tot_px = sum(z["px"] for z in zones) or 1
        tot_sf = sum(z["sf"] for z in zones) or 1
        worst = max(
            (abs(z["px"] / tot_px - z["sf"] / tot_sf), z["name"]) for z in zones
        ) if zones else (0, "-")

        floors.append({
            "id": f["id"],
            "label": f["label"],
            "img": f"plan_refs/{img_name}",
            "w": crop.width,
            "h": crop.height,
            "sf": tot_sf,
            "zones": zones,
        })
        flag = " ".join(unmatched)
        print(f"{f['label']:<13} zones={len(zones):>2}/{len(rows):<2} sf={tot_sf:>6,} "
              f"img={crop.width}x{crop.height} maxdev={worst[0]*100:4.1f}% ({worst[1]}) {flag}")

    cats = sorted(totals.items(), key=lambda kv: -kv[1])
    with (OUT / "room_categories.js").open("w", encoding="utf-8") as fh:
        fh.write("// Mercy University Main Hall zone standard.\n")
        fh.write("// Generated from the 2021 Noelker and Hull zone plans by build/build_zones.py.\n")
        fh.write("window.MERCY_ZONES = ")
        json.dump([[n, colour_of[n]] for n, _ in cats], fh, indent=2)
        fh.write(";\n")
        fh.write("window.MERCY_ZONE_SF = ")
        json.dump(dict(cats), fh, indent=2)
        fh.write(";\n")

    with (OUT / "zone_plans.js").open("w", encoding="utf-8") as fh:
        fh.write("// Rendered zone plans; the dashboard resolves a zone by pixel colour.\n")
        fh.write("window.MERCY_ZONE_PLANS = ")
        json.dump({"building": "Main Hall", "dpi": DPI, "floors": floors}, fh, indent=1)
        fh.write(";\n")

    print(f"\n{len(cats)} zone types, {sum(totals.values()):,} SF total")


if __name__ == "__main__":
    main()
