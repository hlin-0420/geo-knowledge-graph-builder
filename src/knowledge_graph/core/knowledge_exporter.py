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
                for query in cypher_commands.split(';'):
                    query = query.strip()
                    if query:
                        session.run(query)

    def extract_graph_data(self):
        with self.driver.session() as session:
            nodes = session.run("MATCH (n) RETURN labels(n) AS labels, properties(n) AS props")
            relationships = session.run("""
                MATCH (a)-[r]->(b)
                RETURN type(r) AS rel_type, properties(r) AS props,
                       labels(a) AS a_labels, properties(a) AS a_props,
                       labels(b) AS b_labels, properties(b) AS b_props
            """)

            node_list = [record.data() for record in nodes]
            rel_list = [record.data() for record in relationships]
            return node_list, rel_list

    def format_data_for_llm(self, node_list, rel_list):
        docs = []

        for node in node_list:
            label = ', '.join(node["labels"])
            props = ', '.join(f"{k}: {v}" for k, v in node["props"].items())
            docs.append(f"Node ({label}) with properties: {props}")

        for rel in rel_list:
            a_label = ', '.join(rel["a_labels"])
            b_label = ', '.join(rel["b_labels"])
            a_props = ', '.join(f"{k}: {v}" for k, v in rel["a_props"].items())
            b_props = ', '.join(f"{k}: {v}" for k, v in rel["b_props"].items())
            r_type = rel["rel_type"]
            r_props = ', '.join(f"{k}: {v}" for k, v in rel["props"].items())
            docs.append(
                f"Relationship ({r_type}) from ({a_label} - {a_props}) "
                f"to ({b_label} - {b_props}) with properties: {r_props}"
            )
        return docs

    def save_docs_to_file(self, docs, output_path="graph_knowledge.txt"):
        with open(output_path, 'w', encoding='utf-8') as f:
            for doc in docs:
                f.write(doc + "\n")


if __name__ == "__main__":
    # Configure Neo4j credentials from environment
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

    # Initialize loader
    loader = CurveGraphLoader(uri, user, password)

    # (Optional) Load graph structure and data
    loader.run_cypher_file("./cypher/graph_setup.cypher")
    loader.run_cypher_file("./cypher/unique_curves/nodes.cypher")
    loader.run_cypher_file("./cypher/unique_curves/relationships.cypher")

    # Extract and format knowledge
    nodes, relationships = loader.extract_graph_data()
    docs = loader.format_data_for_llm(nodes, relationships)
    loader.save_docs_to_file(docs, "./text_files/graph_knowledge.txt")

    loader.close()
    print("Graph loaded and knowledge exported for LLM.")
