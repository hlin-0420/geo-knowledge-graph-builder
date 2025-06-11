MERGE (geo:GEO {name:'GEO Help Guide'})
MERGE (curve:Curve {name: 'Curve'})
MERGE (geo)-[:HAS_TOPIC]->(curve);

MERGE (curve:Curve {name: 'Curve'})
MERGE (curve_settings:Settings {name: 'Settings'})
MERGE (curve)-[:HAS_ATTRIBUTE]->(curve_settings);