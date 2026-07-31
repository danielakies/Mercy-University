"""Build the Main Hall instructional room inventory used by the dashboard.

Source: Mercy University Instructional Utilization Report, April 2025,
pages 35-36 (general-purpose classrooms) and 41-42 (laboratories).
Only Main Hall (MH) records are included.
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import fitz

OUT = Path(__file__).resolve().parents[1] / "schedules.js"
REPORT = Path(__file__).resolve().parents[3] / (
    "Mercy University Instructional Utilization Report Final  SUBMITTED 22OCT2025 (003).pdf"
)

# room, ASF, seats, ASF/seat, course count, occupancy %, weekly hours, hours %, comment
CLASSROOMS = [
    ("MH111",724,36,20.1,11,55,29.7,80,""), ("MH113",1558,36,43.3,12,50,32.8,88,""),
    ("MH200",277,15,18.5,3,73,7.1,19,""), ("MH201",359,20,18.0,12,83,32.4,87,""),
    ("MH202",368,24,15.3,12,81,36.2,97,""), ("MH203",370,20,18.5,11,76,29.4,79,""),
    ("MH204",357,20,17.9,12,80,33.3,89,""), ("MH205",608,30,20.3,12,77,31.3,84,""),
    ("MH206",341,18,18.9,6,56,13.8,37,""), ("MH211",910,42,21.7,14,55,35.8,96,""),
    ("MH213",950,30,31.7,12,60,32.7,88,""), ("MH219",309,18,17.2,8,88,22.7,61,""),
    ("MH236",363,18,20.2,6,83,17.0,46,""), ("MH238",564,30,18.8,10,58,30.2,81,""),
    ("MH240",564,30,18.8,10,63,29.3,79,""), ("MH241",563,30,18.8,13,68,35.0,94,""),
    ("MH242",610,35,17.4,10,63,24.7,66,""), ("MH280",665,32,20.8,9,57,24.9,67,""),
    ("MH310",555,29,19.1,11,75,28.9,77,""), ("MH312",558,24,23.3,11,79,30.8,83,""),
    ("MH316",375,18,20.8,7,80,19.7,53,""), ("MH324",562,30,18.7,9,77,24.8,66,""),
    ("MH326",562,30,18.7,9,57,21.4,57,""), ("MH332",410,19,21.6,5,72,11.3,30,""),
    ("MH364",980,40,24.5,12,68,29.2,78,""), ("MH382",656,24,27.3,11,78,30.2,81,""),
    ("MHG2",1261,48,26.3,12,57,28.0,75,""), ("MHG3",1300,48,27.1,13,62,28.2,76,""),
    ("MHG4",840,28,30.0,10,76,29.5,79,""), ("MHLH",2164,178,12.2,8,22,19.3,52,""),
]

LABS = [
    ("MH217",582,20,29.1,11,94,31.5,84,""), ("MH239",576,18,32.0,9,77,21.4,57,""),
    ("MH277A",1252,24,52.2,8,61,20.0,54,""), ("MH277B",1430,24,59.6,5,57,12.0,32,""),
    ("MH279",621,20,31.1,10,99,28.3,76,""), ("MH302",993,24,41.4,7,44,23.8,64,""),
    ("MH305",1222,24,50.9,None,None,None,None,"Evening and weekend only."),
    ("MH309",953,20,47.7,7,79,19.8,53,""), ("MH311",1236,16,77.3,5,88,14.2,38,""),
    ("MH313",513,24,21.4,8,64,20.6,55,""), ("MH314",755,20,37.8,8,74,20.5,55,""),
    ("MH315",776,18,43.1,6,83,26.2,70,""), ("MH317",742,24,30.9,7,78,19.0,51,""),
    ("MH318",475,16,29.7,3,98,17.0,46,""), ("MH319",772,24,32.2,5,63,14.2,38,""),
    ("MH321",1045,24,43.5,7,79,19.8,53,""), ("MH322",596,8,74.5,3,46,17.0,46,""),
    ("MH323",840,20,42.0,1,90,5.7,15,""), ("MH376",885,24,36.9,2,60,4.0,11,""),
    ("MH378",970,40,24.3,4,39,6.7,18,""),
]

OPEN_LABS = [
    ("MH277C",189,6,31.5,None,None,None,None,"Open laboratory"),
    ("MH372",529,16,33.1,None,None,None,None,"Open laboratory"),
    ("MH374",1368,40,34.2,None,None,None,None,"Open laboratory"),
]

# The report groups the lecture hall with general-purpose classrooms, but the 2021 zone plan
# paints it as ASSEMBLY. Splitting it out lets the classroom figures reconcile between the two.
ROOM_TYPE_OVERRIDES = {
    "MHLH": ("Lecture Hall", "FICM 610"),
}

# Stated specialties from the Rickes report (not inferred from course schedules).
SPECIALTY = {
    "MHLH": "Lecture hall",
    "MH217": "Computer lab",
    "MH239": "Computer lab",
    "MH277A": "Nursing Basic Skills Lab",
    "MH277B": "Nursing Basic Skills Lab",
    "MH277C": "Nursing SIM Lab",
    "MH279": "Anatomy & Physiology Lab",
    "MH302": "Veterinary Technology Lab",
    "MH309": "General Chemistry Lab",
    "MH311": "Organic Chemistry Lab",
    "MH313": "Computer lab",
    "MH314": "Computer lab",
    "MH315": "Clinical Lab Science / Biology",
    "MH317": "Microbiology Lab",
    "MH318": "Physics Lab",
    "MH319": "A&P / Vet Anatomy Lab",
    "MH321": "General Biology Lab",
    "MH322": "Biology Research Lab",
    "MH323": "Cell Biology Lab",
    "MH372": "Health SIM / OT–PT Lab",
    "MH374": "Movement Lab / OT–PT",
    "MH376": "Shared Skills Lab",
    "MH378": "Shared Skills Lab",
}


def floor(room):
    # MHLH carries no floor digit and the report never states its level, so it stays unassigned.
    code = room.removeprefix("MH")
    if code.startswith("G"):
        return "G"
    return code[0] if code and code[0].isdigit() else ""


def record(row, room_type, ficm):
    room, area, seats, asf_seat, courses, occupancy, weekly, hours_pct, comment = row
    room_type, ficm = ROOM_TYPE_OVERRIDES.get(room, (room_type, ficm))
    return {
        "room": room, "floor": floor(room), "roomType": room_type, "ficm": ficm,
        "specialty": SPECIALTY.get(room, ""),
        "asf": area, "seats": seats, "asfPerSeat": asf_seat, "courseCount": courses,
        "seatOccupancy": occupancy, "weeklyHours": weekly, "hoursPercent": hours_pct,
        "comment": comment,
    }


SCHOOL_NAMES = {
    "School of Soc & Behavioral Sci": "School of Social & Behavioral Sciences",
    "School of Health & Natural Sci": "School of Health & Natural Sciences",
}


def scheduled_users():
    """Return course counts by room and school from the report's course-level appendix."""
    use = defaultdict(Counter)
    doc = fitz.open(REPORT)
    pattern = re.compile(
        r"Main Hall\n(MH(?:G\d|LH|\d+[A-Z]?))\n(School of[^\n]+)\n",
        re.I,
    )
    for page in doc:
        text = page.get_text()
        for room, school in pattern.findall(text):
            room = room.upper()
            school = SCHOOL_NAMES.get(school.strip(), school.strip())
            use[room][school] += 1
    return use


