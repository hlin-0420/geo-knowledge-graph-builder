MERGE (:Type {
  name: 'ASCII',
  delimiter: 'Space',
  extension: '*.txt *.asc',
  comments: 'Mudlog data may occasionally come in this format.'
});

MERGE (:Type {
  name: 'ASCII',
  delimiter: 'Comma',
  extension: '*.csv *.txt',
  comments: 'Mudlog data or output from a spreadsheet'
});

MERGE (:Type {
  name: 'ASCII',
  delimiter: 'Tab',
  extension: '*.txt',
  comments: 'Mudlog data or output from a spreadsheet.'
});

MERGE (:Type {
  name: 'LAS',
  delimiter: '-',
  extension: '*.LAS',
  comments: 'Wireline data in a structured ASCII (CWLAS) format.'
});

MERGE (:Type {
  name: 'XML',
  delimiter: '-',
  extension: '*.XML',
  comments: 'In anticipation of the day when oilfield vendor data becomes available in eXtensible Mark-up Language [XML] format.'
});
