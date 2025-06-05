// Create or match central nodes
MERGE (curve:Curve {name: 'Curve'})
MERGE (type:Type {name: 'Type'})
MERGE (curve)-[:HAS_ATTRIBUTE]->(type)

// Define all formats and link to 'Type'
WITH type

MERGE (ascii_space:Format {
  name: 'ASCII - Space',
  delimiter: 'Space',
  extension: '*.txt *.asc',
  comments: 'Mudlog data may occasionally come in this format.'
})
MERGE (type)-[:HAS_FORMAT]->(ascii_space)

MERGE (ascii_comma:Format {
  name: 'ASCII - Comma',
  delimiter: 'Comma',
  extension: '*.csv *.txt',
  comments: 'Mudlog data or output from a spreadsheet'
})
MERGE (type)-[:HAS_FORMAT]->(ascii_comma)

MERGE (ascii_tab:Format {
  name: 'ASCII - Tab',
  delimiter: 'Tab',
  extension: '*.txt',
  comments: 'Mudlog data or output from a spreadsheet.'
})
MERGE (type)-[:HAS_FORMAT]->(ascii_tab)

MERGE (las:Format {
  name: 'LAS',
  delimiter: '-',
  extension: '*.LAS',
  comments: 'Wireline data in a structured ASCII (CWLAS) format.'
})
MERGE (type)-[:HAS_FORMAT]->(las)

MERGE (xml:Format {
  name: 'XML',
  delimiter: '-',
  extension: '*.XML',
  comments: 'In anticipation of the day when oilfield vendor data becomes available in XML format.'
})
MERGE (type)-[:HAS_FORMAT]->(xml)