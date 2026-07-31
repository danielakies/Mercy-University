"""Build Westchester campus utilization aggregates + CSV from the Rickes April 2025 report."""
import csv
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]

TAXONOMY = {
    "A": {"label": "A · 5–12 seats", "seats": "5–12", "color": "#F28620"},
    "B": {"label": "B · 13–18 seats", "seats": "13–18", "color": "#F9ED32"},
    "C": {"label": "C · 19–36 seats", "seats": "19–36", "color": "#49B0B9"},
    "D": {"label": "D · 37–74 seats", "seats": "37–74", "color": "#00AEEF"},
    "E": {"label": "E · 75–200 seats", "seats": "75–200", "color": "#3D54A5"},
    "F": {"label": "F · 201+ seats", "seats": "201+", "color": "#8B5E3C"},
}

# room, asf, seats, asf/seat, courses, occ%, weekly hrs, hrs%, comment
CLASSROOMS = [
    ("MEH030", 658, 30, 21.9, 5, 47, 14, 38, ""),
    ("MEH031", 920, 48, 19.2, 9, 36, 25.3, 68, ""),
    ("MEH032", 909, 48, 18.9, 11, 59, 30.3, 81, ""),
    ("MH111", 724, 36, 20.1, 11, 55, 29.7, 80, ""),
    ("MH113", 1558, 36, 43.3, 12, 50, 32.8, 88, ""),
    ("MH200", 277, 15, 18.5, 3, 73, 7.1, 19, ""),
    ("MH201", 359, 20, 18, 12, 83, 32.4, 87, ""),
    ("MH202", 368, 24, 15.3, 12, 81, 36.2, 97, ""),
    ("MH203", 370, 20, 18.5, 11, 76, 29.4, 79, ""),
    ("MH204", 357, 20, 17.9, 12, 80, 33.3, 89, ""),
    ("MH205", 608, 30, 20.3, 12, 77, 31.3, 84, ""),
    ("MH206", 341, 18, 18.9, 6, 56, 13.8, 37, ""),
    ("MH211", 910, 42, 21.7, 14, 55, 35.8, 96, ""),
    ("MH213", 950, 30, 31.7, 12, 60, 32.7, 88, ""),
    ("MH219", 309, 18, 17.2, 8, 88, 22.7, 61, ""),
    ("MH236", 363, 18, 20.2, 6, 83, 17, 46, ""),
    ("MH238", 564, 30, 18.8, 10, 58, 30.2, 81, ""),
    ("MH240", 564, 30, 18.8, 10, 63, 29.3, 79, ""),
    ("MH241", 563, 30, 18.8, 13, 68, 35, 94, ""),
    ("MH242", 610, 35, 17.4, 10, 63, 24.7, 66, ""),
    ("MH280", 665, 32, 20.8, 9, 57, 24.9, 67, ""),
    ("MH310", 555, 29, 19.1, 11, 75, 28.9, 77, ""),
    ("MH312", 558, 24, 23.3, 11, 79, 30.8, 83, ""),
    ("MH316", 375, 18, 20.8, 7, 80, 19.7, 53, ""),
    ("MH324", 562, 30, 18.7, 9, 77, 24.8, 66, ""),
    ("MH326", 562, 30, 18.7, 9, 57, 21.4, 57, ""),
    ("MH332", 410, 19, 21.6, 5, 72, 11.3, 30, ""),
    ("MH364", 980, 40, 24.5, 12, 68, 29.2, 78, ""),
    ("MH382", 656, 24, 27.3, 11, 78, 30.2, 81, ""),
    ("MHG2", 1261, 48, 26.3, 12, 57, 28, 75, ""),
    ("MHG3", 1300, 48, 27.1, 13, 62, 28.2, 76, ""),
    ("MHG4", 840, 28, 30, 10, 76, 29.5, 79, ""),
    ("MHLH", 2164, 178, 12.2, 8, 22, 19.3, 52, ""),
    ("VIC102", 431, 12, 35.9, 6, 92, 17, 46, ""),
    ("VIC103", 572, 36, 15.9, 11, 56, 30.8, 83, ""),
    ("VIC104", 784, 35, 22.4, 11, 54, 28.4, 76, ""),
    ("VIC105", 773, 39, 19.8, 8, 59, 23.4, 63, ""),
    ("VIC107", 767, 40, 19.2, 8, 46, 22.5, 60, ""),
    ("VIC108", 759, 35, 21.7, 7, 42, 19.5, 52, ""),
    ("VIC122", 766, 16, 47.9, None, None, None, None, "Unscheduled room."),
    ("VIC206", 1026, 40, 25.7, 12, 50, 32, 86, ""),
    ("VIC216", 332, 20, 16.6, 9, 87, 25, 67, ""),
]

