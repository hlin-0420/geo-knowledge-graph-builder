from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Load credentials securely
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

# Load Cypher script
with open("./cypher/graph_setup.cypher", "r", encoding="utf-8") as f:
    cypher_script = f.read()

# Create driver
driver = GraphDatabase.driver(uri, auth=(user, password))

def setup_graph(tx, script):
    for statement in script.split(';'):
        stmt = statement.strip()
        if stmt:  # skip empty lines
            tx.run(stmt)

# Run transaction
with driver.session() as session:
    session.execute_write(setup_graph, cypher_script)

driver.close()