// Create a vector index for the Type node based on the 'embedding' property
CREATE VECTOR INDEX type_vector_index 
FOR (t:Type) 
ON (t.embedding) 
OPTIONS { indexConfig: {
  `vector.dimensions`: 384,
  `vector.similarity_function`: 'cosine'
}};