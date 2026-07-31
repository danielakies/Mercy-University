// FICM space classification for Mercy Main Hall program zones.
// Mapped from the 2021 Noelker and Hull zone names onto Postsecondary Education
// Facilities Inventory and Classification Manual (FICM) series. Nonassignable
// categories (WWW / XXX / YYY) are listed last by design.
window.MERCY_FICM = {
  series: [
    {
      code: "100",
      label: "Classrooms",
      series: "100 series",
      assignable: true,
      description: "General purpose classrooms, lecture halls, recitation rooms, seminar rooms, and other spaces used primarily for scheduled nonlaboratory instruction."
    },
    {
      code: "200",
      label: "Laboratory Facilities",
      series: "200 series",
      assignable: true,
      description: "Rooms or spaces characterized by special purpose equipment or a specific configuration that ties instructional or research activities to a particular discipline or a closely related group of disciplines."
    },
    {
      code: "300",
      label: "Office Facilities",
      series: "300 series",
      assignable: true,
      description: "Offices and conference rooms specifically assigned to each of the various academic, administrative, and service functions."
    },
    {
      code: "400",
      label: "Study Facilities",
      series: "400 series",
      assignable: true,
      description: "Study rooms, stacks, open-stack reading rooms, and library processing spaces."
    },
    {
      code: "500",
      label: "Special Use Facilities",
      series: "500 series",
      assignable: true,
      description: "Military training rooms, athletic and physical education spaces, media production rooms, clinics, demonstration areas, field buildings, animal quarters, greenhouses, and other room categories that are sufficiently specialized in their primary activity or function to merit a unique room code."
    },
    {
      code: "600",
      label: "General Use Facilities",
      series: "600 series",
      assignable: true,
      description: "Assembly rooms, exhibition space, food facilities, lounges, merchandising facilities, recreational facilities, meeting rooms, child and adult care rooms, and other facilities that are characterized by a broader availability to faculty, students, staff, or the public than are special use areas."
    },
    {
      code: "700",
      label: "Support Facilities",
      series: "700 series",
      assignable: true,
      description: "Computing facilities, shops, central storage areas, vehicle storage areas, and central service space that provide centralized support for the activities of a campus."
    },
    {
      code: "800",
      label: "Health Care Facilities",
      series: "800 series",
      assignable: true,
      description: "Facilities used to provide patient care (human and animal)."
    },
    {
      code: "900",
      label: "Residential Facilities",
      series: "900 series",
      assignable: true,
      description: "Housing facilities for students, faculty, staff, and visitors to the campus."
    },
    {
      code: "000",
      label: "Unclassified Facilities",
      series: "000 series",
      assignable: true,
      description: "Inactive or unfinished areas, or areas in the process of conversion."
    },
    {
      code: "WWW",
      label: "Circulation Area",
      series: "WWW series",
      assignable: false,
      description: "Nonassignable spaces required for physical access to floors or subdivisions of space within the building, whether directly bounded by partitions or not."
    },
    {
      code: "XXX",
      label: "Building Service Area",
      series: "XXX series",
      assignable: false,
      description: "Nonassignable spaces used to support its cleaning and public hygiene functions."
    },
    {
      code: "YYY",
      label: "Mechanical Area",
      series: "YYY series",
      assignable: false,
      description: "Nonassignable spaces of a building designed to house mechanical equipment and utility services, and shaft areas."
    }
  ],
  // Zone-plan program name → FICM series code. Assignments follow the zone's
  // stated program use, not a surveyed FICM inventory.
  zones: {
    "GENERAL CLASSROOMS": "100",
    "SIM LAB": "200",
    "HEALTH & NATURAL SCIENCES": "200",
    "VET TECH": "200",
    "LIBRARY ADMINISTRATION": "300",
    "ADMISSIONS": "300",
    "STUDENT AFFAIRS": "300",
    "PROVOST / COLLEGE-WIDE PROGRAMS": "300",
    "FACULTY & ADJUNCT": "300",
    "PACT": "300",
    "SECURITY SERVICES": "300",
    "VETERAN SERVICES": "300",
    "CONTROL": "300",
    "MEETING ROOM": "300",
    "FACULTY SUPPORT / LOUNGE": "300",
    "LIBRARY": "400",
    "SPEECH & HEARING CTR": "500",
    "VITALE CENTER": "500",
    "ASSEMBLY": "600",
    "CAFE": "600",
    "FOOD SERVICE": "600",
    "RETAIL": "600",
    "GENERAL USE": "600",
    "STORAGE / CLOSETS": "700",
    "HEALTH CENTER": "800",
    "CIRCULATION/SUPPORT": "WWW",
    "BUILDING SERVICES": "XXX",
    "MECHANICAL": "YYY"
  }
};
