MATCH (g:Group)
WHERE g.name = "Gas Components"
DETACH DELETE g;