from neo4j import GraphDatabase
import os

class CurveGraphLoader:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()

    def run_cypher_file(self, filepath):
        with self.driver.session() as session:
            with open(filepath, 'r', encoding='utf-8') as f:
                cypher_commands = f.read()
                # Run individual queries split by semicolon
                for query in cypher_commands.split(';'):
                    query = query.strip()
                    if query:
                        session.run(query)

if __name__ == "__main__":
    # Configure connection details
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

    loader = CurveGraphLoader(uri, user, password)
    
    # Run setup
    loader.run_cypher_file("./cypher/graph_setup.cypher")
    
    # Load data
    loader.run_cypher_file("./cypher/unique_curves/nodes.cypher")
    loader.run_cypher_file("./cypher/unique_curves/relationships.cypher")

    loader.close()
    print("Graph loaded successfully.")
