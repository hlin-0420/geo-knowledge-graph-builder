# GEO Knowledge Graph Builder

This project extracts structured knowledge from the GEO Help Guide HTML pages and converts it into a knowledge graph.

## Features

- Parse .htm files from GEO Help Guide
- GEO — an integrated PC-based well log authoring, analysis, and reporting system developed by Geologix for petroleum geologists, geoscientists, and engineers.
- Build and visualize the knowledge graph
- Export triples to Neo4j or RDF format

## Setup

```bash
git clone https://github.com/hlin-0420/geo-knowledge-graph-builder.git
cd geo-knowledge-graph-builder
pip install -r requirements.txt