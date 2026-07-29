# Mercy University Main Hall Dashboard

Open `mercy-main-hall-dashboard.html` in a web browser. The dashboard is self-contained and
works directly from the local folder; no web server or installation is required.

## Dashboard tabs

1. **Plan vs. Inventory** — 2021 program-zone plans by floor alongside the April 2025
   instructional room inventory and utilization metrics.
2. **Building Stack** — an exploded axonometric of the four floor plates with one program
   highlighted through the building.
3. **Full Building Analysis** — program mix, room types and uses, departmental/school use,
   utilization, and MEP/infrastructure information.
4. **Site & Campus** — boundary survey, utilities, aerial context, campus buildings, and
   geothermal/site coordination notes.

Each tab has its own URL fragment (`#plan`, `#stack`, `#analysis`, `#site`), so a particular
view can be bookmarked or pasted into an email.

## Interacting with the plan

On the **Plan vs. Inventory** tab the floor plan is a live canvas. Hover a colored area for its
zone name and area, click it to isolate it (the rest of the plan fades) and open a detail panel,
and click a legend row for the same result. Scroll to zoom, drag to pan, and use Fit to reset.
Press `Esc` or use Clear selection to deselect.

Clicking any room row in the inventory or utilization tables opens a record with area, seats,
utilization, and the schools that scheduled courses there. Where the room's program matches a
zone on its floor, **Show zone on plan** jumps to that floor and highlights the zone.

Zone-to-room links are matched by program name, not by surveyed location: the 2021 zone plan
carries no room numbers, so the detail panel labels these as candidates and the room record marks
the program zone as inferred.

## FICM classification

Every program zone is mapped to a Postsecondary Education Facilities Inventory and Classification
Manual (FICM) series in `Mercy supporting documents/ficm_categories.js`. Legends, the Building
Stack program picker, and the Full Building Analysis mix are ordered by series — Classrooms (100)
through Health Care (800), with Circulation (WWW), Building Service (XXX), and Mechanical (YYY)
kept at the bottom as nonassignable. The mapping follows the zone's stated program use; it is not
a surveyed FICM inventory.

## Building Stack tab

The four zone plans are redrawn as white sheets with navy linework and stacked in axonometric,
ground floor at the bottom. Pick a program in **Highlight program** and it is painted green on
every floor that contains it; floors without it are dimmed and their label greyed.

Clicking a plate selects it without leaving the tab: the other plates fade back and a panel opens
below the stack with that floor's zoned area, its assignable/nonassignable split, its programs
grouped by FICM series, and its inventoried rooms. Click the plate again, or Clear selection, to
deselect. To leave for the floor plan, use **Open plan →** next to the floor label or the
**Open on the Plan tab** button in the panel.

Tilt and Rotate reshape the view. Spread is a percentage of a plate's own projected height, so the
separation stays consistent at any angle; the whole stack is scaled to stay within about 1,500px
of height.

The callout on each painted region prorates that floor's legend total by painted area, so the
numbers add up to the legend figure but are estimates for any single region. The plates are
cropped per sheet, so they are centered rather than registered to a shared building grid.

## Generated data

- `Mercy supporting documents/room_categories.js` — program types and colors.
- `Mercy supporting documents/zone_plans.js` — floor definitions and zone totals.
- `Mercy supporting documents/schedules.js` — 53 Main Hall instructional rooms.
- `Mercy supporting documents/analysis_data.js` — departmental, MEP, and site facts.
- `Mercy supporting documents/ficm_categories.js` — FICM series definitions and zone-to-series map.
- `Mercy supporting documents/plan_refs/` — browser-ready plan and site images.
- `Mercy supporting documents/plan_images.js` — the four floor plates inlined as data URLs.

`plan_images.js` exists because the dashboard reads pixel data off the plans to hit-test zones.
A browser on a `file://` page treats each local image as its own origin, so drawing one onto a
canvas taints it and pixel reads fail. Data URLs are same-origin and keep the dashboard working
from a double-click. Re-run `build_plan_images.py` whenever the plates are regenerated.

Regenerate the zone and inventory data with:

```powershell
py "Mercy Dashboard\Mercy supporting documents\build\build_zones.py"
py "Mercy Dashboard\Mercy supporting documents\build\build_inventory.py"
py "Mercy Dashboard\Mercy supporting documents\build\build_plan_images.py"
```

Run those commands from the parent `unzipped files` folder, where the source PDFs currently
reside.

## Current data boundary

The 2021 source is a program-zone plan totaling 144,808 SF. The April 2025 utilization report
contains 53 Main Hall instructional spaces totaling 40,003 ASF and 1,494 seats. It is not a
complete current facilities inventory; a verified whole-building room schedule is still needed
for room-by-room reconciliation of offices, support, circulation, mechanical, and other
non-instructional space.

Room `MHLH` (the lecture hall) has no floor digit in its code and the report never states its
level, so it is listed without a floor rather than guessed.
