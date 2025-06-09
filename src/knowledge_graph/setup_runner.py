import os
from neo4j import GraphDatabase
from pathlib import Path

# Load environment variables (optional)
from dotenv import load_dotenv
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def run_cypher_file(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        raw_cypher = file.read()

    # Split by semicolon, but ignore empty/whitespace-only statements
    statements = [stmt.strip() for stmt in raw_cypher.split(";") if stmt.strip()]

    with driver.session() as session:
        print(f"🔁 Running: {filepath}")
        for i, statement in enumerate(statements, start=1):
            try:
                session.run(statement)
                print(f"  ✅ Statement {i} ran successfully.")
            except Exception as e:
                print(f"  ❌ Statement {i} failed:\n{statement}\nError: {e}")
        print(f"✅ Completed: {filepath}")

def main():
    cypher_scripts = [
        "cypher/schema/nodes.cypher",
        "cypher/schema/relationships.cypher",
        "cypher/data/curve_type.cypher",
        "cypher/setup/02_create_vector_index.cypher",
    ]

    for script_path in cypher_scripts:
        full_path = Path.cwd() / script_path  # ✅ Safe cross-platform join
        run_cypher_file(full_path)

if __name__ == "__main__":
    main()