TEACHING_LABS = [
    ("GMH112", None, 20, None, 1, 15, 2.8, 8, ""),
    ("MEH029", 249, 32, 7.8, 8, 83, 24.8, 66, ""),
    ("MH217", 582, 20, 29.1, 11, 94, 31.5, 84, ""),
    ("MH239", 576, 18, 32, 9, 77, 21.4, 57, ""),
    ("MH277A", 1252, 24, 52.2, 8, 61, 20, 54, ""),
    ("MH277B", 1430, 24, 59.6, 5, 57, 12, 32, ""),
    ("MH279", 621, 20, 31.1, 10, 99, 28.3, 76, ""),
    ("MH302", 993, 24, 41.4, 7, 44, 23.8, 64, ""),
    ("MH305", 1222, 24, 50.9, None, None, None, None, "Evening and weekend only."),
    ("MH309", 953, 20, 47.7, 7, 79, 19.8, 53, ""),
    ("MH311", 1236, 16, 77.3, 5, 88, 14.2, 38, ""),
    ("MH313", 513, 24, 21.4, 8, 64, 20.6, 55, ""),
    ("MH314", 755, 20, 37.8, 8, 74, 20.5, 55, ""),
    ("MH315", 776, 18, 43.1, 6, 83, 26.2, 70, ""),
    ("MH317", 742, 24, 30.9, 7, 78, 19, 51, ""),
    ("MH318", 475, 16, 29.7, 3, 98, 17, 46, ""),
    ("MH319", 772, 24, 32.2, 5, 63, 14.2, 38, ""),
    ("MH321", 1045, 24, 43.5, 7, 79, 19.8, 53, ""),
    ("MH322", 596, 8, 74.5, 3, 46, 17, 46, ""),
    ("MH323", 840, 20, 42, 1, 90, 5.7, 15, ""),
    ("MH376", 885, 24, 36.9, 2, 60, 4, 11, ""),
    ("MH378", 970, 40, 24.3, 4, 39, 6.7, 18, ""),
    ("VIC101", 1045, 23, 45.4, 4, 79, 11.3, 30, ""),
    ("VIC110", 775, 32, 24.2, 10, 61, 28.3, 76, ""),
    ("VIC114", 0, 40, 0, 10, 45, 28.2, 76, ""),
    ("VIC115", 1040, 16, 65, 2, 53, 5.7, 15, ""),
    ("VIC120", 766, 30, 25.5, 3, 28, 9, 24, ""),
    ("VIC123", 766, 16, 47.9, None, None, None, None, "Spring only."),
    ("VIC200", 441, 16, 27.6, 7, 63, 19.8, 53, ""),
    ("VIC203", 556, 18, 30.9, 8, 78, 24.7, 66, ""),
    ("VIC204", 549, 18, 30.5, 8, 62, 24.2, 65, ""),
    ("VIC207", 358, 15, 23.9, 4, 65, 11.3, 30, ""),
    ("VIC208", 803, 16, 50.2, 10, 76, 44.2, 118, ""),
    ("VIC210", 766, 12, 63.8, 5, 112, 22.1, 59, ""),
    ("VIC212", 786, 32, 24.6, 10, 88, 29.5, 79, ""),
    ("VIC214", 756, 32, 23.6, 12, 85, 33.3, 89, ""),
    ("VIC215", 855, 30, 28.5, 6, 62, 16.8, 45, ""),
]

OPEN_LABS = [
    ("MH277C", 189, 6, 31.5, None, None, None, None, "Open laboratory"),
    ("MH372", 529, 16, 33.1, None, None, None, None, "Open laboratory"),
    ("MH374", 1368, 40, 34.2, None, None, None, None, "Open laboratory"),
    ("VIC205B", 745, 10, 74.5, None, None, None, None, "Open laboratory"),
]

WINDOW = 37.33


def building_of(room):
    if room.startswith("MEH"):
        return "Mercy Hall"
    if room.startswith("MH"):
        return "Main Hall"
    if room.startswith("VIC"):
        return "Victory Hall"
    if room.startswith("GMH"):
        return "Gratia Mahony Hall"
    return "Other"


def taxonomy(seats):
    if seats is None:
        return None
    s = int(seats)
    if s <= 12:
        return "A"
    if s <= 18:
        return "B"
    if s <= 36:
        return "C"
    if s <= 74:
        return "D"
    if s <= 200:
        return "E"
    return "F"


def avg(vals):
    vals = [v for v in vals if v is not None]
    return round(sum(vals) / len(vals), 1) if vals else None


