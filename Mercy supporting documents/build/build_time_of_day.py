"""Digitise the Westchester time-of-day charts out of the Rickes utilization report.

Page 42 of the report plots "Number of Simultaneous Classrooms in Use - Fall 2023" as
seven small-multiple step charts (Mon-Sun), in 5-minute increments, with three series:
all classes, School of Health & Natural Sciences, and School of Nursing.  The figure is
vector art, so the polylines can be read back to real numbers instead of eyeballed.

Writes westchester_time_of_day.js for the dashboard.
"""
from __future__ import annotations

import json
import pathlib
import re
from collections import defaultdict

import fitz

HERE = pathlib.Path(__file__).resolve().parent
DOCS = HERE.parent
ROOT = DOCS.parent.parent
PDF = ROOT / "Mercy University Instructional Utilization Report Final  SUBMITTED 22OCT2025 (003).pdf"
OUT = DOCS / "westchester_time_of_day.js"

PAGE = 42
ACTIVE_CLASSROOMS = 41          # stated on the same page
STEP_MIN = 5                    # the chart's own increment
WINDOW = (8 * 60, 17 * 60 + 20)  # 8:00 AM - 5:20 PM instructional window (report p.7)

# Stroke colours used by the three series on page 42.
SERIES = [
    ("all",     (0.337, 0.380, 0.173), "All classes"),
    ("hns",     (0.000, 0.690, 0.314), "School of Health & Natural Sciences"),
    ("nursing", (1.000, 0.000, 0.000), "School of Nursing"),
]
COLOUR_TOL = 0.02

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})\s*(AM|PM)$")


def near(a, b, tol=COLOUR_TOL):
    return a is not None and b is not None and all(abs(x - y) <= tol for x, y in zip(a, b))


def to_minutes(text):
    m = TIME_RE.match(text.strip())
    if not m:
        return None
    h, mi, ap = int(m.group(1)), int(m.group(2)), m.group(3)
    if ap == "PM" and h != 12:
        h += 12
    if ap == "AM" and h == 12:
        h = 0
    return h * 60 + mi


