// Dashboard facts assembled from the shared Mercy University source folder.
// Items with status "confirmed" are directly stated in the cited source.
window.MERCY_ANALYSIS = {
  departments: [],
  mep: [
    {
      discipline: "HVAC",
      title: "Admissions & Welcome Center modernization",
      detail: "The 2025 construction set is a partial second-floor + roof renovation in Main Hall: remove AHU1, AC1/AC2 and condensers CON1–3, then install 13 Mitsubishi indoor units (AC/1-1 through AC/1-13) with refrigerant piping, condensate and new distribution.",
      source: "20250509-MU_A&WC_ISSUED FOR CONSTRUCTION_MEP-FP S&S.pdf",
      sheets: "M060 / M100–M102 / M301",
      status: "confirmed"
    },
    {
      discipline: "HVAC",
      title: "New roof condensing units",
      detail: "ACCU-1 is scheduled at 72,000 Btu/h cooling and 80,000 Btu/h heating (model TUHYP0723AN40A); ACCU-2 at 144,000 / 160,000 Btu/h (TUHYE1443AN41AN). Both are 208 V, 3-phase Mitsubishi R-410A units.",
      source: "20250509-MU_A&WC_ISSUED FOR CONSTRUCTION_MEP-FP S&S.pdf",
      sheets: "M301.00",
      status: "confirmed"
    },
    {
      discipline: "Ventilation",
      title: "Existing dedicated outdoor-air systems",
      detail: "DOAS-1 and DOAS-2 remain as existing rooftop AAON units serving classrooms/offices, about 2,000 CFM each, with energy recovery and MERV-8 / MERV-13 filtration. The 2025 schedule lists them for reference only.",
      source: "20250509-MU_A&WC_ISSUED FOR CONSTRUCTION_MEP-FP S&S.pdf",
      sheets: "M301.00",
      status: "confirmed"
    },
    {
      discipline: "Heating plant",
      title: "Existing fossil-fuel heating path",
      detail: "The geothermal feasibility study describes an approximately 80% efficient oil or natural-gas boiler serving Main Hall, with campus heating-water piping nearby. No verified current boiler tag or capacity was found in the shared files.",
      source: "Mercy PON5614-5 MercyUniversityMainHall_FeasibilityStudyReport.pdf",
      sheets: "pp. 17 / 22",
      status: "confirmed"
    },
    {
      discipline: "Geothermal",
      title: "Proposed closed-loop borefield",
      detail: "Brightcore recommends 120 vertical boreholes at 500 ft depth and 20 ft spacing in the parking lot northwest of Main Hall, sized for full heating and cooling of the existing ~150,000 SF building plus a planned 52,085 SF addition.",
      source: "Mercy PON5614-5 MercyUniversityMainHall_FeasibilityStudyReport.pdf",
      sheets: "Exec summary; GEO-100 / GEO-101",
      status: "confirmed"
    },
    {
      discipline: "Geothermal",
      title: "Modeled loads and cost",
      detail: "Modeled peaks are 4,545 kBtu/h heating and 4,792 kBtu/h cooling. Report costs are about $4.5M for the ground loop and $10M for interior HVAC retrofit before incentives.",
      source: "Mercy PON5614-5 MercyUniversityMainHall_FeasibilityStudyReport.pdf",
      sheets: "pp. 3, 14–20",
      status: "confirmed"
    },
    {
      discipline: "Electrical / life safety",
      title: "2025 project-area upgrades",
      detail: "A&WC work includes second-floor power and lighting removals/new work, roof equipment feeds from panels PP1/PP2, and fire-alarm work on an existing Honeywell Farenhyt IFP-2100 system.",
      source: "20250509-MU_A&WC_ISSUED FOR CONSTRUCTION_MEP-FP S&S.pdf",
      sheets: "E060–E401; FA100",
      status: "confirmed"
    },
    {
      discipline: "Legacy systems",
      title: "2009 renovation record drawings",
      detail: "The HVAC, Electrical and Plumbing folders are 2009 renovation drawings (not the original 1960 set), documenting basement/first-floor work, packaged roof units and service notes such as an existing 800A 120/208V service.",
      source: "HVAC, Electrical and Plumbing folders",
      sheets: "M1–M7; E01–E12; PL1–PL3",
      status: "confirmed"
    }
  ],
  site: {
    address: "555 Broadway, Dobbs Ferry, NY 10522",
    context: "Westchester Campus on the east bank of the Hudson River, spanning the Villages of Dobbs Ferry and Irvington, west of Broadway / U.S. Route 9.",
    buildings: [
      "Main Hall", "Hudson Hall", "Victory Hall", "Mercy Hall",
      "Maher / Gratia Maher Hall", "Verrazzano Hall", "Mahoney Hall",
      "Tim and Lee Hall Pavilion"
    ],
    edges: [
      "Hudson River / Metro-North ROW",
      "Broadway / U.S. Route 9",
      "Old Croton Trailway State Park",
      "The Landing on the Water HOA"
    ],
    sources: [
      "MJ819.08_MercyCollege_bndy survey-Boundary Survey_WIP.pdf",
      "2-19-26AllUtilities11X17.pdf",
      "DF Site Overhead Image 2025.pdf",
      "Mercy PON5614-5 MercyUniversityMainHall_FeasibilityStudyReport.pdf",
      "SitePlans/SP1-SP11 (1959 historic)"
    ],
    notes: [
      "Boundary survey MJ819.08 (09/17/2025) is marked work-in-progress; it labels the principal campus buildings, drives, easements and property context.",
      "Campus utilities are shown on the C&S AllUtilities aerial: storm, sanitary, water, electrical, communications, gas/fuel and heating water, densest around Main Hall / Hudson Hall.",
      "Proposed geothermal borefield: 120 holes @ 500 ft, 20 ft spacing, NW Main Hall parking lot; stay 5 ft clear of storm drains and outside the MTA 200 ft rail buffer.",
      "Main Hall is about 150,000 SF (c. 1960) with a planned 52,085 SF addition noted in the feasibility study.",
      "Athletic facilities west/northwest of Main Hall include a turf field, baseball diamond, tennis courts and pool.",
      "1959 SitePlans TIFs are historic Mount Mercy record drawings and are not a current utilities inventory.",
      "Total campus acreage appears on the survey AREA TABLE but was not reliably extractable from the PDF text layer."
    ]
  }
};