def make_room(row, room_type, ficm):
    room, asf, seats, asf_s, courses, occ, hrs, pct, comment = row
    tax = taxonomy(seats)
    util = pct
    if util is None and hrs is not None:
        util = round(100 * hrs / WINDOW, 1)
    return {
        "room": room,
        "building": building_of(room),
        "roomType": room_type,
        "ficm": ficm,
        "taxonomy": tax,
        "taxonomyLabel": TAXONOMY[tax]["label"] if tax else "Unmapped",
        "asf": asf,
        "seats": seats,
        "asfPerSeat": asf_s,
        "courseCount": courses,
        "seatOccupancy": occ,
        "weeklyHours": hrs,
        "hoursPercent": pct,
        "utilization": util,
        "comment": comment,
    }


def main():
    rooms = []
    for row in CLASSROOMS:
        r = make_room(row, "General-Purpose Classroom", "FICM 100")
        if r["room"] == "MHLH":
            r["roomType"] = "Lecture Hall"
            r["ficm"] = "FICM 610"
        rooms.append(r)
    rooms += [make_room(row, "Teaching Laboratory", "FICM 210") for row in TEACHING_LABS]
    rooms += [make_room(row, "Open Laboratory", "FICM 220") for row in OPEN_LABS]

    buildings = ["Main Hall", "Mercy Hall", "Victory Hall", "Gratia Mahony Hall"]
    by_building = {}
    for b in buildings:
        subset = [r for r in rooms if r["building"] == b]
        sched = [r for r in subset if r["utilization"] is not None]
        by_building[b] = {
            "rooms": len(subset),
            "scheduled": len(sched),
            "utilization": avg([r["utilization"] for r in sched]),
            "seatOccupancy": avg([r["seatOccupancy"] for r in sched]),
            "weeklyHours": avg([r["weeklyHours"] for r in sched]),
            "courses": sum((r["courseCount"] or 0) for r in subset),
            "seats": sum((r["seats"] or 0) for r in subset if r["seats"]),
            "asf": sum((r["asf"] or 0) for r in subset if r["asf"]),
            "weeklyHoursTotal": round(sum((r["weeklyHours"] or 0) for r in subset), 1),
        }

    by_tax = {}
    for code, meta in TAXONOMY.items():
        subset = [r for r in rooms if r["taxonomy"] == code]
        sched = [r for r in subset if r["utilization"] is not None]
        by_tax[code] = {
            **meta,
            "rooms": len(subset),
            "scheduled": len(sched),
            "utilization": avg([r["utilization"] for r in sched]),
            "seatOccupancy": avg([r["seatOccupancy"] for r in sched]),
            "weeklyHours": avg([r["weeklyHours"] for r in sched]),
            "courses": sum((r["courseCount"] or 0) for r in subset),
            "weeklyHoursTotal": round(sum((r["weeklyHours"] or 0) for r in subset), 1),
            "seats": sum((r["seats"] or 0) for r in subset if r["seats"]),
            "asf": sum((r["asf"] or 0) for r in subset if r["asf"]),
        }

    by_building_tax = {
        b: {
            code: avg([
                r["utilization"] for r in rooms
                if r["building"] == b and r["taxonomy"] == code and r["utilization"] is not None
            ])
            for code in TAXONOMY
        }
        for b in buildings
    }

    # Proxy for "management": registrar general classrooms vs specialty teaching labs.
    by_mgmt = {
        "General-purpose / registrar classrooms": {
            "rooms": sum(1 for r in rooms if r["roomType"] in ("General-Purpose Classroom", "Lecture Hall")),
            "utilization": avg([
                r["utilization"] for r in rooms
                if r["roomType"] in ("General-Purpose Classroom", "Lecture Hall") and r["utilization"] is not None
            ]),
            "courses": sum((r["courseCount"] or 0) for r in rooms if r["roomType"] in ("General-Purpose Classroom", "Lecture Hall")),
            "weeklyHoursTotal": round(sum((r["weeklyHours"] or 0) for r in rooms if r["roomType"] in ("General-Purpose Classroom", "Lecture Hall")), 1),
        },
        "Specialty teaching & open labs": {
            "rooms": sum(1 for r in rooms if r["roomType"] in ("Teaching Laboratory", "Open Laboratory")),
            "utilization": avg([
                r["utilization"] for r in rooms
                if r["roomType"] in ("Teaching Laboratory", "Open Laboratory") and r["utilization"] is not None
            ]),
            "courses": sum((r["courseCount"] or 0) for r in rooms if r["roomType"] in ("Teaching Laboratory", "Open Laboratory")),
            "weeklyHoursTotal": round(sum((r["weeklyHours"] or 0) for r in rooms if r["roomType"] in ("Teaching Laboratory", "Open Laboratory")), 1),
        },
    }

    by_mgmt_tax = {
        "General-purpose / registrar classrooms": {
            code: avg([
                r["utilization"] for r in rooms
                if r["roomType"] in ("General-Purpose Classroom", "Lecture Hall")
                and r["taxonomy"] == code and r["utilization"] is not None
            ])
            for code in TAXONOMY
        },
        "Specialty teaching & open labs": {
            code: avg([
                r["utilization"] for r in rooms
                if r["roomType"] in ("Teaching Laboratory", "Open Laboratory")
                and r["taxonomy"] == code and r["utilization"] is not None
            ])
            for code in TAXONOMY
        },
    }

    # Peak simultaneous classrooms by weekday from Westchester chart callouts (report p.40 / text).
    day_of_week = {
        "label": "Peak simultaneous classrooms in use — Fall 2023 (not a sample week)",
        "activeClassrooms": 41,
        "peakSimultaneous": 38,
        "note": (
            "No sample-week or multi-week reservation feed is in the source files. "
            "These figures are Fall 2023 peak simultaneous classroom counts by weekday "
            "from the Westchester utilization chart (Rickes report). Thursday reached the "
            "campus maximum of 38 of 41 active classrooms."
        ),
        "days": [
            {"day": "Monday", "peakRooms": 37, "utilization": round(100 * 37 / 41, 1)},
            {"day": "Tuesday", "peakRooms": 35, "utilization": round(100 * 35 / 41, 1), "note": "SHNS peak 11 classrooms"},
            {"day": "Wednesday", "peakRooms": 37, "utilization": round(100 * 37 / 41, 1)},
            {"day": "Thursday", "peakRooms": 38, "utilization": round(100 * 38 / 41, 1), "note": "Campus max; Nursing peak 6"},
            {"day": "Friday", "peakRooms": 20, "utilization": round(100 * 20 / 41, 1)},
            {"day": "Saturday", "peakRooms": 7, "utilization": round(100 * 7 / 41, 1)},
            {"day": "Sunday", "peakRooms": 5, "utilization": round(100 * 5 / 41, 1)},
        ],
    }

    payload = {
        "campus": "Westchester",
        "source": "Mercy University Instructional Space Needs Analysis, April 2025 (Rickes Associates)",
        "period": "Fall 2023 daytime instructional window (Mon–Thu 8:00 AM–5:20 PM, 37.33 hrs/week)",
        "utilizationMetric": (
            "Avg. percent of instructional-window hours scheduled "
            "(report “Avg. Percent Hrs. Fall Day” = weekly hours ÷ 37.33)"
        ),
        "taxonomy": TAXONOMY,
        "rooms": rooms,
        "byBuilding": by_building,
        "byTaxonomy": by_tax,
        "byBuildingTaxonomy": by_building_tax,
        "byManagement": by_mgmt,
        "byManagementTaxonomy": by_mgmt_tax,
        "dayOfWeek": day_of_week,
        "timeOfDay": {
            "available": False,
            "note": (
                "Campus-wide utilization-by-hour is only printed as chart images in the report "
                "and could not be extracted as a numeric series. Day-of-week peak simultaneous "
                "use is shown instead. A few Main Hall SIM/skills rooms have Fall 2024 hour grids, "
                "but those are not campus-wide."
            ),
        },
        "totals": {
            "rooms": len(rooms),
            "scheduled": len([r for r in rooms if r["utilization"] is not None]),
            "asf": sum((r["asf"] or 0) for r in rooms if r["asf"]),
            "seats": sum((r["seats"] or 0) for r in rooms if r["seats"]),
            "courses": sum((r["courseCount"] or 0) for r in rooms),
            "utilization": avg([r["utilization"] for r in rooms]),
            "weeklyHoursTotal": round(sum((r["weeklyHours"] or 0) for r in rooms), 1),
        },
    }

    js = OUT / "westchester_utilization.js"
    js.write_text(
        "// Generated from Westchester tables in the April 2025 Rickes utilization report.\n"
        "window.MERCY_WESTCHESTER = " + json.dumps(payload, indent=2) + ";\n",
        encoding="utf-8",
    )

    csv_path = OUT / "westchester_instructional_inventory.csv"
    fields = [
        "room", "building", "roomType", "ficm", "taxonomy", "taxonomyLabel",
        "asf", "seats", "asfPerSeat", "courseCount", "seatOccupancy",
        "weeklyHours", "hoursPercent", "utilization", "comment",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rooms:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in fields})

    print(f"{len(rooms)} rooms -> {js.name}, {csv_path.name}")
    print("taxonomy counts:", {k: v["rooms"] for k, v in by_tax.items()})
    print("building util:", {k: v["utilization"] for k, v in by_building.items()})
    print("mgmt util:", {k: v["utilization"] for k, v in by_mgmt.items()})


if __name__ == "__main__":
    main()