def spans(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                t = s["text"].strip()
                if t:
                    x0, y0, x1, y1 = s["bbox"]
                    out.append({"t": t, "cx": (x0 + x1) / 2, "cy": (y0 + y1) / 2,
                                "x0": x0, "x1": x1, "y0": y0, "y1": y1})
    return out


def rules(page):
    """Long horizontal rules: the black one is the value-0 axis, grey ones are gridlines."""
    black, grey = set(), set()
    for d in page.get_drawings():
        col, w = d.get("color"), d.get("width") or 0
        if col is None or w > 1.2:
            continue
        for item in d["items"]:
            if item[0] != "l":
                continue
            a, b = item[1], item[2]
            if abs(a.y - b.y) > 0.3 or abs(a.x - b.x) < 120:
                continue
            seg = (round(a.y, 3), round(min(a.x, b.x), 2), round(max(a.x, b.x), 2))
            if max(col) < 0.05:
                black.add(seg)
            elif min(col) > 0.80 and max(col) < 0.92:
                grey.add(seg)
    return black, grey


def build_panels(page, sp):
    """One small multiple per black baseline; scale comes from the printed 19/38 gridlines."""
    black, grey = rules(page)
    panels = []
    for y0, x0, x1 in sorted(black):
        above = sorted({y for y, gx0, _gx1 in grey
                        if abs(gx0 - x0) < 2 and 0 < y0 - y < 90}, reverse=True)
        if len(above) < 2:
            continue
        # the two nearest gridlines are 19 and 38 rooms; they must be evenly spaced
        g19, g38 = above[0], above[1]
        s1, s2 = y0 - g19, g19 - g38
        if not (0.85 <= s1 / s2 <= 1.18):
            continue
        ticks = [s for s in sp
                 if to_minutes(s["t"]) is not None
                 and 2 < s["cy"] - y0 < 25
                 and x0 - 5 <= s["cx"] <= x1 + 5]
        if len(ticks) < 2:
            continue
        ticks.sort(key=lambda s: s["cx"])
        a, b = ticks[0], ticks[-1]
        panels.append({
            "y0": y0, "y38": g38, "left": x0, "right": x1,
            "px1": a["cx"], "px2": b["cx"],
            "t1": to_minutes(a["t"]), "t2": to_minutes(b["t"]),
        })
    # weekday captions are rotated and sit in the gutter immediately left of each panel
    labels = [s for s in sp if s["t"] in DAYS]
    for p in panels:
        best, bd = None, 1e9
        for s in labels:
            if not (p["left"] - 45 < s["cx"] < p["left"]):
                continue
            if not (p["y38"] - 20 < s["cy"] < p["y0"] + 10):
                continue
            d = abs(s["cy"] - (p["y0"] + p["y38"]) / 2)
            if d < bd:
                bd, best = d, s["t"]
        p["day"] = best
    return [p for p in panels if p["day"]]


def segments(page):
    """Flatten every stroked path into (colour, x0, y0, x1, y1) segments."""
    out = []
    for d in page.get_drawings():
        col = d.get("color")
        if col is None:
            continue
        for item in d["items"]:
            if item[0] == "l":
                a, b = item[1], item[2]
                out.append((col, a.x, a.y, b.x, b.y))
            elif item[0] == "c":
                pts = item[1:]
                for i in range(len(pts) - 1):
                    out.append((col, pts[i].x, pts[i].y, pts[i + 1].x, pts[i + 1].y))
    return out


def sample(panel, segs, colour):
    """Read a step polyline back into value-per-5-minute-bin."""
    x_per_min = (panel["px2"] - panel["px1"]) / (panel["t2"] - panel["t1"])
    y_per_val = (panel["y0"] - panel["y38"]) / 38.0
    top = panel["y38"] - 6
    bottom = panel["y0"] + 3

    bins = defaultdict(float)
    for col, ax, ay, bx, by in segs:
        if not near(col, colour):
            continue
        if not (panel["left"] <= ax <= panel["right"] and panel["left"] <= bx <= panel["right"]):
            continue
        if not (top <= ay <= bottom and top <= by <= bottom):
            continue
        # A step chart's verticals carry no new information; sample the horizontals.
        for px, py in ((ax, ay), (bx, by)):
            t = panel["t1"] + (px - panel["px1"]) / x_per_min
            v = (panel["y0"] - py) / y_per_val
            if v < -0.5:
                continue
            slot = int(round(t / STEP_MIN)) * STEP_MIN
            bins[slot] = max(bins[slot], max(0.0, v))
    return bins


def densify(bins):
    """Fill the 5-minute grid across the plotted range; gaps mean zero rooms in use."""
    if not bins:
        return []
    lo, hi = min(bins), max(bins)
    out = []
    for t in range(lo, hi + STEP_MIN, STEP_MIN):
        out.append([t, round(bins.get(t, 0.0), 1)])
    return out


def main():
    doc = fitz.open(PDF)
    page = doc[PAGE]
    sp = spans(page)
    panels = build_panels(page, sp)
    segs = segments(page)
    print(f"panels found: {[p['day'] for p in panels]}")

    days = {}
    for p in panels:
        series = {}
        for key, colour, _label in SERIES:
            series[key] = densify(sample(p, segs, colour))
        days[p["day"]] = series
        peaks = {k: (max(v for _, v in s) if s else 0) for k, s in series.items()}
        print(f"  {p['day']:<10} peak {peaks}")

    # Round to whole rooms; the source counts rooms, so fractions are digitising noise.
    for d in days.values():
        for k, s in d.items():
            for pt in s:
                pt[1] = round(pt[1])

    def window_avg(series):
        pts = [v for t, v in series if WINDOW[0] <= t <= WINDOW[1]]
        return round(100 * sum(pts) / len(pts) / ACTIVE_CLASSROOMS, 1) if pts else None

    weekday = [d for d in ["Monday", "Tuesday", "Wednesday", "Thursday"] if d in days]
    grid = sorted({t for d in weekday for t, _ in days[d]["all"]})
    combined = []
    for t in grid:
        vals = []
        for d in weekday:
            lut = dict(days[d]["all"])
            if t in lut:
                vals.append(lut[t])
        if vals:
            combined.append([t, round(sum(vals) / len(vals), 1)])

    data = {
        "source": "Rickes Associates, Mercy University Instructional Utilization Report "
                  "(submitted 22 Oct 2025), p.42 - 'Number of Simultaneous Classrooms in Use, "
                  "Fall 2023', Westchester Campus. Curves digitised from the report's vector artwork.",
        "campus": "Westchester",
        "term": "Fall 2023",
        "metric": "Classrooms in use at each 5-minute increment, as a share of the 41 active classrooms",
        "activeClassrooms": ACTIVE_CLASSROOMS,
        "stepMinutes": STEP_MIN,
        "window": {"start": WINDOW[0], "end": WINDOW[1], "label": "8:00 AM - 5:20 PM",
                   "hours": 9.33, "weeklyHours": 37.33,
                   "note": "Instructional window defined in the report (p.7): Monday-Thursday, "
                           "8:00 a.m. to 5:20 p.m., 37.33 hours per week."},
        "series": [{"key": k, "label": l} for k, _c, l in SERIES],
        "days": days,
        "weekdayAverage": combined,
        "windowAverage": {
            "all": window_avg(combined),
            **{d: window_avg(days[d]["all"]) for d in days},
        },
    }

    OUT.write_text(
        "/* Generated by build_time_of_day.py - do not edit by hand. */\n"
        "window.MERCY_TIME_OF_DAY = " + json.dumps(data, indent=1) + ";\n",
        encoding="utf-8")
    print("wrote", OUT, OUT.stat().st_size, "bytes")
    print("window averages:", data["windowAverage"])


if __name__ == "__main__":
    main()
