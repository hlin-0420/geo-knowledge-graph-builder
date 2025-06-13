// Create a vector index for the Type node based on the 'embedding' property
CREATE VECTOR INDEX type_vector_index 
FOR (t:Type) 
ON (t.embedding) 
OPTIONS { indexConfig: {
  `vector.dimensions`: 384,
  `vector.similarity_function`: 'cosine'
}};

CREATE VECTOR INDEX filetype_vector_index
FOR (f:FileType)
ON (f.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 384,
    `vector.similarity_function`: 'cosine'
  }
};

CREATE INDEX filetype_name_index FOR (f:FileType) ON (f.name);
CREATE INDEX component_name_index FOR (c:Component) ON (c.name);
CREATE INDEX concept_name_index FOR (c:Concept) ON (c.name);
CREATE INDEX system_name_index FOR (s:System) ON (s.name);
CREATE INDEX curve_name_index FOR (c:Curve) ON (c.name);
