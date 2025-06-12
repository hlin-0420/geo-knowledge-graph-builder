MERGE (geo:GEO {name:'GEO Help Guide'})
MERGE (curve:Curve {name: 'Curve'})
MERGE (geo)-[:HAS_TOPIC]->(curve);

MERGE (curve:Curve {name: 'Curve'})
MERGE (curve_settings:Settings {name: 'Settings'})
MERGE (curve)-[:HAS_ATTRIBUTE]->(curve_settings);

MERGE (curve_settings:Settings {name: 'Settings'})
MERGE (scale:Scales {name: 'Scales'})
MERGE (curve_settings)-[:HAS_ATTRIBUTE]->(scale);

MERGE (scale:Scales {name: 'Scales'})
MERGE (linear_type: Linear_Type {name: 'Linear Type'})
MERGE (scale)-[:HAS_ATTRIBUTE]->(linear_type);

MERGE (scale:Scales {name: 'Scales'})
MERGE (log_type: Log_Type {name: 'Log Type'})
MERGE (scale)-[:HAS_ATTRIBUTE]->(log_type);

MERGE (scale:Scales {name: 'Scales'})
MERGE (left_track_edge_value: Left_Track_Edge_Value {name: 'Left Track Edge Value', type: 'Min', value: 0})
MERGE (scale)-[:HAS_ATTRIBUTE]->(left_track_edge_value);

MERGE (scale:Scales {name: 'Scales'})
MERGE (right_track_edge_value: Right_Track_Edge_Value {name: 'Right Track Edge Value', type: 'Min', value: 0})
MERGE (scale)-[:HAS_ATTRIBUTE]->(right_track_edge_value);