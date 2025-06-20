"""
kg_schema.py
============

Utility helpers that *only* deal with reading Neo4j’s live schema and turning
it into something an LLM can consume.  No LangChain imports, no prompts, no
side-effects.
"""
from functools import lru_cache
from typing import Dict, List
from langchain_neo4j import Neo4jGraph


def _get_graph() -> Neo4jGraph:           # used only inside this module
    import os
    return Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
    )


@lru_cache(maxsize=1)
def schema_dict() -> Dict[str, Dict[str, List[str]]]:
    """
    Returns
        { 'System': { 'HAS_TOPIC': ['Concept', ...], ... }, ... }
    """
    graph = _get_graph()
    cypher = """
    CALL db.schema.visualization() YIELD relationships
    UNWIND relationships AS r
    RETURN r.startNodeName AS src, r.type AS rel, r.endNodeName AS dst
    """
    rows = graph.query(cypher)

    out: Dict[str, Dict[str, List[str]]] = {}
    for row in rows:
        out.setdefault(row["src"], {}).setdefault(row["rel"], []).append(row["dst"])

    # dedupe & sort for determinism
    for src in out:
        for rel in out[src]:
            out[src][rel] = sorted(set(out[src][rel]))
    return out


def schema_text() -> str:
    """LLM-friendly (#LABEL)-[:REL]->(LABEL) listing."""
    lines = ["# === Valid Neo4j Schema ==="]
    for src, rels in sorted(schema_dict().items()):
        for typ, dsts in sorted(rels.items()):
            for dst in dsts:
                lines.append(f"({src})-[:{typ}]->({dst})")
    return "\n".join(lines)