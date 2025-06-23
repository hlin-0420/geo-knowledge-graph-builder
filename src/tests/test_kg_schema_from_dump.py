import json
from collections import defaultdict
from pathlib import Path

from ..qa_bot.core.kg_schema import schema_text

RECORDS = Path(__file__).parent.parent / "tests" / "records.json"   # tests/records.json

def _load_dump(path: Path) -> dict[str, dict[str, list[str]]]:
    """
    Convert the Neo4j Browser/APOC export JSON into the (src→rel→dsts) dict
    shape that kg_schema.schema_dict() expects.
    """
    with path.open(encoding="utf-8-sig") as fh:     # handles the BOM
        raw = json.load(fh)

    out: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))

    for rec in raw:
        src_label = rec["src"]["labels"][0]
        dst_label = rec["dst"]["labels"][0]
        rel_type  = rec["rel"]["type"]
        out[src_label][rel_type].add(dst_label)

    # turn inner sets into **sorted** lists so ordering is deterministic
    return {
        src: {rel: sorted(dsts) for rel, dsts in rels.items()}
        for src, rels in out.items()
    }

def test_schema_text_from_dump(monkeypatch):
    """
    GIVEN relationships exported from Neo4j (records.json)
    WHEN  schema_text() is executed
    THEN  each '(Src)-[:REL]->(Dst)' line in the output must be present, and
          the list must be sorted exactly like the implementation dictates.
    """
    # ① Build the stub directly from the JSON dump
    dump_dict = _load_dump(RECORDS)

    # ② Patch the dependency so no live DB is required
    monkeypatch.setattr(schema_text, "schema_dict", lambda: dump_dict)

    # ③ Expected output: header + one line per (src,rel,dst), sorted
    header = "# === Valid Neo4j Schema ==="
    expected_lines = [header]

    for src in sorted(dump_dict):
        for rel in sorted(dump_dict[src]):
            for dst in dump_dict[src][rel]:
                expected_lines.append(f"({src})-[:{rel}]->({dst})")

    expected_output = "\n".join(expected_lines)

    # ④ Act + Assert
    assert schema_text.schema_text() == expected_output