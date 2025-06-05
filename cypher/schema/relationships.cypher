// Curve created by operation
MATCH (c:Curve {name: "Shale Zone Cutoff"}), (o:Operation {name: "Create Cutoff Curve"})
CREATE (c)-[:CREATED_BY]->(o);

MATCH (c:Curve {name: "Gamma Ray Table Curve"}), (o:Operation {name: "Create Curve From Table Columns"})
CREATE (c)-[:CREATED_BY]->(o);

MATCH (c:Curve {name: "Manual Polyline"}), (o:Operation {name: "Create Polyline Curve"})
CREATE (c)-[:CREATED_BY]->(o);

MATCH (c:Curve {name: "C1"}), (o:Operation {name: "Create Multiple Curve Data"})
CREATE (c)-[:CREATED_BY]->(o);

MATCH (c:Curve {name: "C2"}), (o:Operation {name: "Create Multiple Curve Data"})
CREATE (c)-[:CREATED_BY]->(o);

// Curve group containment
MATCH (g:Group {name: "Gas Components"}), (c:Curve {name: "C1"})
CREATE (g)-[:CONTAINS]->(c);

MATCH (g:Group {name: "Gas Components"}), (c:Curve {name: "C2"})
CREATE (g)-[:CONTAINS]->(c);

// Group created by operation
MATCH (g:Group {name: "Gas Components"}), (o:Operation {name: "Create Multiple Curve Data"})
CREATE (g)-[:CREATED_BY]->(o);

// View and Edit relation
MATCH (g:Group {name: "Gas Components"}), (o:Operation {name: "View and Edit Curve Groups"})
CREATE (g)-[:VIEWED_BY]->(o);