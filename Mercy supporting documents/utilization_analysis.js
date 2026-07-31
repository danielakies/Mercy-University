// Room utilization analysis framing from Rickes Associates,
// "Mercy University Instructional Space Needs Analysis," April 2025.
// Metrics and findings below focus on Main Hall (MH) rooms inventoried in that report.
window.MERCY_UTILIZATION = {
  source: "Mercy University Instructional Space Needs Analysis, April 2025 (Rickes Associates)",
  sourceFile: "Mercy University Instructional Utilization Report Final SUBMITTED 22OCT2025 (003).pdf",
  rawCsv: "Mercy supporting documents/main_hall_instructional_inventory.csv",
  scope: "Main Hall instructional rooms only — classrooms, teaching labs, open labs, and the lecture hall.",
  instructionalWindow: {
    label: "Fall 2023 day instructional window",
    hours: 37.33,
    days: "Monday–Thursday",
    start: "8:00 AM",
    end: "5:20 PM",
    note: "Weekends and evenings are excluded; they serve a subset of courses and are not the day-utilization benchmark."
  },
  benchmarks: {
    classroom: {
      asfPerSeat: { low: 20, high: 25, label: "ASF / Seat", note: "20–25 ASF/seat for general-purpose classrooms; ~30+ preferred for active learning." },
      seatOccupancy: { target: 70, label: "Seat occupancy", note: "Target balances efficiency with scheduling flexibility." },
      hourUtilization: { target: 70, weeklyHours: 26.1, label: "Hour utilization", note: "70% of the 37.33-hour day window = 26.1 weekly hours." }
    },
    laboratory: {
      asfPerSeat: { note: "Lab ASF/seat varies by specialty; no single campus target is stated for all lab types." },
      seatOccupancy: { target: 80, label: "Station occupancy", note: "Higher than classrooms because of specialization and function." },
      hourUtilization: { target: 50, weeklyHours: 18.7, label: "Hour utilization", note: "Labs typically use a lower hour target than classrooms to allow setup, cleanup, and prep." }
    }
  },
  findings: [
    {
      title: "Westchester classrooms are at the hour-utilization target",
      body: "Across the Westchester Campus, average day utilization of general-purpose classrooms was at the recommended 70% (~26 weekly hours). That indicates classroom count is roughly sufficient for current need, with pressure likely at peak times."
    },
    {
      title: "Main Hall drives most Westchester classroom load",
      body: "Main Hall holds the majority of Westchester’s general-purpose classrooms. Many MH rooms sit at or above the 26.1-hour target; a few (such as MH200) are well below, often reflecting size, location, or preference factors."
    },
    {
      title: "ASF per seat is tight for active learning",
      body: "Westchester’s average classroom ASF/seat is about 21 — just above the lower target edge. That supports lecture-style teaching but can limit active-learning layouts. Fixed-seat auditoriums such as MHLH fall below the target by design."
    },
    {
      title: "Seat occupancy is near target in Main Hall classrooms",
      body: "Main Hall general-purpose classrooms average near the 70% seat-occupancy target. The lecture hall (MHLH) is much lower (~22%), which is typical for large fixed-seat halls and is usually excluded from campus averages."
    },
    {
      title: "Teaching labs have capacity in stations, not always in hours",
      body: "Westchester teaching-lab station occupancy averages below the 80% lab target in many cases, suggesting room to grow section size in some specialties. Hour utilization varies widely by lab type (SIM/skills vs science vs computer)."
    },
    {
      title: "Peak scheduling is near capacity campus-wide",
      body: "At Westchester, peak simultaneous classroom use approached the count of active classrooms, indicating pinch points when matching class size to room size — especially relevant to Main Hall’s preferred rooms."
    }
  ]
};
