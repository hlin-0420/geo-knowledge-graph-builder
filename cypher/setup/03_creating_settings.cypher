MERGE (curve:Curve {name: 'Curve'})
MERGE (curve_settings:Settings {name: 'Settings'})
MERGE (curve)-[:HAS_ATTRIBUTE]->(curve_settings);