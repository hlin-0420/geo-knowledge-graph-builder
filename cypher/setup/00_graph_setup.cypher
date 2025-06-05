MERGE (:System {name: 'GEO File System'});

MERGE (:FileType {name: 'ODF', fullName: 'Output Database File'});
MERGE (:FileType {name: 'ODT', fullName: 'Template File'});
MERGE (:FileType {name: 'OIF', fullName: 'Interval File'});

MERGE (:Component {name: 'Library Info', details: 'headers, lithology, modifiers, symbols'});
MERGE (:Component {name: 'View File Content', details: 'track layout, depth, scale'});
MERGE (:Component {name: 'INI Settings', details: 'curve defaults, computed curves'});
MERGE (:Component {name: 'Document Tree', details: 'structure with warnings'});

MERGE (:Concept {name: 'Depth Interval Subset', description: 'e.g. 7000-8000ft segment of full ODF'});

MATCH (odf:FileType {name: 'ODF'}), (odt:FileType {name: 'ODT'})
MERGE (odf)-[:HAS_TEMPLATE]->(odt);

MATCH (odf:FileType {name: 'ODF'}), (oif:FileType {name: 'OIF'})
MERGE (odf)-[:CAN_BE_SEGMENTED_INTO]->(oif);

MATCH (odt:FileType {name: 'ODT'}), (odf:FileType {name: 'ODF'})
MERGE (odt)-[:CREATED_FROM]->(odf);

MATCH (oif:FileType {name: 'OIF'}), (odf:FileType {name: 'ODF'})
MERGE (oif)-[:EXTRACTED_FROM]->(odf);

MATCH (odt:FileType {name: 'ODT'}), (lib:Component {name: 'Library Info'})
MERGE (odt)-[:CONTAINS]->(lib);

MATCH (odt:FileType {name: 'ODT'}), (view:Component {name: 'View File Content'})
MERGE (odt)-[:CONTAINS]->(view);

MATCH (odt:FileType {name: 'ODT'}), (ini:Component {name: 'INI Settings'})
MERGE (odt)-[:CONTAINS]->(ini);

MATCH (odt:FileType {name: 'ODT'}), (tree:Component {name: 'Document Tree'})
MERGE (odt)-[:HAS_DOCUMENT_TREE]->(tree);

MATCH (oif:FileType {name: 'OIF'}), (subset:Concept {name: 'Depth Interval Subset'})
MERGE (oif)-[:REPRESENTS]->(subset);