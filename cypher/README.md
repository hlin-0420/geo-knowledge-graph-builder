# 📘 Cypher Scripts for GEO Knowledge Graph Builder

This directory contains Cypher scripts for setting up, populating, and maintaining the **GEO Knowledge Graph** using [Neo4j](https://neo4j.com/). The knowledge graph represents structured relationships from GEO's help documentation, including curve types, file types, and associated metadata.

---

## 📁 Directory Structure

```bash
cypher/
├── setup/
│   ├── 00_graph_setup.cypher       # Sets constraints, indexes, and database setup
│   └── 01_load_order.cypher        # Specifies the execution order for loading scripts
├── schema/
│   ├── nodes.cypher                # Defines node creation (e.g., Curve, FileType)
│   ├── relationships.cypher        # Establishes graph relationships between nodes
│   └── filetypes.cypher            # Adds file type nodes and their links
├── data/
│   └── curve_type.cypher           # Inserts specific curve type data as reference nodes
└── run_all.cypher                  # [Optional] Aggregates all scripts into one
```

## 🔄 Execution Order
To maintain data integrity and dependency logic, run the Cypher scripts in the following order:

setup/00_graph_setup.cypher — Sets up indexes and constraints.

setup/01_load_order.cypher — Ensures dependencies are respected in later stages.

schema/nodes.cypher — Creates core nodes.

schema/relationships.cypher — Links nodes with semantic relationships.

schema/filetypes.cypher — Adds filetype-specific nodes.

data/curve_type.cypher — Loads specific curve types as static metadata.

✅ You can automate this using run_all.cypher or a Python/CLI script.

## 🧱 Node & Relationship Types
Nodes
:Curve

:FileType

Custom types defined in curve_type.cypher

Relationships
:USES

:RELATED_TO

:HAS_TYPE

See individual .cypher files for details on properties and structure.

## 🛠️ Requirements
Neo4j Desktop or Server

cypher-shell for command-line execution (optional)

Recommended: Python script or Makefile to orchestrate execution

## ▶️ Running the Scripts (Manually)

```
cypher-shell -u neo4j -p password < setup/00_graph_setup.cypher
cypher-shell -u neo4j -p password < setup/01_load_order.cypher
cypher-shell -u neo4j -p password < schema/nodes.cypher
cypher-shell -u neo4j -p password < schema/relationships.cypher
cypher-shell -u neo4j -p password < schema/filetypes.cypher
cypher-shell -u neo4j -p password < data/curve_type.cypher
```

Or run them all via:
```
cypher-shell -u neo4j -p password < run_all.cypher
```

## 📌 Notes
All Cypher scripts are idempotent if designed with MERGE instead of CREATE.

If loading large datasets, consider wrapping writes in `CALL { ... } IN TRANSACTIONS`.

This repo assumes a clean or pre-configured Neo4j database.

## 🧩 Contribution
Feel free to add new data sources, relationships, or file formats. Submit a pull request with:

Script in the appropriate folder (`schema/`, `data/`, etc.)

Description of the change

Update to this README if structure changes

## 📞 Contact
Maintained by: Haocheng Lin
For inquiries: GitHub Issues

---

Let me know if you'd like this README adjusted for automated workflows (e.g., Python, Docker) or extended with sample Cypher queries to inspect the graph!