def main():
    rooms = (
        [record(r, "General-Purpose Classroom", "FICM 100") for r in CLASSROOMS]
        + [record(r, "Teaching Laboratory", "FICM 210") for r in LABS]
        + [record(r, "Open Laboratory", "FICM 220") for r in OPEN_LABS]
    )
    use = scheduled_users()
    for room in rooms:
        counts = use.get(room["room"], {})
        room["departments"] = sorted(counts, key=lambda k: (-counts[k], k))
        room["departmentUse"] = dict(counts)
    payload = {
        "building": "Main Hall",
        "buildingCode": "MH",
        "address": "555 Broadway, Dobbs Ferry, NY 10522",
        "source": "Mercy University Instructional Space Needs Analysis, April 2025",
        "scopeNote": "Instructional inventory only; non-instructional rooms are not included.",
        "departmentNote": (
            "Departments are scheduled course users in the Fall 2023 daytime appendix, "
            "not verified permanent room ownership."
        ),
        "rooms": rooms,
    }
    OUT.write_text(
        "// Generated by build/build_inventory.py from the April 2025 utilization report.\n"
        "window.MERCY_INVENTORY = " + json.dumps(payload, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"{len(rooms)} Main Hall rooms -> {OUT.name}")
    print(f"{sum(r['asf'] for r in rooms):,} instructional ASF; {sum(r['seats'] for r in rooms)} seats")
    print(f"{sum(bool(r['departments']) for r in rooms)} rooms have scheduled school/department users")


if __name__ == "__main__":
    main()
