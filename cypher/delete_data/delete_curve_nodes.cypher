MATCH (c:Curve)
WHERE c.name IN ["Shale Zone Cutoff", "C1", "C2", "Gamma Ray Table Curve", "Manual Polyline"]
DETACH DELETE c;