MATCH (o:Operation)
WHERE o.name IN [
  "Create User-defined Curve",
  "Create Cutoff Curve",
  "Create Curve From Table Columns",
  "Create Polyline Curve",
  "Create Multiple Curve Data",
  "Edit Curve Data",
  "Mouse Set Curve Data",
  "Compile Curves",
  "View and Edit Curve Groups",
  "Generate Integrated Travel Time Pips"
]
DETACH DELETE o;